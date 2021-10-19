from django.template.loader import render_to_string
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api.conf import APIField
from wagtail.core.fields import RichTextField
from commonknowledge.wagtail.helpers import get_children_of_type
from commonknowledge.wagtail.models import ChildListMixin
from commonknowledge.django.cache import django_cached_model

from logbooks.models.helpers import group_by_title
from logbooks.models.mixins import ArticlePage, BaseLogbooksPage, ContributorMixin, GeocodedMixin, ThumbnailMixin, IndexedPageManager
from logbooks.models.snippets import AtlasTag


class StoryPage(ArticlePage):
    '''
    Logbook entry pages are typically short articles, produced by consistent authors, associated with a single logbook.
    '''

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    show_in_menus_default = True
    parent_page_types = ['logbooks.StoryIndexPage']


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


class LogbookEntryPage(ArticlePage):
    '''
    Logbook entry pages are typically short articles, produced by consistent authors, associated with a single logbook.
    '''

    class Meta:
        verbose_name = "Logbook Entry"
        verbose_name_plural = "Logbook Entries"

    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookPage']

    def content_html(self):
        '''
        Render just the content of the page, for embedding in a logbook
        '''

        return render_to_string('logbooks/content_entry/logbook_entry.html', {
            'self': self
        })


class LogbookPage(ChildListMixin, ContributorMixin, GeocodedMixin, ThumbnailMixin, BaseLogbooksPage):
    '''
    Collection of logbook entries.
    '''

    objects = IndexedPageManager()
    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookIndexPage']

    tags = ClusterTaggableManager(through=AtlasTag, blank=True)
    description = RichTextField()

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('description'),
        FieldPanel('tags'),
    ] + ContributorMixin.content_panels + GeocodedMixin.content_panels

    api_fields = [
        APIField('tags'),
        APIField('description'),
    ] + ContributorMixin.api_fields + GeocodedMixin.api_fields

    def get_child_list_queryset(self, _request):
        return self.logbook_entries

    def get_thumbnail_images(self):
        return tuple(x.cover_image() for x in self.logbook_entries if x.cover_image() is not None)

    def card_content_html(self):
        return render_to_string('logbooks/thumbnails/basic_thumbnail.html', {
            'self': self
        })

    @property
    def logbook_entries(self):
        return get_children_of_type(self, LogbookEntryPage)


class LogbookIndexPage(ChildListMixin, BaseLogbooksPage):
    '''
    Collection of logbooks.
    '''

    page_size = 50
    show_in_menus_default = True
    parent_page_types = ['home.HomePage']

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
