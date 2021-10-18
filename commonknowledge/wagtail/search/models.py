from django.db import models
from wagtail.core.models import Page
from wagtail.search import index
from wagtail.core.blocks.stream_block import StreamBlock, StreamValue
from wagtail.core.blocks.struct_block import StructValue
from wagtail.core.rich_text import RichText, get_text_for_indexing

from commonknowledge.helpers import get_path


class StreamfieldIndexer:
    def __init__(self, **handlers):
        self.handlers = handlers

    def handle(self, content):
        if not isinstance(content, StreamValue):
            return []

        default_handler = self.handlers.get('_default')

        result = []
        for block in content:
            handler = self.handlers.get(block.block_type, default_handler)
            if handler:
                result += list(handler.handle(block.value))

        return result


class StructIndexer:
    def __init__(self, **handlers):
        self.handlers = handlers

    def handle(self, content):
        if not isinstance(content, StructValue):
            return []

        result = []

        for key, handler in self.handlers.items():
            value = content.get(key)
            if value:
                result += list(handler.handle(value))

        return result


class TextIndexer:
    def handle(self, content):
        if isinstance(content, RichText):
            return [get_text_for_indexing(content.source)]
        if isinstance(content, str):
            return [content]

        return []


class IndexedStreamfieldMixin(Page):
    '''
    Mixin for a wagtail page that indexes its streamfield content on save.

    By default, will index every text or rich text block in a `body` or `content` attribute.
    Override indexed_streamfield_attrs to index different attrs.

    Customize how a streamfield's contents are indexed by by overriding `streamfield_indexer`
    with an Indexer object (implementing a method `handle(self, value): list(str)`)
    '''

    SUBCLASSES = []

    class Meta:
        abstract = True

    indexed_streamfield_text = models.TextField(default='', blank=True)
    indexed_streamfield_attrs = ('body', 'content')

    search_fields = [index.SearchField('indexed_streamfield_text')]

    @ classmethod
    def reindex_all(cls):
        for subclass in IndexedStreamfieldMixin.SUBCLASSES:
            if issubclass(subclass, cls):
                subclass.reindex_streamfields()

    @ classmethod
    def reindex_streamfields(cls):
        for instance in cls.objects.all():
            instance.save()

    @ classmethod
    def __init_subclass__(cls):
        if cls != IndexedStreamfieldMixin:
            IndexedStreamfieldMixin.SUBCLASSES.append(cls)

        return super().__init_subclass__()

    def save(self, *args, **kwargs):
        sources = (
            s
            for attr in self.indexed_streamfield_attrs
            for s in self.streamfield_indexer.handle(getattr(self, attr, None))
        )

        self.indexed_streamfield_text = '\n'.join(sources)

        return super().save(*args, **kwargs)

    streamfield_indexer = StreamfieldIndexer(
        _default=TextIndexer()
    )
