from django.db import models
from django.conf import settings
from django.db.models import Q, Subquery, OuterRef
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from django.forms.widgets import SelectMultiple
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.forms.tags import TagField
from wagtail.models import Page
from smartforests.models import Tag, User
from smartforests.util import ensure_list
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultipleChooserPanel,
    TitleFieldPanel,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField
from wagtail.models import Locale, Orderable
from wagtailmedia.edit_handlers import MediaChooserPanel
from commonknowledge.wagtail.models import ChildListMixin
from django.template.defaultfilters import slugify
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from smartforests.mixins import SeoMixin
from smartforests.util import (
    flatten_list,
    group_by_tag_name,
    static_file_absolute_url,
)
from smartforests import wagtail_settings
from logbooks.models.fields import TagFieldPanel, LocalizedTaggableManager
from logbooks.models.mixins import (
    ArticlePage,
    ArticleSeoMixin,
    BaseLogbooksPage,
    ContributorMixin,
    GeocodedMixin,
    IndexPage,
    ThumbnailMixin,
    SidebarRenderableMixin,
)
from logbooks.models.snippets import AtlasTag
from smartforests.models import CmsImage
from django.shortcuts import redirect
from wagtailautocomplete.edit_handlers import AutocompletePanel
from smartforests.utils.api import APIRichTextField
from smartforests.mixins import SeoMetadataMixin
from smartforests.tag_cloud import get_nodes_and_links


class StoryPage(ArticlePage, ThumbnailMixin):
    """
    Stories are longer, self-contained articles.
    """

    class Meta:
        verbose_name = _("Story")
        verbose_name_plural = _("Stories")

    icon_class = "icon-stories"

    extract = RichTextField(blank=True)
    image = ForeignKey(CmsImage, on_delete=models.SET_NULL, null=True, blank=True)

    show_in_menus_default = True
    parent_page_types = ["logbooks.StoryIndexPage"]

    content_panels = ArticlePage.content_panels + [
        FieldPanel("image"),
        FieldPanel("extract"),
    ]

    api_fields = ArticlePage.api_fields + [
        APIField("image"),
        APIField("extract"),
    ]

    @property
    def cover_image(self):
        return self.image

    @property
    def citation_intro(self):
        return _("To cite this story: ")

    def get_first_image_from_body(self):
        images = self.body_images()
        if len(images) > 0:
            return images[0]
        return None

    def get_thumbnail_images(self):
        if self.cover_image is not None:
            return [self.cover_image]
        image = self.get_first_image_from_body()
        if image is not None:
            return [image]
        else:
            return []

    def get_tags(self):
        return self.tags.all()


class StoryIndexPage(Page):
    """
    Collection of stories.
    """

    parent_page_types = ["home.HomePage"]

    class Meta:
        verbose_name = "Stories Index Page"

    def get_context(self, request):
        context = super().get_context(request)

        child_qs = self.get_children().live().specific()

        # Subquery to get all the translations of each page, ordered by publish date
        translations = StoryPage.objects.filter(
            translation_key=OuterRef("translation_key")
        ).order_by("first_published_at")

        # Annotate with the earliest publish date in the subquery
        # This will be the publish date of the original version of the page
        child_qs = child_qs.annotate(
            original_published_at=Subquery(
                translations.values("first_published_at")[:1]
            )
        ).order_by("-original_published_at")

        context["child_list_page"] = child_qs
        return context


