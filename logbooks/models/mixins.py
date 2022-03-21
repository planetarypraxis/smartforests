from io import BytesIO
from os import access
import urllib
from urllib.parse import urlencode, urlparse, urlunparse
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.fields import CharField
from wagtailautocomplete.edit_handlers import AutocompletePanel
from commonknowledge.django.cache import django_cached_model
from commonknowledge.django.images import generate_imagegrid_filename, render_image_grid
from commonknowledge.geo import get_coordinates_data, static_map_marker_image_url
from commonknowledge.wagtail.models import ChildListMixin
from django.db.models.query_utils import subclasses
from logbooks.models.tag_cloud import TagCloud
from logbooks.tasks import regenerate_page_thumbnails
from logbooks.thumbnail import get_thumbnail_opts
from logbooks.models.snippets import AtlasTag
from logbooks.models.serializers import PageCoordinatesSerializer, UserSerializer
from logbooks.models.blocks import ArticleContentStream
from turbo_response import TurboFrame
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words
from sumy.nlp.stemmers import Stemmer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.parsers.plaintext import PlaintextParser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http.response import HttpResponseNotFound
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.api.conf import APIField
from wagtail.core.models import Page, PageManager, PageRevision
from django.contrib.gis.db import models as geo
from commonknowledge.wagtail.search.models import IndexedStreamfieldMixin
from mapwidgets.widgets import MapboxPointFieldWidget
from smartforests.models import CmsImage, Tag, User
from smartforests.util import group_by_title
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.snippets.models import register_snippet
from wagtailseo.models import SeoMixin, SeoType, TwitterCard
from wagtail.core.rich_text import get_text_for_indexing
import requests
from django.core.files.images import ImageFile


class BaseLogbooksPage(Page):
    '''
    Common utilities for pages in this module
    '''

    class Meta:
        abstract = True

    icon_class = None
    show_title = False

    @classmethod
    def for_tag(cls, tag):
        '''
        Return all live pages matching the tag
        '''
        return cls.objects.filter(
            tagged_items__tag=tag
        ).live()

    @classmethod
    def model_info(cls):
        ''''
        Expose the meta attr to templates
        '''
        return cls._meta

    @classmethod
    def label(self):
        return self._meta.verbose_name

    @property
    def link_url(self):
        '''
        Wrapper for url allowing us to link to a page embedded in a parent (as with logbook entries) without
        overriding any wagtail internals

        '''

        return self.url

    @property
    def top_level_category(self):
        parent = self.get_parent().specific
        if parent is not None and isinstance(parent, BaseLogbooksPage):
            return parent.top_level_category

        return self


class ContributorMixin(BaseLogbooksPage):
    '''
    Common configuration for pages that want to track their contributors.
    '''

    class Meta:
        abstract = True

    additional_contributing_users = ParentalManyToManyField(
        User,
        blank=True,
        help_text="Contributors who have not directly edited this page"
    )

    additional_contributing_people = ParentalManyToManyField(
        'logbooks.Person',
        blank=True,
        help_text="Contributors who are not users of the Atlas"
    )

    excluded_contributors = ParentalManyToManyField(
        User,
        blank=True,
        related_name='+',
        help_text="Contributors who should be hidden from public citation"
    )

    def get_contributors(self):
        p = self
        return list(
            set(
                [p.owner] + [
                    user
                    for user in [
                        revision.user
                        for revision in PageRevision.objects.filter(page=p).select_related('user')
                    ]
                    if user is not None
                ] + list(
                    p.additional_contributing_users.all()
                ) + list(
                    p.additional_contributing_people.all()
                )
            ) - set(self.excluded_contributors.all())
        )

    @property
    def contributors(self):
        '''
        Return all the people who have contributed to this page and its subpages
        '''
        pages = Page.objects.type(
            ContributorMixin).descendant_of(self, inclusive=True).specific()
        contributors = []

        for page in pages:
            contributors += page.get_contributors()

        return list(set(contributors) - set(self.excluded_contributors.all()))

    api_fields = [
        APIField('contributors', serializer=UserSerializer(many=True)),
    ]

    content_panels = [
        AutocompletePanel('additional_contributing_users'),
        AutocompletePanel('additional_contributing_people'),
        AutocompletePanel('excluded_contributors'),
    ]


