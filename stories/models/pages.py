from datetime import datetime
from django.db.models.fields import CharField
from commonknowledge.wagtail.helpers import get_children_of_type
from smartforests.utils.helpers import group_by_title
from smartforests.utils.thumbnail import generate_thumbnail
from django.contrib.contenttypes.models import ContentType
from django.db import models
from wagtail.core.models import Page, PageManager
from django.template.loader import render_to_string
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag
from wagtail.snippets.models import register_snippet
from commonknowledge.wagtail.models import ChildListMixin
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core import blocks
from wagtail.contrib.settings.models import BaseSetting, register_setting
from commonknowledge.django.cache import django_cached_model
from django.contrib.gis.db import models as geo
from smartforests.models import AtlasTag


class IndexedPageManager(PageManager):
    def get_queryset(self):
        return super().get_queryset().select_related('index_entry')


class StoryIndexPage(ChildListMixin, Page):
    class Meta:
        verbose_name = "Stories index page"

    show_in_menus_default = True
    subpage_types = ['stories.StoryPage']


class QuoteBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(features=['bold', 'italic', 'link'])
    author = blocks.CharBlock(required=False)
    title = blocks.CharBlock(required=False)
    date = blocks.DateBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        template = 'stories/story_blocks/quote.html'
        icon = 'quote'


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    caption = blocks.CharBlock()

    class Meta:
        template = 'stories/story_blocks/image.html'
        icon = 'image'


class StoryPage(Page):
    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    @classmethod
    def content_type_id(cls):
        return ContentType.objects.get_for_model(cls).id

    objects = IndexedPageManager()
    show_in_menus_default = False
    subpage_types = []
    geographical_location = CharField(max_length=250, null=True, blank=True)
    coordinates = geo.PointField(null=True, blank=True)
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)
    description = RichTextField()

    # Streamfield of options here
    body = StreamField([
        ('text', blocks.RichTextBlock(features=[
            'h3', 'bold', 'italic', 'link', 'ol', 'ul'
        ], template='stories/story_blocks/text.html')),
        ('quote', QuoteBlock()),
        ('embed', blocks.RichTextBlock(features=[
         'embed'], template='stories/story_blocks/text.html')),
        ('image', ImageBlock()),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('tags'),
        StreamFieldPanel('body'),
        MultiFieldPanel(
            [
                FieldPanel('geographical_location'),
                FieldPanel('coordinates')
            ],
            heading="Geographical data",
        )
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

    def thumbnail_content_html(self):
        if self.thumbnail_image is None:
            return render_to_string('stories/thumbnails/story_no_image.html', {
                'self': self
            })

        return render_to_string('stories/thumbnails/story_images.html', {
            'self': self,
            'thumbnail_images': self.thumbnail_image,
        })

    def content_html(self):
        return render_to_string('stories/story.html', {
            'self': self
        })