class EpisodePage(ArticlePage):
    """
    Episodes are individual items for the radio.
    """

    class Meta:
        verbose_name = _("Radio Episode")
        verbose_name_plural = _("Radio Episodes")

    show_in_menus_default = True
    parent_page_types = ["logbooks.RadioIndexPage"]
    icon_class = "icon-radio"

    promote_panels = [FieldPanel("featured")] + SeoMixin.seo_panels

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/N0g8oFn.png"
        else:
            return static_file_absolute_url("img/mapicons/radio.png")

    image = ForeignKey(CmsImage, on_delete=models.SET_NULL, null=True, blank=True)

    thumbnail = ForeignKey(
        CmsImage,
        related_name="episode_thumbnail",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    api_fields = ArticlePage.api_fields + [
        APIField("image"),
        APIField("thumbnail", serializer=ImageRenditionField("fill-100x100")),
    ]

    audio = models.ForeignKey(
        "wagtailmedia.Media",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = (
        Page.content_panels
        + [
            MediaChooserPanel("audio", media_type="audio"),
            FieldPanel("image"),
            FieldPanel("thumbnail"),
        ]
        + ArticlePage.additional_content_panels
    )

    featured = models.BooleanField(default=False)

    @property
    def cover_image(self):
        return self.image

    @property
    def citation_intro(self):
        return _("To cite this radio episode: ")


class PlaylistPage(ArticlePage):
    content_panels = (
        Page.content_panels
        + [
            MultipleChooserPanel(
                "episodes", label="Episodes", chooser_field_name="episode"
            )
        ]
        + [
            FieldPanel("body"),
            FieldPanel("endnotes"),
            InlinePanel("footnotes", label="Footnotes"),
        ]
    )
    parent_page_types = ["logbooks.RadioPlaylistIndexPage"]

    class Meta:
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"

    def get_thumbnail_images(self):
        thumbnails = set(item.episode.thumbnail for item in self.episodes.all())
        return list(thumbnails)

    @property
    def real_contributors(self):
        return []

    @property
    def image(self):
        first_child_episode = self.episodes.order_by("-id").first()
        if not first_child_episode:
            return None
        return first_child_episode.episode.image

    @property
    def all_localized_tags(self):
        locale = Locale.get_active()
        all_tag_keys = set()
        for child_episode in self.episodes.all():
            tag_keys = child_episode.episode.tags.all().values_list(
                "translation_key", flat=True
            )
            all_tag_keys = all_tag_keys.union(tag_keys)
        localized_tags = Tag.objects.filter(
            translation_key__in=all_tag_keys, locale=locale
        )
        return list(sorted(localized_tags, key=lambda tag: tag.name))

    @property
    def episode_count(self):
        return self.episodes.count()


class PlaylistPageEpisode(Orderable):
    page = ParentalKey(PlaylistPage, on_delete=models.CASCADE, related_name="episodes")
    episode = models.ForeignKey(EpisodePage, on_delete=models.CASCADE, related_name="+")

    panels = [
        FieldPanel("episode", widget=wagtail_settings.RadioEpisodeChooser),
    ]


class RadioIndexPageMixin:
    def radio_parent_pages(self):
        locale = Locale.get_active()
        return {
            "home": RadioIndexPage.objects.filter(locale=locale).first(),
            "playlists": RadioPlaylistIndexPage.objects.filter(locale=locale).first(),
            "archive": RadioArchivePage.objects.filter(locale=locale).first(),
        }


class RadioIndexPage(RadioIndexPageMixin, IndexPage):
    """
    Archive page for the Radio. A collection of episodes.
    """

    class Meta:
        verbose_name = "Radio index page"

    def featured(self):
        return (
            EpisodePage.objects.live()
            .filter(featured=True, locale=self.locale)
            .order_by("-first_published_at")
        )

    def playlists(self):
        return PlaylistPage.objects.live().filter(locale=self.locale)


class RadioArchivePage(RadioIndexPageMixin, IndexPage):
    """
    Index page for the Radio. Featured episodes and playlists.
    """

    class Meta:
        verbose_name = "Radio archive page"

    def get_child_list_queryset(self, *args, **kwargs):
        return (
            EpisodePage.objects.live()
            .filter(locale=self.locale)
            .select_related("audio", "image", "thumbnail")
        )


class RadioPlaylistIndexPage(RadioIndexPageMixin, IndexPage):
    """
    Index page for playlists. A collection of episodes.
    """

    class Meta:
        verbose_name = "Radio playlist index page"


class LogbookEntryPage(ArticlePage):
    """
    Logbook entry pages are typically short articles, produced by consistent authors, associated with a single logbook.
    """

    class Meta:
        verbose_name = _("Logbook Entry")
        verbose_name_plural = _("Logbook Entries")

    show_in_menus_default = True
    parent_page_types = ["logbooks.LogbookPage"]
    icon_class = "icon-logbooks"

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/hWAL2vF.png"
        else:
            return static_file_absolute_url("img/mapicons/logbooks.png")

    content_html = "logbooks/content_entry/logbook_entry.html"

    def serve(self, *args, **kwargs):
        """
        Never allow logbook entries to be visited on their own.
        """
        return redirect(self.link_url)

    @property
    def link_url(self):
        """
        Wrapper for url allowing us to link to a page embedded in a parent (as with logbook entries) without
        overriding any wagtail internals
        """

        return f"{self.get_parent().url}#{self.slug}"


class LogbookPage(
    RoutablePageMixin,
    SidebarRenderableMixin,
    ChildListMixin,
    ContributorMixin,
    GeocodedMixin,
    ThumbnailMixin,
    ArticleSeoMixin,
    BaseLogbooksPage,
):
    """
    Collection of logbook entries.
    """

    class Meta:
        verbose_name = _("Logbook")
        verbose_name_plural = _("Logbooks")

    icon_class = "icon-logbooks"
    show_in_menus_default = True
    parent_page_types = ["logbooks.LogbookIndexPage"]
    show_title = True

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/hWAL2vF.png"
        else:
            return static_file_absolute_url("img/mapicons/logbooks.png")

    tags = LocalizedTaggableManager(through=AtlasTag, blank=True)
    description = RichTextField(
        features=[
            "bold",
            "italic",
            "link",
            "ol",
            "ul",
            "hr",
            "code",
            "blockquote",
            "h2",
            "h3",
            "h4",
            "image",
            "embed"
        ]
    )

    seo_description_sources = SeoMetadataMixin.seo_description_sources + ["description"]

    content_panels = (
        [
            TitleFieldPanel("title", classname="full title"),
            FieldPanel("description"),
            TagFieldPanel("tags"),
        ]
        + GeocodedMixin.content_panels
        + ContributorMixin.content_panels
    )

    settings_panels = [FieldPanel("first_published_at")] + Page.settings_panels

    api_fields = (
        [
            APIField("last_published_at"),
            APIField("icon_class"),
            APIField("tags"),
            APIRichTextField("description"),
        ]
        + ContributorMixin.api_fields
        + GeocodedMixin.api_fields
    )

    @classmethod
    def for_tag(cls, tag_or_tags, locale=None):
        """
        Return all live pages matching the tag.

        As logbook entries aren't really pages, we consider the logbooks for a given tag
        to be all logbooks that either have the tag themselves or who have an entry with the tag.
        """

        logbooks = super().for_tag(tag_or_tags).live().public()
        if locale is not None:
            logbooks = logbooks.filter(locale=locale)
        logbooks = set(logbooks)

        logbook_entry_logbooks = set(
            entry.get_parent().specific
            for entry in LogbookEntryPage.for_tag(tag_or_tags, locale=locale)
            .live()
            .public()
        )

        return logbooks.union(logbook_entry_logbooks)

    def get_thumbnail_images(self):
        image_lists = [
            page.get_thumbnail_images() for page in self.get_child_list_queryset()
        ]
        # `set()` in case an image is reused
        images = list(set(flatten_list(image_lists)))
        images.reverse()

        return [image for image in images]

    card_content_html = "logbooks/thumbnails/basic_thumbnail.html"

    @property
    def cover_image(self):
        """
        Returns the first image in the body stream (or None if there aren't any).

        Used to determine which image to contribute to a thumbnail when images from multiple pages are combined into a single thumbnail (as with logbooks)
        """

        images = self.get_thumbnail_images()
        return None if len(images) == 0 else images[0]

    @property
    def entry_tags(self):
        return list(
            set(
                tag
                for entry in self.get_child_list_queryset()
                for tag in entry.tags.all()
            )
        )

    @property
    def all_localized_tags(self):
        locale = Locale.get_active()
        tags_including_child_pages = list(self.tags.all()) + self.entry_tags
        translation_keys = [tag.translation_key for tag in tags_including_child_pages]
        localized_tags = Tag.objects.filter(
            translation_key__in=translation_keys, locale=locale
        )
        return list(sorted(localized_tags, key=lambda tag: tag.name))

    @property
    def preview_text(self):
        return self.description

    @property
    def tag_cloud(self):
        return get_nodes_and_links(self.all_localized_tags)

    @property
    def citation_intro(self):
        return _("To cite this logbook: ")

    @route(r"^(?P<path>.*)/?$")
    def serve_subpages_too(self, request, path, *args, **kwargs):
        """
        LogbookEntryPage URLs will be captured by LogbookPage.
        The path will be converted into a hash by frontend javascript.
        """
        return self.render(request, context_overrides={"hash": path})


class LogbookIndexPage(IndexPage):
    """
    Collection of logbooks.
    """

    class Meta:
        verbose_name = "Logbooks index page"

    def relevant_tags(self):
        children = Page.get_descendants(self)

        tags = Tag.objects.filter(
            logbooks_atlastag_items__content_object__live=True,
            logbooks_atlastag_items__content_object__in=children,
        ).distinct()

        return group_by_tag_name(tags)

    def get_filters(self, request):
        filter = {}

        tag_filter = request.GET.get("filter", None)
        if tag_filter is not None:
            try:
                tag_ids = Tag.get_translated_tag_ids(tag_filter)
                filter["pk__in"] = [l.id for l in LogbookPage.for_tag(tag_ids)]
            except Tag.DoesNotExist:
                pass

        return filter


class ContributorTagField(TagField):
    """
    Override the TagField form field to be a <select> dropdown.
    """

    class ContributorTagSelect(SelectMultiple):
        """
        Replace the default tag widget with a <select> dropdown, restricting
        contributor tags to one of a set, defined by the parent
        ContributorsIndexPage in the group_by_tags field.
        """

        def __init__(self, *args, **kwargs) -> None:
            locale = Locale.get_active()
            parent_page = ContributorsIndexPage.objects.filter(locale=locale).first()
            tags = (
                parent_page.group_by_tags.all()
                if parent_page
                else Tag.objects.filter(
                    name__in=["internal", "external"], locale__language_code="en"
                )
            )
            choices = [(tag.name, tag.name) for tag in tags]
            super().__init__(*args, **kwargs, choices=choices)

    widget = ContributorTagSelect

    def clean(self, value):
        """
        The value provided by the <select> dropdown does not need to be
        parsed (unlike the default tag component, which uses comma-separated values).
        """
        return value


class ContributorTaggableManager(LocalizedTaggableManager):
    """
    Tags field that uses a select dropdown instead of the default tag widget (see above).
    Used for contributors, which have a restricted range of tags available.
    """

    def formfield(self, form_class=ContributorTagField, **kwargs):
        return super().formfield(ContributorTagField, **kwargs)


class ContributorPage(GeocodedMixin, ArticleSeoMixin, BaseLogbooksPage):
    allow_search = True
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ["logbooks.ContributorsIndexPage"]
    icon_class = "icon-contributor"
    show_title = True

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/aebDhw0.png"
        else:
            return static_file_absolute_url("img/mapicons/circle.png")

    class Meta:
        verbose_name = _("Contributor")
        verbose_name_plural = _("Contributors")

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contributor_pages",
    )

    byline = CharField(max_length=1000, blank=True, null=True)
    avatar = ForeignKey(CmsImage, on_delete=models.SET_NULL, null=True, blank=True)
    bio = RichTextField(blank=True, null=True)

    tags = ContributorTaggableManager(through=AtlasTag, help_text="")
    past_contributor = models.BooleanField(blank=True, default=False)

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("byline"),
        FieldPanel("avatar"),
        AutocompletePanel("user"),
        FieldPanel("bio"),
        FieldPanel("tags"),
        FieldPanel("past_contributor"),
    ] + GeocodedMixin.content_panels

    seo_image_sources = ["og_image", "avatar", "default_seo_image"]

    seo_description_sources = SeoMetadataMixin.seo_description_sources + ["byline"]

    @classmethod
    def create_for_user(cls, user):
        if ContributorPage.objects.filter(user=user).exists():
            return

        contributor_index = ContributorsIndexPage.objects.first()

        title = user.get_full_name() or user.username
        contributor_page = ContributorPage(title=title, slug=slugify(title), user=user)
        contributor_index.add_child(instance=contributor_page)
        contributor_page.save()

    card_content_html = "logbooks/thumbnails/contributor_thumbnail.html"

    @property
    def all_localized_tags(self):
        if self.slug == "common-knowledge":
            return []

        if not self.user:
            return []

        locale = Locale.get_active()
        translation_keys = list(
            self.user.edited_tags.values_list("translation_key", flat=True)
        ) + list(self.tags.values_list("translation_key", flat=True))
        localized_tags = Tag.objects.filter(
            translation_key__in=translation_keys, locale=locale
        )
        return list(sorted(localized_tags, key=lambda tag: tag.name))

    @classmethod
    def for_tag(cls, tag_or_tags, locale=None):
        qs = cls.objects.live().filter(
            Q(user__in=User.for_tag(tag_or_tags))
            | Q(tagged_items__tag__in=ensure_list(tag_or_tags))
        )
        if locale is not None:
            qs = qs.filter(locale=locale)
        return qs.distinct()

    @property
    def tag_cloud(self):
        return get_nodes_and_links(self.all_localized_tags)

    api_fields = [
        APIField("last_published_at"),
        APIField("byline"),
        APIField("avatar"),
        APIField("user"),
        APIRichTextField("bio"),
    ]


