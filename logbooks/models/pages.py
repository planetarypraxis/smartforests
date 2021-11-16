from django.db import models
from django.conf import settings
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.text import slugify
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.core.models import Page
from wagtail.search.index import AutocompleteField
from smartforests.models import Tag, User
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
from logbooks.models.mixins import ArticlePage, BaseLogbooksPage, ContributorMixin, DescendantPageContributorMixin, GeocodedMixin, IndexPage, ThumbnailMixin, SidebarRenderableMixin
from logbooks.models.snippets import AtlasTag
from smartforests.models import CmsImage
from logbooks.models.tag_cloud import TagCloud
from django.shortcuts import redirect
from wagtailautocomplete.edit_handlers import AutocompletePanel


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
    icon_class = "icon-radio"

    image = ForeignKey(CmsImage, on_delete=models.SET_NULL,
                       null=True, blank=True)
    audio = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        MediaChooserPanel('audio', media_type='audio'),
        ImageChooserPanel('image'),
    ] + ArticlePage.additional_content_panels

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
    is_content_page = True
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


class ContributorPage(GeocodedMixin, BaseLogbooksPage):
    allow_search = True
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ['logbooks.ContributorsIndexPage']
    icon_class = 'icon-contributor'

    class Meta:
        verbose_name = "Contributor"

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
        ImageChooserPanel('avatar'),
        AutocompletePanel('user'),
        FieldPanel('bio')
    ] + GeocodedMixin.content_panels

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

    def card_content_html(self):
        return render_to_string('logbooks/thumbnails/contributor_thumbnail.html', {
            'self': self
        })

    @property
    def tags(self):
        if self.user:
            return self.user.edited_tags()

    @classmethod
    def for_tag(cls, tag):
        return cls.objects.live().filter(
            user__in=User.with_edited_tags(tag)
        )


class ContributorsIndexPage(IndexPage):
    '''
    Collection of people
    '''

    class Meta:
        verbose_name = "Contributors index page"

    def relevant_tags(self):
        return group_by_title(Tag.objects.all(), key='name')

    def get_child_list_queryset(self, request):
        return ContributorPage.objects.child_of(self).live()

    def get_filters(self, request):
        filter = {}

        tag_filter = request.GET.get('filter', None)
        if tag_filter is not None:
            try:
                tag = Tag.objects.get(slug=tag_filter)
                filter['user__in'] = User.with_edited_tags(tag)

            except Tag.DoesNotExist:
                pass

        return filter
