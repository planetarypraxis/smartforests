from django.db import models
from django.db.models.fields.related import ForeignKey
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField
from commonknowledge.wagtail.helpers import get_children_of_type
from commonknowledge.wagtail.models import ChildListMixin
from commonknowledge.django.cache import django_cached_model
from wagtail.api import APIField
from logbooks.models.helpers import group_by_title
from logbooks.models.mixins import ArticlePage, BaseLogbooksPage, ContributorMixin, DescendantPageContributorMixin, GeocodedMixin, ThumbnailMixin, IndexedPageManager, SidebarRenderableMixin, TurboFrameMixin
from logbooks.models.snippets import AtlasTag
from smartforests.models import CmsImage
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


class StoryIndexPage(ChildListMixin, BaseLogbooksPage):
    '''
    Collection of stories.
    '''

    class Meta:
        verbose_name = "Stories index page"

    def get_child_list_queryset(self, *args, **kwargs):
        return self.get_children().order_by('-last_published_at').specific()

    show_in_menus_default = True
    parent_page_types = ['home.HomePage']
    max_count = 1


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

    def get_url(self, request=None, current_site=None):
        return self.get_parent().get_url(request=request)

    @property
    def full_url(self):
        return self.get_parent().full_url


class LogbookPage(SidebarRenderableMixin, ChildListMixin, ContributorMixin, GeocodedMixin, ThumbnailMixin, BaseLogbooksPage):
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
    def preview_text(self):
        return self.description


class LogbookIndexPage(ChildListMixin, RoutablePageMixin, BaseLogbooksPage):
    '''
    Collection of logbooks.
    '''

    allow_search = True
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ['home.HomePage']
    max_count = 1

    def get_child_list_queryset(self, request):
        from .indexes import LogbookPageIndex

        tag_filter = request.GET.get('filter', None)
        filter = {}

        if tag_filter is not None:
            try:
                tag = Tag.objects.get(slug=tag_filter)
                filter['tags__contains'] = tag.id
            except Tag.DoesNotExist:
                pass

        return LogbookPageIndex.filter_pages(
            **filter, content_type=LogbookPage.content_type_id()).specific()

    @django_cached_model('logbooks.LogbookIndexPage.relevant_tags')
    def relevant_tags(self):
        return group_by_title(Tag.objects.filter(logbooks_atlastag_items__isnull=False).distinct(), key='name')

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['tag_filter'] = request.GET.get('filter', None)

        return context
