from wagtail.core import blocks
from wagtail.core.blocks.field_block import PageChooserBlock
from wagtail.core.fields import StreamField
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail_footnotes.blocks import RichTextBlockWithFootnotes

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

    def get_api_representation(self, value, context=None):
        print("QuoteBlock", value)
        return super().get_api_representation(value, context)


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    caption = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'code', 'blockquote'])

    class Meta:
        template = 'logbooks/story_blocks/image.html'
        icon = 'image'

    def get_api_representation(self, value, context=None):
        print("ImageBlock", value)
        return super().get_api_representation(value, context)


def ArticleContentStream(block_types=None, **kwargs):
    common_block_types = [
        ('text', RichTextBlockWithFootnotes(features=[
            'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes',
        ], template='logbooks/story_blocks/text.html')),
        ('quote', QuoteBlock()),
        ('embed', EmbedBlock(template='logbooks/story_blocks/embed.html')),
        ('image', ImageBlock()),
    ]

    return StreamField(common_block_types + (block_types or []), **kwargs)


ArticleContentStream.text_indexer = StreamfieldIndexer(
    quote=StructIndexer(
        title=TextIndexer(),
        author=TextIndexer(),
        text=TextIndexer(),
    ),
    _default=TextIndexer(),
)
