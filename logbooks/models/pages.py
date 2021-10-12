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


class QuoteBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(features=['bold', 'italic', 'link'])
    author = blocks.CharBlock(required=False)
    title = blocks.CharBlock(required=False)
    date = blocks.DateBlock(required=False)
    link = blocks.URLBlock(required=False)

    class Meta:
        template = 'logbooks/entry_blocks/quote.html'
        icon = 'quote'


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    caption = blocks.CharBlock()

    class Meta:
        template = 'logbooks/entry_blocks/image.html'
        icon = 'image'


class LogbookIndexPage(ChildListMixin, Page):
    page_size = 50
    show_in_menus_default = True
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

        return LogbookPageIndex.filter_pages(
            **filter, content_type=LogbookPage.content_type_id()).specific()

    @django_cached_model('logbooks.LogbookIndexPage.relevant_tags')
    def relevant_tags(self):
        return group_by_title(Tag.objects.filter(smartforests_atlastag_items__isnull=False).distinct(), key='name')

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['tag_filter'] = request.GET.get('filter', None)

        return context


class LogbookPage(Page):
    @classmethod
    def content_type_id(cls):
        return ContentType.objects.get_for_model(cls).id

    objects = IndexedPageManager()
    show_in_menus_default = True
    subpage_types = ['logbooks.LogbookEntryPage']
    description = RichTextField()
    tags = ClusterTaggableManager(through=AtlasTag, blank=True)

    geographical_location = CharField(max_length=250, null=True, blank=True)
    coordinates = geo.PointField(null=True, blank=True)

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('description'),
        FieldPanel('tags'),
        MultiFieldPanel(
            [
                FieldPanel('geographical_location'),
                FieldPanel('coordinates')
            ],
            heading="Geographical data",
        ),
    ]

    @property
    def thumbnail_image(self):
        if self.index_entry and self.index_entry.thumbnail_image:
            return self.index_entry.thumbnail_image

    def regenerate_thumbnail(self, index_data):
        entries = self.get_children().specific()

        images = tuple(
            x.cover_image() for x in entries if x.cover_image() is not None)

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


class LogbookEntryPage(Page):
    class Meta:
        verbose_name = "Logbook Entry"
        verbose_name_plural = "Logbook Entries"

    @classmethod
    def content_type_id(cls):
        return ContentType.objects.get_for_model(cls).id

    objects = IndexedPageManager()
    show_in_menus_default = False
    subpage_types = []
    geographical_location = CharField(max_length=250, null=True, blank=True)
    coordinates = geo.PointField(null=True, blank=True)

    # Streamfield of options here
    body = StreamField([
        ('text', blocks.RichTextBlock(features=[
            'h3', 'bold', 'italic', 'link', 'ol', 'ul'
        ], template='logbooks/entry_blocks/text.html')),
        ('quote', QuoteBlock()),
        ('embed', blocks.RichTextBlock(features=[
         'embed'], template='logbooks/entry_blocks/text.html')),
        ('image', ImageBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        MultiFieldPanel(
            [
                FieldPanel('geographical_location'),
                FieldPanel('coordinates')
            ],
            heading="Geographical data",
        ),
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
            return render_to_string('logbooks/thumbnails/story_no_image.html', {
                'self': self
            })

        return render_to_string('logbooks/thumbnails/story_images.html', {
            'self': self,
            'thumbnail_images': self.thumbnail_image,
        })

    def content_html(self):
        print(self.title)
        return render_to_string('logbooks/logbook_entry.html', {
            'self': self
        })
