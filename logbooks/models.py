from django.db import models
from wagtail.core.models import Page, PageManager
from django.db.models import Count

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.snippets.models import register_snippet
from commonknowledge.wagtail.models import ChildListMixin
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.fields import RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks


# Should these just be pages?
@register_snippet
class AtlasTag(TaggedItemBase):
    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)


class StoryIndexPage(Page):
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
        # We'll use this for the logbook album view
        # Look in self.body for an image and pull out the first one
        for block in self.body.stream_data:
            print(block['type'], block)
            if block['type'] == 'imageBlock':
                return block
        pass


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
        tags = self.tags.all()
        print(tags)
        matches = StoryPage.objects.filter(tags__in=tags).live()
        print(matches)
        # .annotate(Count('title'))
        # print(matches)
        # related = matches.order_by('-title__count')
        return matches


class Tag():
    # description = string
    pass
