from django.db import models
from django.conf import settings
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.text import slugify
from wagtail.models import Page
from smartforests.models import Tag, User
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField
from wagtailmedia.edit_handlers import MediaChooserPanel
from commonknowledge.wagtail.helpers import get_children_of_type
from commonknowledge.wagtail.models import ChildListMixin
from commonknowledge.django.cache import django_cached_model
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from smartforests.util import ensure_list, flatten_list, group_by_tag_name, static_file_absolute_url
from logbooks.models.fields import TagFieldPanel, LocalizedTaggableManager
from logbooks.models.mixins import ArticlePage, ArticleSeoMixin, BaseLogbooksPage, ContributorMixin, GeocodedMixin, IndexPage, ThumbnailMixin, SidebarRenderableMixin
from logbooks.models.snippets import AtlasTag
from smartforests.models import CmsImage
from django.shortcuts import redirect
from wagtailautocomplete.edit_handlers import AutocompletePanel
from smartforests.utils.api import APIRichTextField
from smartforests.mixins import SeoMetadataMixin
from smartforests.tag_cloud import get_nodes_and_links


class StoryPage(ArticlePage):
    '''
    Stories are longer, self-contained articles.
    '''

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    icon_class = 'icon-stories'

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/6TwclOR.png"
        else:
            return static_file_absolute_url('img/mapicons/stories.png')

    show_in_menus_default = True
    parent_page_types = ['logbooks.StoryIndexPage']

    image = ForeignKey(CmsImage, on_delete=models.SET_NULL,
                       null=True, blank=True)

    content_panels = ArticlePage.content_panels + [
        FieldPanel('image')
    ]

    api_fields = ArticlePage.api_fields + [
        APIField('image'),
    ]

    @property
    def cover_image(self):
        return self.image

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


class StoryIndexPage(IndexPage):
    '''
    Collection of stories.
    '''

    class Meta:
        verbose_name = "Stories index page"


class EpisodePage(ArticlePage):
    '''
    Episodes are individual items for the radio.
    '''

    class Meta:
        verbose_name = "Radio Episode"
        verbose_name_plural = "Radio Episodes"

    show_in_menus_default = True
    parent_page_types = ['logbooks.RadioIndexPage']
    icon_class = "icon-radio"

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/N0g8oFn.png"
        else:
            return static_file_absolute_url('img/mapicons/radio.png')

    image = ForeignKey(CmsImage, on_delete=models.SET_NULL,
                       null=True, blank=True)

    thumbnail = ForeignKey(CmsImage, related_name='episode_thumbnail', on_delete=models.SET_NULL,
                           null=True, blank=True)

    api_fields = ArticlePage.api_fields + [
        APIField('image'),
        APIField('thumbnail', serializer=ImageRenditionField('fill-100x100')),
    ]

    audio = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        MediaChooserPanel('audio', media_type='audio'),
        FieldPanel('image'),
        FieldPanel('thumbnail'),
    ] + ArticlePage.additional_content_panels

    @property
    def cover_image(self):
        return self.image


class RadioIndexPage(IndexPage):
    '''
    Index page for the Radio. A collection of episodes.
    '''

    class Meta:
        verbose_name = "Radio index page"


class LogbookEntryPage(ArticlePage):
    '''
    Logbook entry pages are typically short articles, produced by consistent authors, associated with a single logbook.
    '''

    class Meta:
        verbose_name = "Logbook Entry"
        verbose_name_plural = "Logbook Entries"

    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookPage']
    icon_class = 'icon-logbooks'

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/hWAL2vF.png"
        else:
            return static_file_absolute_url('img/mapicons/logbooks.png')

    content_html = 'logbooks/content_entry/logbook_entry.html'

    def serve(self, *args, **kwargs):
        '''
        Never allow logbook entries to be visited on their own.
        '''
        return redirect(self.link_url)

    @property
    def link_url(self):
        '''
        Wrapper for url allowing us to link to a page embedded in a parent (as with logbook entries) without
        overriding any wagtail internals
        '''

        return f'{self.get_parent().url}#{self.slug}'


