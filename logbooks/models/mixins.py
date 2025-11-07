from io import BytesIO
from functools import cached_property
import urllib
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtailautocomplete.edit_handlers import AutocompletePanel
from commonknowledge.django.images import generate_imagegrid_filename, render_image_grid
from commonknowledge.geo import get_coordinates_data, static_map_marker_image_url
from commonknowledge.wagtail.models import ChildListMixin
from logbooks.tasks import regenerate_page_thumbnails
from logbooks.thumbnail import get_thumbnail_opts
from logbooks.models.snippets import AtlasTag
from logbooks.models.serializers import (
    PageCoordinatesSerializer,
    UserSerializer,
)
from logbooks.models.blocks import ArticleContentStream
from logbooks.models.fields import TagFieldPanel, LocalizedTaggableManager
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.parsers.plaintext import PlaintextParser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.response import TemplateResponse
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api.conf import APIField
from wagtail.models import Page, Revision, Locale
from wagtail.images.models import Image
from wagtail.fields import RichTextField
from wagtail_localize.fields import SynchronizedField
from django.contrib.gis.db import models as geo
from commonknowledge.wagtail.search.models import IndexedStreamfieldMixin
from mapwidgets.widgets import MapboxPointFieldWidget
from smartforests.models import CmsImage, Tag, User
from smartforests.tag_cloud import get_nodes_and_links
from smartforests.util import ensure_list, group_by_tag_name
from modelcluster.fields import ParentalManyToManyField
from wagtailseo.models import SeoType, TwitterCard
from treebeard.mp_tree import get_result_class
import requests
from django.core.files.images import ImageFile
from smartforests.mixins import SeoMetadataMixin
from django.http import HttpResponseRedirect


class BaseLogbooksPage(Page):
    """
    Common utilities for pages in this module
    """

    class Meta:
        abstract = True

    icon_class = None
    show_title = False

    @classmethod
    def for_tag(cls, tag_or_tags, locale=None):
        """
        Return all live pages matching the tag
        """
        qs = cls.objects.filter(tagged_items__tag__in=ensure_list(tag_or_tags)).live()
        if locale is not None:
            qs = qs.filter(locale=locale)
        return qs.distinct()

    @classmethod
    def model_info(cls):
        """'
        Expose the meta attr to templates
        """
        return cls._meta

    @classmethod
    def label(self):
        return self._meta.verbose_name

    @property
    def page_type(self):
        return self._meta.verbose_name

    @property
    def citation_intro(self):
        """
        Added so that the citation itself can be left
        untranslated, while the sentence as a whole
        is translated.
        """
        return _("To cite this page: ")

    @property
    def link_url(self):
        """
        Wrapper for url allowing us to link to a page embedded in a parent (as with logbook entries) without
        overriding any wagtail internals

        """

        return self.url

    @property
    def top_level_category(self):
        """
        Return the index page that is the top-level parent for
        the current page.
        """

        # Start with the current page
        category_page = self

        # Go up the page tree, stopping when there is no parent
        parent = category_page.get_parent()
        while parent:
            parent_is_home_or_root = parent.depth <= 2

            # If the parent is the home page, stop going up the tree
            # as the current page must be the top level category
            if parent_is_home_or_root:
                break

            # If the parent is not the home or root page, it could
            # be the top level category page, so continue going up
            # the tree
            category_page = parent
            parent = category_page.get_parent()

        return category_page

    @cached_property
    def original_published_at(self):
        return (
            type(self)
            .objects.filter(translation_key=self.translation_key)
            .order_by("first_published_at")
            .values_list("first_published_at", flat=True)
            .first()
        )


