from commonknowledge.wagtail.helpers import get_children_of_type
from logbooks.models.helpers import group_by_title
from logbooks.thumbnail import generate_thumbnail
from django.contrib.contenttypes.models import ContentType
from django.db import models
from wagtail.core.models import Page, PageManager
from django.template.loader import render_to_string
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag
from wagtail.snippets.models import register_snippet
from commonknowledge.wagtail.models import ChildListMixin
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks
from wagtail.contrib.settings.models import BaseSetting, register_setting
from commonknowledge.django.cache import django_cached_model

from smartforests.models import CmsImage


# Should these just be pages?
@register_snippet
class AtlasTag(TaggedItemBase):
    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)


class IndexedPageManager(PageManager):
    def get_queryset(self):
        return super().get_queryset().select_related('index_entry')


# CMS settings for canonical index pages
@register_setting
class ImportantPages(BaseSetting):
    logbooks_index_page = models.ForeignKey(
        'logbooks.LogbookIndexPage', null=True, on_delete=models.SET_NULL, related_name='+')
    stories_index_page = models.ForeignKey(
        'logbooks.StoryIndexPage', null=True, on_delete=models.SET_NULL, related_name='+')

    panels = [
        PageChooserPanel('logbooks_index_page'),
        PageChooserPanel('stories_index_page'),
    ]


class StoryIndexPage(ChildListMixin, Page):
    show_in_menus_default = True
    parent_page_types = ['home.HomePage']
    subpage_types = ['logbooks.StoryPage']


class QuoteBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(features=['bold', 'italic', 'link'])
    author = blocks.CharBlock(required=False)
    title = blocks.CharBlock(required=False)
    date = blocks.DateBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        template = 'logbooks/story_blocks/quote.html'
        icon = 'quote'


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    caption = blocks.CharBlock()

    class Meta:
        template = 'logbooks/story_blocks/image.html'
        icon = 'image'


class StoryPage(Page):
    @classmethod
    def content_type_id(cls):
        return ContentType.objects.get_for_model(cls).id

    objects = IndexedPageManager()
    show_in_menus_default = True
    parent_page_types = ['logbooks.StoryIndexPage']
    subpage_types = []
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)

    # Streamfield of options here
    body = StreamField([
        ('text', blocks.RichTextBlock(features=[
         'h3', 'bold', 'italic', 'link', 'ol', 'ul'])),
        ('quote', QuoteBlock()),
        ('embed', blocks.RichTextBlock(features=['embed'])),
        ('image', ImageBlock()),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
        StreamFieldPanel('body'),
    ]

    def regenerate_thumbnail(self, *args):
        return generate_thumbnail(self.images(), fileslug=f'storythumbnail_{self.slug}')

    def cover_image(self):
        images = self.images()
        return None if len(images) == 0 else images[0]

    def images(self):
        return tuple(
            block.value.get('image')
            for block in self.body
            if block.block_type == 'image'
            and block.value.get('image')
        )

    @property
    def thumbnail_image(self):
        if self.index_entry and self.index_entry.thumbnail_image:
            return self.index_entry.thumbnail_image

    def thumbnail_content(self):
        if self.thumbnail_image is None:
            return render_to_string('logbooks/thumbnails/story_no_image.html', {
                'self': self
            })

        return render_to_string('logbooks/thumbnails/story_images.html', {
            'self': self,
            'thumbnail_images': self.thumbnail_image,
        })


class LogbookIndexPage(ChildListMixin, Page):
    page_size = 50
    show_in_menus_default = True
    parent_page_types = ['home.HomePage']
    subpage_types = ['logbooks.LogbookPage']

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

        return LogbookPageIndex.filter_pages(**filter)

    @django_cached_model('logbooks.LogbookIndexPage.relevant_tags')
    def relevant_tags(self):
        return group_by_title(Tag.objects.filter(logbooks_atlastag_items__isnull=False).distinct(), key='name')


class LogbookPage(ChildListMixin, Page):
    objects = IndexedPageManager()
    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookIndexPage']
    subpage_types = []
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)

    content_panels = [
        FieldPanel('title', classname="full title"),

        FieldPanel('tags'),
    ]

    def get_child_list_queryset(self, request):
        tag_filter = request.GET.get('filter', None)
        filter = {}

        if tag_filter is not None:
            filter['tags__contains'] = tag_filter

        return self.index_entry.get_related_pages(content_type=StoryPage.content_type_id(), **filter)

    @property
    def thumbnail_image(self):
        if self.index_entry and self.index_entry.thumbnail_image:
            return self.index_entry.thumbnail_image

    def regenerate_thumbnail(self, index_data):
        stories = index_data.get_related_pages(
            content_type=ContentType.objects.get_for_model(
                StoryPage).id
        )

        images = tuple(
            x.cover_image() for x in stories if x.cover_image() is not None)

        return generate_thumbnail(images, fileslug=f'logbookthumbnail_{self.slug}')

    def thumbnail_content(self):
        if self.thumbnail_image is None:
            return render_to_string('logbooks/thumbnails/logbook_no_image.html', {
                'self': self
            })

        return render_to_string('logbooks/thumbnails/logbook_images.html', {
            'self': self,
            'thumbnail_images': self.thumbnail_image,
        })