@register_snippet
class Person(models.Model):
    class Meta:
        verbose_name_plural = 'People'

    '''
    Non-users who are manually tagged as contributors
    '''
    name = CharField(max_length=500)
    contributor_page = ParentalKey(
        'logbooks.ContributorPage', null=True, blank=True)

    autocomplete_search_field = 'name'

    @classmethod
    def autocomplete_create(kls: type, value: str):
        return kls.objects.create(name=value)

    def __str__(self) -> str:
        return self.name

    def autocomplete_label(self):
        return str(self)

    def edited_content_pages(self):
        from logbooks.models.pages import LogbookPage
        return set([
            page
            for page in
            LogbookPage.objects.filter(
                additional_contributing_people=self).specific()
        ])

    def edited_tags(self):
        from smartforests.models import Tag
        return Tag.objects.filter(logbooks_atlastag_items__content_object__in=self.edited_content_pages())


class GeocodedMixin(BaseLogbooksPage):
    '''
    Common configuration for pages that want to track a geographical location.
    '''

    class Meta:
        abstract = True
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    geographical_location = models.CharField(
        max_length=250, null=True, blank=True)
    coordinates = geo.PointField(null=True, blank=True)
    map_image = models.ForeignKey(
        CmsImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

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

    def save(self, *args, **kwargs):
        coordinates_changed = self.__previous_coordinates != self.coordinates
        if self.geographical_location is None or coordinates_changed:
            self.update_location_name()
        if self.map_image is None or coordinates_changed:
            self.update_map_thumbnail()
        super().save(*args, **kwargs)

    def update_location_name(self):
        if self.coordinates is not None:
            location_data = get_coordinates_data(
                self.coordinates,
                zoom=11,
                username='jennifer@planetarypraxis.org'
            )
            self.geographical_location = location_data.get(
                'display_name', None)

    def update_map_thumbnail(self):
        if self.coordinates is None:
            return
        url = self.static_map_marker_image_url()
        if url is None:
            return
        response = requests.get(url)
        image = ImageFile(BytesIO(response.content),
                          name=f'{urllib.parse.quote(url)}.png')

        if self.map_image is not None:
            self.map_image.delete()

        self.map_image = CmsImage(
            alt_text=f"Map of {self.geographical_location}",
            title=f'Generated map thumbnail for {self._meta.model_name} {self.slug}',
            file=image
        )
        self.map_image.save()

    def static_map_marker_image_url(self) -> str:
        return static_map_marker_image_url(
            self.coordinates,
            access_token=settings.MAPBOX_API_PUBLIC_TOKEN,
            marker_url=self.map_marker,
            username='smartforests',
            style_id='ckziehr6u001e14ohgl2brzlu',
            width=300,
            height=200,
        )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('geographical_location'),
                FieldPanel('coordinates', widget=MapboxPointFieldWidget)
            ],
            heading="Geographical data",
        )
    ]

    api_fields = [
        APIField('label'),
        APIField('geographical_location'),
        APIField('coordinates', serializer=PageCoordinatesSerializer)
    ]


class SeoMetadataMixin(SeoMixin, Page):
    class Meta:
        abstract = True

    promote_panels = SeoMixin.seo_panels

    seo_image_sources = [
        "og_image"  # Explicit sharing image
    ]

    seo_description_sources = [
        "search_description",  # Explicit sharing description
    ]

    @property
    def seo_description(self) -> str:
        """
        Middleware for seo_description_sources
        """
        for attr in self.seo_description_sources:
            if hasattr(self, attr):
                text = getattr(self, attr)
                if text:
                    # Strip HTML if there is any
                    return get_text_for_indexing(text)
        return ""


class ThumbnailMixin(BaseLogbooksPage):
    '''
    Common configuration for pages that want to generate a thumbnail image derived from a subclass-defined list of images.
    '''

    class Meta:
        abstract = True

    seo_image_sources = SeoMetadataMixin.seo_image_sources + [
        "most_recent_image"
        # TODO: use `thumbnail_image`, requires migration to CmsImage
    ]

    thumbnail_image = models.ImageField(null=True, blank=True)

    def get_thumbnail_images(self):
        return []

    @property
    def most_recent_image(self):
        images = self.get_thumbnail_images()
        if len(images) > 0:
            return images[0]
        return None

    def regenerate_thumbnail(self):
        images = [img.file for img in self.get_thumbnail_images()]
        imagegrid_opts = get_thumbnail_opts(images)

        if imagegrid_opts is None:
            self.thumbnail_image.name = None
            return

        filename = generate_imagegrid_filename(
            prefix='page_thumbs', slug=self.slug, **imagegrid_opts)

        if default_storage.exists(filename):
            self.thumbnail_image.name = filename
            return

        self.thumbnail_image = render_image_grid(
            filename=filename,
            **imagegrid_opts
        )

    card_content_html = 'logbooks/thumbnails/basic_thumbnail.html'

    def save(self, *args, regenerate_thumbnails=True, **kwargs):
        if regenerate_thumbnails:

            page = self
            while isinstance(page, ThumbnailMixin):
                regenerate_page_thumbnails(page.id)
                page = page.get_parent().specific

        return super().save(*args, **kwargs)


