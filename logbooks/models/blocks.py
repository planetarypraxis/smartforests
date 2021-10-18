from wagtail.core import blocks
from wagtail.core.blocks.field_block import PageChooserBlock
from wagtail.core.fields import StreamField
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from commonknowledge.wagtail.search.models import StreamfieldIndexer, StructIndexer, TextIndexer


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


class ArticleContentStream(StreamField):
    text_indexer = StreamfieldIndexer(
        quote=StructIndexer(
            title=TextIndexer(),
            author=TextIndexer(),
            text=TextIndexer(),
        ),
        _default=TextIndexer(),
    )

    common_block_types = [
        ('text', blocks.RichTextBlock(features=[
            'h3', 'bold', 'italic', 'link', 'ol', 'ul'
        ], template='logbooks/story_blocks/text.html')),
        ('quote', QuoteBlock()),
        ('embed', EmbedBlock(template='logbooks/story_blocks/embed.html')),
        ('image', ImageBlock()),
    ]

    def __init__(self, block_types=None, **kwargs):
        super().__init__(self.common_block_types + (block_types or []), **kwargs)
