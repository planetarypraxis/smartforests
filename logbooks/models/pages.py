from logbooks.thumbnail import generate_thumbnail
from django.contrib.contenttypes.models import ContentType
from django.db import models
from wagtail.core.models import Page, PageManager
from django.template.loader import render_to_string
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.snippets.models import register_snippet
from commonknowledge.wagtail.models import ChildListMixin
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks
from wagtail.contrib.settings.models import BaseSetting, register_setting

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

    def cover_image(self):
        # Find the first image in this story
        for block in self.body:
            if block.block_type == 'image':
                image: CmsImage = block.value.get('image')
                return image


class LogbookIndexPage(ChildListMixin, Page):
    show_in_menus_default = True
    parent_page_types = ['home.HomePage']
    subpage_types = ['logbooks.LogbookPage']


class LogbookPage(Page):
    objects = IndexedPageManager()
    show_in_menus_default = True
    parent_page_types = ['logbooks.LogbookIndexPage']
    subpage_types = []
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tags'),
    ]

    @property
    def thumbnail_image(self):
        if self.index_entry and self.index_entry.thumbnail_image:
            return self.index_entry.thumbnail_image

    def regenerate_thumbnail(self, index_data):
        stories = index_data.get_related_pages(
            metadata__content_type=ContentType.objects.get_for_model(
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
