from wagtail import blocks
from wagtail.blocks.field_block import PageChooserBlock
from wagtail.fields import StreamField
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail_footnotes.blocks import RichTextBlockWithFootnotes
from wagtail.rich_text import expand_db_html

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
        return {
            "text": expand_db_html(str(value['text'])) if value['text'] is not None else None,
            "author": value['author'],
            "title": value['title'],
            "date": value['date'],
            "link": value['link'],
        }


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    caption = blocks.RichTextBlock(
        features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'code', 'blockquote'])

    class Meta:
        template = 'logbooks/story_blocks/image.html'
        icon = 'image'

    def get_api_representation(self, value, context=None):
        return {
            "image": {
                "id": value['image'].get_api_representation()
            },
            "caption": expand_db_html(str(value['caption'])) if value['caption'] is not None else None,
        }


def ArticleContentStream(block_types=None, **kwargs):
    common_block_types = [
        ('text', RichTextBlockWithFootnotes(features=[
            'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes',
        ], template='logbooks/story_blocks/text.html')),
        ('quote', QuoteBlock()),
        ('embed', EmbedBlock(template='logbooks/story_blocks/embed.html')),
        ('image', ImageBlock()),
    ]

    return StreamField(common_block_types + (block_types or []), use_json_field=True, **kwargs)


ArticleContentStream.text_indexer = StreamfieldIndexer(
    quote=StructIndexer(
        title=TextIndexer(),
        author=TextIndexer(),
        text=TextIndexer(),
    ),
    _default=TextIndexer(),
)