class ContributorMixin(BaseLogbooksPage):
    """
    Common configuration for pages that want to track their contributors.
    """

    class Meta:
        abstract = True

    additional_contributors = ParentalManyToManyField(
        User,
        blank=True,
        help_text="Contributors who have not directly edited this page",
    )

    excluded_contributors = ParentalManyToManyField(
        User,
        blank=True,
        related_name="+",
        help_text="Contributors who should be hidden from public citation",
    )

    # Materialised list of contributors
    # No longer used due to preview bugs
    contributors = ParentalManyToManyField(
        User, blank=True, related_name="+", help_text="Index list of contributors"
    )

    override_translatable_fields = [
        SynchronizedField("additional_contributors"),
        SynchronizedField("excluded_contributors"),
    ]

    def get_page_revision_editors(self):
        content_type = ContentType.objects.get_for_model(self)

        return set(
            [self.owner]
            + [
                user
                for user in [
                    revision.user
                    for revision in Revision.objects.filter(
                        object_id=self.id, content_type=content_type
                    ).select_related("user")
                ]
                if user is not None
            ]
        )

    @property
    def real_contributors(self):
        return self.get_real_contributors()

    @property
    def draft_contributors(self):
        return self.get_real_contributors(preview=True)

    def get_real_contributors(self, preview=False):
        contributors = set(self.get_page_contributors())

        # Add page tree's contributors
        descendents = Page.objects.type(ContributorMixin).descendant_of(self, inclusive=False).specific()
        if not preview:
            descendents = descendents.live()

        for page in descendents:
            if preview:
                page = page.get_latest_revision_as_object()
            contributors.update(page.get_page_contributors())

        for excluded in self.excluded_contributors.all():
            if excluded in contributors:
                contributors.remove(excluded)

        return [c for c in contributors if c.username not in ["common-knowledge", "hello@commonknowledge.coop"]]

    def get_page_contributors(self):
        return list(
            set(
                list(self.get_page_revision_editors())
                + list(self.additional_contributors.all())
            )
            - set(self.excluded_contributors.all())
        )

    api_fields = [
        APIField("contributors", serializer=UserSerializer(many=True)),
    ]

    content_panels = [
        AutocompletePanel("additional_contributors"),
        AutocompletePanel("excluded_contributors"),
    ]


class GeocodedMixin(BaseLogbooksPage):
    """
    Common configuration for pages that want to track a geographical location.
    """

    class Meta:
        abstract = True
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    geographical_location = models.CharField(max_length=250, null=True, blank=True)
    coordinates = geo.PointField(null=True, blank=True)
    map_image = models.ForeignKey(
        CmsImage, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    @property
    def longitude(self):
        if self.coordinates:
            return self.coordinates.coords[0]

    @property
    def latitude(self):
        if self.coordinates:
            return self.coordinates.coords[1]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For comparison purposes
        self.__previous_coordinates = self.coordinates

    @property
    def has_coordinates(self):
        return self.latitude is not None

    def save(self, *args, **kwargs):
        try:
            coordinates_changed = self.__previous_coordinates != self.coordinates
            if self.has_coordinates is True and self.geographical_location is None:
                self.update_location_name()
            if self.has_coordinates is True and (
                self.map_image is None or coordinates_changed
            ):
                self.update_map_thumbnail()
        except:
            pass
        super().save(*args, **kwargs)

    def update_location_name(self):
        if self.coordinates is not None:
            location_data = get_coordinates_data(
                self.coordinates, zoom=5, username="jennifer@planetarypraxis.org"
            )
            self.geographical_location = location_data.get("display_name", None)

    def update_map_thumbnail(self):
        if self.coordinates is None:
            return
        url = self.static_map_marker_image_url()
        if url is None:
            return
        response = requests.get(url)
        if response.status_code != 200:
            print("Map generator error:", url)
            print(response.status_code, response.content)
            return
        image = ImageFile(BytesIO(response.content), name=f"map-{self.pk}.png")

        if self.map_image is not None:
            self.map_image.delete()

        self.map_image = CmsImage(
            alt_text=f"Map of {self.geographical_location}",
            title=f"Generated map thumbnail for {self._meta.model_name} {self.slug}",
            file=image,
        )
        self.map_image.save()

    def static_map_marker_image_url(self) -> str:
        return static_map_marker_image_url(
            self.coordinates,
            access_token=settings.MAPBOX_API_PUBLIC_TOKEN,
            marker_url=self.map_marker,
            username="smartforests",
            style_id="ckziehr6u001e14ohgl2brzlu",
            width=300,
            height=200,
            zoom=5,
        )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("geographical_location"),
                FieldPanel("coordinates", widget=MapboxPointFieldWidget),
            ],
            heading="Geographical data",
        )
    ]

    api_fields = [
        APIField("label"),
        APIField("geographical_location"),
        APIField("coordinates", serializer=PageCoordinatesSerializer),
    ]


