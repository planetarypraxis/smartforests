from django.db import models
from django.conf import settings
from django.db.models.fields.related import ForeignKey
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from modelcluster.contrib.taggit import ClusterTaggableManager
from smartforests.models import Tag
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField
from wagtailmedia.edit_handlers import MediaChooserPanel
from commonknowledge.wagtail.helpers import get_children_of_type
from commonknowledge.wagtail.models import ChildListMixin
from commonknowledge.django.cache import django_cached_model
from wagtail.api import APIField
from smartforests.util import group_by_title
from logbooks.models.mixins import ArticlePage, BaseLogbooksPage, ContributorMixin, DescendantPageContributorMixin, GeocodedMixin, IndexPage, ThumbnailMixin, IndexedPageManager, SidebarRenderableMixin
from logbooks.models.snippets import AtlasTag
from smartforests.models import CmsImage
from logbooks.models.tag_cloud import TagCloud
from django.shortcuts import redirect


class StoryPage(ArticlePage):
    '''
    Stories are longer, self-contained articles.
    '''

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    icon_class = 'icon-stories'

    show_in_menus_default = True
    parent_page_types = ['logbooks.StoryIndexPage']

    image = ForeignKey(CmsImage, on_delete=models.SET_NULL,
                       null=True, blank=True)

    content_panels = ArticlePage.content_panels + [
        ImageChooserPanel('image')
    ]

    def cover_image(self):
        return self.image


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

    show_in_menus_default = True
    parent_page_types = ['logbooks.RadioIndexPage']

    image = ForeignKey(CmsImage, on_delete=models.SET_NULL,
                       null=True, blank=True)
    audio = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = ArticlePage.content_panels + [
        ImageChooserPanel('image'),
        MediaChooserPanel('audio', media_type='audio'),
    ]

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

    def content_html(self):
        '''
        Render just the content of the page, for embedding in a logbook
        '''

        return render_to_string('logbooks/content_entry/logbook_entry.html', {
            'self': self
        })

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


class LogbookPage(RoutablePageMixin, SidebarRenderableMixin, ChildListMixin, ContributorMixin, GeocodedMixin, ThumbnailMixin, BaseLogbooksPage):
    '''
    Collection of logbook entries.
    '''
    class Meta:
        verbose_name = "Logbook"
        verbose_name_plural = "Logbooks"

    icon_class = 'icon-logbooks'

    objects = IndexedPageManager()
    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookIndexPage']

    tags = ClusterTaggableManager(through=AtlasTag, blank=True)
    description = RichTextField()

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('description'),
        FieldPanel('tags'),
    ] + DescendantPageContributorMixin.content_panels + GeocodedMixin.content_panels

    api_fields = [
        APIField('icon_class'),
        APIField('tags'),
        APIField('description'),
    ] + DescendantPageContributorMixin.api_fields + GeocodedMixin.api_fields

    def get_child_list_queryset(self, _request):
        return self.logbook_entries

    def get_thumbnail_images(self):
        return tuple(x.cover_image() for x in self.logbook_entries if x.cover_image() is not None)

    def card_content_html(self):
        return render_to_string('logbooks/thumbnails/basic_thumbnail.html', {
            'self': self
        })

    def cover_image(self):
        '''
        Returns the first image in the body stream (or None if there aren't any).

        Used to determine which image to contribute to a thumbnail when images from multiple pages are combined into a single thumbnail (as with logbooks)
        '''

        images = self.get_thumbnail_images()
        return None if len(images) == 0 else images[0]

    @property
    def logbook_entries(self):
        return get_children_of_type(self, LogbookEntryPage)

    @property
    def entry_tags(self):
        return [
            tag
            for entry in self.logbook_entries
            for tag in entry.tags.all()
        ]

    @property
    def all_tags(self):
        return self.entry_tags + list(self.tags.all())

    @property
    def preview_text(self):
        return self.description

    @property
    def tag_cloud(self):
        return TagCloud.get_related(self.all_tags)

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