class ContributorsIndexPage(IndexPage):
    """
    Collection of people
    """

    show_in_menus_default = True
    group_by_tags = LocalizedTaggableManager(through=AtlasTag, blank=True)
    content_panels = IndexPage.content_panels + [
        FieldPanel("group_by_tags", heading="Group contributors by tags")
    ]

    class Meta:
        verbose_name = "Contributors index page"

    # Default child list filters out untranslated pages, but
    # we should always show all contributors
    def get_child_list_queryset(self, *args, **kwargs):
        return self.get_children().live().specific()

    def relevant_tags(self):
        return group_by_tag_name(
            Tag.objects.filter(
                logbooks_atlastag_items__content_object__live=True
            ).distinct()
        )

    def get_filters(self, request):
        filter = {}

        tag_filter = request.GET.get("filter", None)
        if tag_filter is not None:
            try:
                tags = Tag.objects.filter(slug=tag_filter)
                filter["pk__in"] = [page.id for page in ContributorPage.for_tag(tags)]

            except Tag.DoesNotExist:
                pass

        return filter

    def get_contributors_for_tag(self, request, tag=None, filter=None, sort=None):
        qs: models.QuerySet = self.get_child_list_queryset(request).filter(
            tagged_items__tag=tag
        )
        if request.user.is_anonymous:
            qs = qs.public()

        if filter:
            if isinstance(filter, dict):
                qs = qs.filter(**filter)
            else:
                qs = qs.filter(filter)
            # Complex filters can introduce joins that create duplicate results
            # Fix with distinct()
            qs = qs.distinct()

        if sort:
            if "original_published_at" in sort.ordering:
                # Subquery to get all the translations of each page, ordered by publish date
                translations = ContributorPage.objects.filter(
                    translation_key=OuterRef("translation_key")
                ).order_by("first_published_at")

                # Annotate with the earliest publish date in the subquery
                # This will be the publish date of the original version of the page
                qs = qs.annotate(
                    original_published_at=Subquery(
                        translations.values("first_published_at")[:1]
                    )
                )
            qs = qs.order_by(sort.ordering)

        return qs

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        contributors_by_tag = {}
        filter = self.get_filters(request)
        sort = self.get_sort(request)
        for tag in self.group_by_tags.all():
            qs = self.get_contributors_for_tag(request, tag, filter, sort)
            if len(qs):
                contributors_by_tag[tag.localized.name] = qs

        remaining_qs = self.get_contributors_for_tag(
            request, tag=None, filter=filter, sort=sort
        )
        if len(remaining_qs):
            contributors_by_tag[_("Uncategorized")] = remaining_qs

        divided_sections = []
        for title, contributors in contributors_by_tag.items():
            current = []
            past = []
            for contributor in contributors:
                if contributor.past_contributor:
                    past.append(contributor)
                else:
                    current.append(contributor)
            divided_sections.append({"title": title, "current": current, "past": past})

        context["sections"] = divided_sections
        context["tag_filter"] = request.GET.get("filter", None)

        return context
