from django.db import models
from wagtail.core.models import Page, PageManager
from django.db.models import Count

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.snippets.models import register_snippet
from commonknowledge.wagtail.models import ChildListMixin
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.fields import RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks
from wagtail.contrib.settings.models import BaseSetting, register_setting
from smartforests.models import CmsImage


# Should these just be pages?
@register_snippet
class AtlasTag(TaggedItemBase):
    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)


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
    parent_page_types = ['home.HomePage']
    subpage_types = ['logbooks.StoryPage']


class StoryPage(Page):
    parent_page_types = ['logbooks.StoryIndexPage']
    subpage_types = []
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)

    # Streamfield of options here
    body = StreamField([
        ('text', blocks.RichTextBlock(features=[
         'h3', 'bold', 'italic', 'link', 'ol', 'ul'])),
        ('quote', blocks.StructBlock([
            ('text', blocks.RichTextBlock(
                features=['bold', 'italic', 'link'])),
            ('author', blocks.CharBlock(required=False)),
            ('date', blocks.DateBlock(required=False)),
            ('link', blocks.URLBlock(required=False)),
        ])),
        ('embed', blocks.RichTextBlock(features=['embed'])),
        ('image', blocks.StructBlock([
            ('image', ImageChooserBlock()),
            ('caption', blocks.CharBlock()),
        ])),
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
    parent_page_types = ['home.HomePage']
    subpage_types = ['logbooks.LogbookPage']


class LogbookPage(Page):
    parent_page_types = ['logbooks.LogbookIndexPage']
    subpage_types = []
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('tags'),
    ]

    def related_stories(self):
        logbooks = LogbookPage.objects.filter(
            tagged_items__tag__in=self.tags.all()).live().distinct()

        return logbooks.annotate(Count('title')).order_by('-title__count')