class SidebarRenderableMixin(BaseLogbooksPage):
    class Meta:
        abstract = True

    def get_sidebar_frame_response(self, request, *args, **kwargs):
        '''
        Render the sidebar frame's html.
        '''

        context = self.get_context(request)
        return TemplateResponse(request, 'logbooks/content_entry/sidepanel.html', context)


class IndexPage(ChildListMixin, SeoMetadataMixin, BaseLogbooksPage):
    '''
    Common configuration for index pages for logbooks, stories and radio episodes.
    '''
    class Meta:
        abstract = True

    is_index_page = True
    allow_search = True
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ['home.HomePage']
    seo_twitter_card = TwitterCard.SUMMARY

    if not settings.DEBUG:
        max_count = 1

    def get_filters(self, request):
        filter = {}

        tag_filter = request.GET.get('filter', None)
        if tag_filter is not None:
            try:
                tag = Tag.objects.get(slug=tag_filter)
                filter['tagged_items__tag_id'] = tag.id
            except Tag.DoesNotExist:
                pass

        return filter

    def relevant_tags(self):
        children = self.get_child_list_queryset(request=None)

        tags = Tag.objects.filter(
            logbooks_atlastag_items__content_object__live=True,
            logbooks_atlastag_items__content_object__in=children
        ).distinct()

        return group_by_title(tags, key='name')

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['tag_filter'] = request.GET.get('filter', None)

        return context


class ArticleSeoMixin(SeoMetadataMixin):
    class Meta:
        abstract = True

    seo_content_type = SeoType.ARTICLE
    seo_twitter_card = TwitterCard.LARGE


class ArticlePage(IndexedStreamfieldMixin, ContributorMixin, ThumbnailMixin, GeocodedMixin, SidebarRenderableMixin, ArticleSeoMixin, BaseLogbooksPage):
    '''
    Common configuration for logbook entries, stories and radio episodes.
    '''
    class Meta:
        abstract = True

    tags = ClusterTaggableManager(through=AtlasTag, blank=True)
    body = ArticleContentStream()
    show_title = True

    additional_content_panels = [
        FieldPanel('tags'),
        StreamFieldPanel('body'),
        InlinePanel("footnotes", label="Footnotes"),
    ] + ContributorMixin.content_panels + GeocodedMixin.content_panels

    content_panels = Page.content_panels + additional_content_panels

    api_fields = [
        APIField('tags'),
        APIField('icon_class'),
    ] + ContributorMixin.api_fields + GeocodedMixin.api_fields

    search_fields = IndexedStreamfieldMixin.search_fields + Page.search_fields
    streamfield_indexer = ArticleContentStream.text_indexer

    def body_images(self):
        '''
        Return all the images in this page's body stream.
        '''

        return tuple(
            block.value.get('image')
            for block in self.body
            if block.block_type == 'image'
            and block.value.get('image')
        )

    seo_image_sources = SeoMetadataMixin.seo_image_sources + [
        "cover_image"
    ]

    @property
    def cover_image(self):
        '''
        Returns the first image in the body stream (or None if there aren't any).

        Used to determine which image to contribute to a thumbnail when images from multiple pages are combined into a single thumbnail (as with logbooks)
        '''

        images = self.body_images()
        return None if len(images) == 0 else images[0]

    def get_thumbnail_images(self):
        return self.body_images()

    seo_description_sources = SeoMetadataMixin.seo_description_sources + [
        'preview_text'
    ]

    @property
    def preview_text(self):
        language = 'english'

        parser = PlaintextParser.from_string(
            self.indexed_streamfield_text, Tokenizer(language))
        stemmer = Stemmer(language)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        summary = ' '.join(
            str(x)
            for x in summarizer(parser.document, 2)
            if str(x).strip() != ''
        )

        if summary:
            return summary
        else:
            return self.indexed_streamfield_text

    @property
    def tag_cloud(self):
        return TagCloud.get_related(self.tags.all())

    @property
    def all_tags(self):
        return list(self.tags.all())