class ThumbnailMixin(BaseLogbooksPage):
    """
    Common configuration for pages that want to generate a thumbnail image derived from a subclass-defined list of images.
    """

    class Meta:
        abstract = True

    seo_image_sources = [
        "og_image",
        "most_recent_image",
        # TODO: use `thumbnail_image`, requires migration to CmsImage
        "default_seo_image",
    ]

    thumbnail_image = models.ForeignKey(CmsImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    @property
    def thumbnail_image_resilient(self):
        if self.thumbnail_image:
            return self.thumbnail_image.get_rendition("fill-400x240")
        if hasattr(self, "image") and self.image:
            return self.image.get_rendition("fill-400x240")
        if self.most_recent_image:
            return self.most_recent_image.get_rendition("fill-400x240")
        else:
            return self.default_seo_image.get_rendition("fill-400x240")

    @property
    def thumbnail_image_placeholder(self):
        if self.thumbnail_image:
            return self.thumbnail_image.get_rendition("fill-10x6")
        if hasattr(self, "image") and self.image:
            return self.image.get_rendition("fill-10x6")
        if self.most_recent_image:
            return self.most_recent_image.get_rendition("fill-10x6")
        else:
            return self.default_seo_image.get_rendition("fill-10x6")

    def get_thumbnail_images(self):
        return []

    @property
    def most_recent_image(self):
        images = self.get_thumbnail_images()
        if len(images) > 0:
            return images[0]
        return None

    def regenerate_thumbnail(self, force=False):
        images = [
            img.get_rendition("width-400").file for img in self.get_thumbnail_images()
        ]

        print(f"Regenerating thumbnail for {self.slug}: images {images}")

        if len(images) == 0:
            return

        if len(images) == 1:
            return

        imagegrid_opts = get_thumbnail_opts(images)

        print(f"Regenerating thumbnail for {self.slug}: opts {imagegrid_opts}")

        if imagegrid_opts is None:
            self.thumbnail_image.name = None
            return

        filename = generate_imagegrid_filename(
            prefix="page_thumbs", slug=self.slug, **imagegrid_opts
        )

        print(f"Regenerating thumbnail for {self.slug}: filename {filename}")

        if default_storage.exists(filename):
            if not force:
                print(
                    f"Regenerating thumbnail for {self.slug}: filename {filename} exists, skipping regen"
                )
                self.thumbnail_image.name = filename
                return
            else:
                print(
                    f"Regenerating thumbnail for {self.slug}: "
                    f"filename {filename} exists but regen is forced"
                )

        grid = render_image_grid(filename=filename, **imagegrid_opts)
        self.thumbnail_image = CmsImage(
            alt_text=f"{self.title} thumbnail",
            title=f"{self.title} thumbnail",
            file=grid
        )
        self.thumbnail_image.save()
        print(f"Regenerating thumbnail for {self.slug}: created {self.thumbnail_image}")

    card_content_html = "logbooks/thumbnails/basic_thumbnail.html"
    alternate_card_content_html = "logbooks/thumbnails/story_page_thumbnail.html"

    def save(self, *args, regenerate_thumbnails=True, **kwargs):
        if regenerate_thumbnails:
            page = self
            while isinstance(page, ThumbnailMixin):
                regenerate_page_thumbnails(page.id)
                try:
                    page = page.get_parent().specific
                except Page.DoesNotExist:
                    break

        return super().save(*args, **kwargs)


class SidebarRenderableMixin(BaseLogbooksPage):
    class Meta:
        abstract = True

    def get_sidebar_frame_response(self, request, *args, **kwargs):
        """
        Render the sidebar frame's html.
        """

        context = self.get_context(request)
        if "Turbo-Frame" in request.headers:
            return TemplateResponse(
                request, "logbooks/content_entry/sidepanel.html", context
            )
        elif "page" in context:
            return HttpResponseRedirect(context["page"].url)


class IndexPage(ChildListMixin, SeoMetadataMixin, BaseLogbooksPage):
    """
    Common configuration for index pages for logbooks, stories and radio episodes.
    """

    class Meta:
        abstract = True

    is_index_page = True
    allow_search = True
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ["home.HomePage"]
    seo_twitter_card = TwitterCard.SUMMARY

    if not settings.DEBUG:
        max_count = 1

    def get_filters(self, request):
        filter = {}

        tag_filter = request.GET.get("filter", None)
        if tag_filter is not None:
            try:
                tag_ids = Tag.get_translated_tag_ids(slug=tag_filter)
                filter["tagged_items__tag_id__in"] = tag_ids
            except Tag.DoesNotExist:
                pass

        return filter

    def relevant_tags(self):
        children = self.get_child_list_queryset(request=None)

        tags = Tag.objects.filter(
            logbooks_atlastag_items__content_object__live=True,
            logbooks_atlastag_items__content_object__in=children,
        ).distinct()

        return group_by_tag_name(tags)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["tag_filter"] = request.GET.get("filter", None)

        return context


class ArticleSeoMixin(SeoMetadataMixin):
    class Meta:
        abstract = True

    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE


class ArticlePage(
    IndexedStreamfieldMixin,
    ContributorMixin,
    ThumbnailMixin,
    GeocodedMixin,
    SidebarRenderableMixin,
    ArticleSeoMixin,
    BaseLogbooksPage,
):
    """
    Common configuration for logbook entries, stories and radio episodes.
    """

    class Meta:
        abstract = True

    tags = LocalizedTaggableManager(through=AtlasTag, blank=True)
    body = ArticleContentStream()
    endnotes = RichTextField(blank=True)
    citation = models.TextField(blank=True)
    show_title = True

    additional_content_panels = (
        [
            TagFieldPanel("tags"),
            FieldPanel("body"),
            FieldPanel("endnotes"),
            FieldPanel("citation"),
            InlinePanel("footnotes", label="Footnotes"),
        ]
        + ContributorMixin.content_panels
        + GeocodedMixin.content_panels
    )

    content_panels = Page.content_panels + additional_content_panels
    settings_panels = [FieldPanel("first_published_at")] + Page.settings_panels

    api_fields = (
        [
            APIField("last_published_at"),
            APIField("tags"),
            APIField("icon_class"),
            APIField("body"),
        ]
        + ContributorMixin.api_fields
        + GeocodedMixin.api_fields
    )

    search_fields = IndexedStreamfieldMixin.search_fields + Page.search_fields
    streamfield_indexer = ArticleContentStream.text_indexer

    override_translatable_fields = ContributorMixin.override_translatable_fields + [
        SynchronizedField("citation"),
    ]

    def body_images(self):
        """
        Return all the images in this page's body stream.
        """

        return tuple(
            block.value.get("image")
            for block in self.body
            if block.block_type == "image" and block.value.get("image")
        )

    seo_image_sources = ["og_image", "cover_image", "default_seo_image"]

    @property
    def cover_image(self):
        """
        Returns the first image in the body stream (or None if there aren't any).

        Used to determine which image to contribute to a thumbnail when images from multiple pages are combined into a single thumbnail (as with logbooks)
        """

        images = self.body_images()
        return None if len(images) == 0 else images[0]

    def get_thumbnail_images(self):
        return [image for image in self.body_images()]

    seo_description_sources = SeoMetadataMixin.seo_description_sources + [
        "preview_text"
    ]

    @property
    def preview_text(self):
        language = "english"

        parser = PlaintextParser.from_string(
            self.indexed_streamfield_text, Tokenizer(language)
        )
        stemmer = Stemmer(language)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        summary = " ".join(
            str(x) for x in summarizer(parser.document, 2) if str(x).strip() != ""
        )

        if summary:
            return summary
        else:
            return self.indexed_streamfield_text

    @property
    def tag_cloud(self):
        return get_nodes_and_links(self.all_localized_tags)

    @property
    def all_localized_tags(self):
        locale = Locale.get_active()
        translation_keys = self.tags.all().values_list("translation_key", flat=True)
        tags = Tag.objects.filter(locale=locale, translation_key__in=translation_keys)
        return list(sorted(tags, key=lambda tag: tag.name))

    @property
    def draft_localized_tags(self):
        return self.all_localized_tags()
