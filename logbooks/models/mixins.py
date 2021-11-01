from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http.response import HttpResponseNotFound
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.api.conf import APIField
from wagtail.core.models import Page, PageManager, PageRevision
from django.contrib.gis.db import models as geo
from commonknowledge.wagtail.search.models import IndexedStreamfieldMixin
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.nlp.tokenizers import Tokenizer
from turbo_response import TurboFrame

from logbooks.models.blocks import ArticleContentStream
from logbooks.models.serializers import PageCoordinatesSerializer, UserSerializer
from logbooks.models.snippets import AtlasTag
from logbooks.thumbnail import generate_thumbnail


class IndexedPageManager(PageManager):
    '''
    Optimization for pages that use the page index. Fetches their index_entry attribute eagerly in queries.
    '''

    def get_queryset(self):
        return super().get_queryset().select_related('index_entry')


class BaseLogbooksPage(Page):
    '''
    Common utilities for pages in this module
    '''

    class Meta:
        abstract = True

    @classmethod
    def content_type_id(cls):
        return ContentType.objects.get_for_model(cls).id

    @property
    def link_url(self):
        '''
        Wrapper for url allowing us to link to a page embedded in a parent (as with logbook entries) without
        overriding any wagtail internals

        '''

        return self.url


class ContributorMixin(Page):
    '''
    Common configuration for pages that want to track their contributors.
    '''

    class Meta:
        abstract = True

    def contributors(self):
        '''
        Return all the people who have contributed to this page
        '''
        return list(set([
            revision.user
            for revision in PageRevision.objects.filter(page=self)
        ] + [self.owner]))

    api_fields = [
        APIField('contributors', serializer=UserSerializer(many=True)),
    ]

    content_panels = []


class DescendantPageContributorMixin(Page):
    '''
    Common configuration for pages that want to track their contributors.
    '''

    class Meta:
        abstract = True

    def contributors(self):
        '''
        Return all the people who have contributed to this page,
        and any descendant pages too.
        '''
        pages = self.get_descendants(inclusive=True)
        return list(set([
            revision.user
            for revision in PageRevision.objects.filter(page__in=pages)
        ]))

    api_fields = [
        APIField('contributors', serializer=UserSerializer(many=True)),
    ]

    content_panels = []


class GeocodedMixin(Page):
    '''
    Common configuration for pages that want to track a geographical location.
    '''

    class Meta:
        abstract = True
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    geographical_location = models.CharField(
        max_length=250, null=True, blank=True)
    coordinates = geo.PointField(null=True, blank=True)

    @property
    def longitude(self):
        if self.coordinates:
            return self.coordinates.coords[0]

    @property
    def latitude(self):
        if self.coordinates:
            return self.coordinates.coords[1]

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('geographical_location'),
                FieldPanel('coordinates')
            ],
            heading="Geographical data",
        )
    ]

    @classmethod
    def label(self):
        return self._meta.verbose_name

    api_fields = [
        APIField('label'),
        APIField('geographical_location'),
        APIField('coordinates', serializer=PageCoordinatesSerializer)
    ]


class ThumbnailMixin(Page):
    '''
    Common configuration for pages that want to generate a thumbnail image derived from a subclass-defined list of images.
    '''

    class Meta:
        abstract = True

    def get_thumbnail_images(self):
        return []

    @property
    def thumbnail_image(self):
        if self.index_entry and self.index_entry.thumbnail_image:
            return self.index_entry.thumbnail_image

    def get_thumbnail_slug(self):
        return f'{self._meta.model_name}thumbnail_{self.slug}'

    def regenerate_thumbnail(self):
        images = self.get_thumbnail_images()
        return generate_thumbnail(images, fileslug=self.get_thumbnail_slug())

    def card_content_html(self):
        '''
        Return markup to render the summary of this page when embedded in a list
        '''
        return render_to_string('logbooks/thumbnails/basic_thumbnail.html', {
            'self': self
        })


class SidebarRenderableMixin:
    def get_sidebar_frame_response(self, request, *args, **kwargs):
        '''
        Render the sidebar frame's html.
        '''

        context = self.get_context(request)
        return TemplateResponse(request, 'logbooks/content_entry/sidepanel.html', context)


class ArticlePage(IndexedStreamfieldMixin, ContributorMixin, ThumbnailMixin, GeocodedMixin, SidebarRenderableMixin, BaseLogbooksPage):
    '''
    Common configuration for logbook entries, stories and radio episodes.
    '''
    class Meta:
        abstract = True

    objects = IndexedPageManager()

    tags = ClusterTaggableManager(through=AtlasTag, blank=True)
    body = ArticleContentStream()

    content_panels = Page.content_panels + [
        FieldPanel('tags'),
        StreamFieldPanel('body'),
        InlinePanel("footnotes", label="Footnotes"),
    ] + ContributorMixin.content_panels + GeocodedMixin.content_panels

    api_fields = [
        APIField('tags'),
        APIField('icon_class'),
    ] + ContributorMixin.api_fields + GeocodedMixin.api_fields

    search_fields = IndexedStreamfieldMixin.search_fields + Page.search_fields
    streamfield_indexer = ArticleContentStream.text_indexer

    def body_images(self):
        '''
        Return all the images in this page's body stream.
        '''

        return tuple(
            block.value.get('image')
            for block in self.body
            if block.block_type == 'image'
            and block.value.get('image')
        )

    def cover_image(self):
        '''
        Returns the first image in the body stream (or None if there aren't any).

        Used to determine which image to contribute to a thumbnail when images from multiple pages are combined into a single thumbnail (as with logbooks)
        '''

        images = self.body_images()
        return None if len(images) == 0 else images[0]

    def get_thumbnail_images(self):
        return self.body_images()

    @property
    def thumbnail_image(self):
        '''
        Return this page's pre-generated thumbnail image.
        '''

        if self.index_entry and self.index_entry.thumbnail_image:
            return self.index_entry.thumbnail_image

    @property
    def preview_text(self):
        language = 'english'

        parser = PlaintextParser.from_string(
            self.indexed_streamfield_text, Tokenizer(language))
        stemmer = Stemmer(language)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        summary = ' '.join(
            str(x)
            for x in summarizer(parser.document, 2)
            if str(x).strip() != ''
        )

        if summary:
            return summary
        else:
            return self.indexed_streamfield_text


class TurboFrameMixin(RoutablePageMixin, Page):
    class Meta:
        abstract = True

    @route('^frame/(?P<dom_id>[-\w_]+)/(?P<template_path>.+)$')
    def turbo_frame_response(self, request, dom_id, template_path, *args, **kwargs):
        return TurboFrame(dom_id).template(f'{template_path.replace("-", "/").strip("/")}.html', {"page": self}).response(request)