class LogbookPage(RoutablePageMixin, SidebarRenderableMixin, ChildListMixin, ContributorMixin, GeocodedMixin, ThumbnailMixin, ArticleSeoMixin, BaseLogbooksPage):
    '''
    Collection of logbook entries.
    '''
    class Meta:
        verbose_name = "Logbook"
        verbose_name_plural = "Logbooks"

    icon_class = 'icon-logbooks'
    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookIndexPage']
    show_title = True

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/hWAL2vF.png"
        else:
            return static_file_absolute_url('img/mapicons/logbooks.png')

    tags = LocalizedTaggableManager(through=AtlasTag, blank=True)
    description = RichTextField(
        features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'code', 'blockquote', 'h2', 'h3', 'h4'])

    seo_description_sources = SeoMetadataMixin.seo_description_sources + [
        "description"
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('description'),
        TagFieldPanel('tags'),
    ] + GeocodedMixin.content_panels + ContributorMixin.content_panels

    settings_panels = [FieldPanel("first_published_at")] + Page.settings_panels

    api_fields = [
        APIField('last_published_at'),
        APIField('icon_class'),
        APIField('tags'),
        APIRichTextField('description'),
    ] + ContributorMixin.api_fields + GeocodedMixin.api_fields

    @classmethod
    def for_tag(cls, tag_or_tags):
        '''
        Return all live pages matching the tag.

        As logbook entries aren't really pages, we consider the logbooks for a given tag
        to be all logbooks that either have the tag themselves or who have an entry with the tag.
        '''

        logbooks = set(super().for_tag(tag_or_tags).live().public())
        logbook_entry_logbooks = set(entry.get_parent().specific
                                     for entry in LogbookEntryPage.for_tag(tag_or_tags).live().public())

        return logbooks.union(logbook_entry_logbooks)

    def get_thumbnail_images(self):
        image_lists = [page.get_thumbnail_images()
                       for page in self.get_child_list_queryset()]
        # `set()` in case an image is reused
        images = list(set(flatten_list(image_lists)))
        images.reverse()

        return [image for image in images]

    card_content_html = 'logbooks/thumbnails/basic_thumbnail.html'

    @property
    def cover_image(self):
        '''
        Returns the first image in the body stream (or None if there aren't any).

        Used to determine which image to contribute to a thumbnail when images from multiple pages are combined into a single thumbnail (as with logbooks)
        '''

        images = self.get_thumbnail_images()
        return None if len(images) == 0 else images[0]

    @property
    def entry_tags(self):
        return list(set(
            tag
            for entry in self.get_child_list_queryset()
            for tag in entry.tags.all()
        ))

    @property
    def all_localized_tags(self):
        localized_tags = set()
        tags_including_child_pages = list(self.tags.all()) + self.entry_tags
        for tag in tags_including_child_pages:
            if tag.localized:
                localized_tags.add(tag.localized)
            else:
                localized_tags.add(tag)
        return list(sorted(localized_tags, key=lambda tag: tag.name))

    @property
    def preview_text(self):
        return self.description

    @property
    def tag_cloud(self):
        return get_nodes_and_links(self.all_localized_tags)

    @route(r'^(?P<path>.*)/?$')
    def serve_subpages_too(self, request, path, *args, **kwargs):
        '''
        LogbookEntryPage URLs will be captured by LogbookPage.
        The path will be converted into a hash by frontend javascript.
        '''
        return self.render(request, context_overrides={
            'hash': path
        })


class LogbookIndexPage(IndexPage):
    '''
    Collection of logbooks.
    '''

    class Meta:
        verbose_name = "Logbooks index page"

    def relevant_tags(self):
        children = Page.get_descendants(self)

        tags = Tag.objects.filter(
            logbooks_atlastag_items__content_object__live=True,
            logbooks_atlastag_items__content_object__in=children
        ).distinct()

        return group_by_tag_name(tags)

    def get_filters(self, request):
        filter = {}

        tag_filter = request.GET.get('filter', None)
        if tag_filter is not None:
            try:
                tag_ids = Tag.get_translated_tag_ids(tag_filter)
                filter['pk__in'] = [l.id for l in LogbookPage.for_tag(tag_ids)]
            except Tag.DoesNotExist:
                pass

        return filter


class ContributorPage(GeocodedMixin, ArticleSeoMixin, BaseLogbooksPage):
    allow_search = True
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ['logbooks.ContributorsIndexPage']
    icon_class = 'icon-contributor'
    show_title = True

    @property
    def map_marker(self):
        if settings.DEBUG:
            # Mapbox API requires an online resource to generate images against
            return "https://imgur.com/aebDhw0.png"
        else:
            return static_file_absolute_url('img/mapicons/circle.png')

    class Meta:
        verbose_name = "Contributor"
        verbose_name_plural = "Contributors"

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='contributor_pages'
    )

    byline = CharField(max_length=1000, blank=True, null=True)
    avatar = ForeignKey(CmsImage, on_delete=models.SET_NULL,
                        null=True, blank=True)
    bio = RichTextField(blank=True, null=True)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('byline'),
        FieldPanel('avatar'),
        AutocompletePanel('user'),
        FieldPanel('bio')
    ] + GeocodedMixin.content_panels

    seo_image_sources = [
        "og_image",
        "avatar",
        "default_seo_image"
    ]

    seo_description_sources = SeoMetadataMixin.seo_description_sources + [
        "byline"
    ]

    @classmethod
    def create_for_user(cls, user):
        if ContributorPage.objects.filter(user=user).exists():
            return

        contributor_index = ContributorsIndexPage.objects.first()

        title = user.get_full_name() or user.username
        contributor_page = ContributorPage(
            title=title,
            slug=slugify(title),
            user=user
        )
        contributor_index.add_child(instance=contributor_page)
        contributor_page.save()

    card_content_html = 'logbooks/thumbnails/contributor_thumbnail.html'

    @property
    def all_localized_tags(self):
        if not self.user:
            return []

        localized_tags = set()
        for tag in self.user.edited_tags:
            if tag.localized:
                localized_tags.add(tag.localized)
            else:
                localized_tags.add(tag)
        return list(sorted(localized_tags, key=lambda tag: tag.name))

    @classmethod
    def for_tag(cls, tag_or_tags):
        return cls.objects.live().filter(
            user__in=User.for_tag(tag_or_tags)
        )

    @property
    def tag_cloud(self):
        return get_nodes_and_links(self.all_localized_tags)

    api_fields = [
        APIField('last_published_at'),
        APIField('byline'),
        APIField('avatar'),
        APIField('user'),
        APIRichTextField('bio'),
    ]


class ContributorsIndexPage(IndexPage):
    '''
    Collection of people
    '''

    show_in_menus_default = True

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

        tag_filter = request.GET.get('filter', None)
        if tag_filter is not None:
            try:
                tags = Tag.objects.filter(slug=tag_filter)
                filter['pk__in'] = ContributorPage.for_tag(tags)

            except Tag.DoesNotExist:
                pass

        return filter
