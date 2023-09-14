# Public REST API to share access to Atlas content
# primarily for use by interactive components of the Atlas website

from drf_spectacular.utils import extend_schema
from smartforests.views import LocaleFromLanguageCode
from logbooks.models.pages import EpisodePage, LogbookEntryPage, LogbookPage, StoryPage
from wagtail.api.v2.serializers import PageSerializer, get_serializer_class
from wagtail.api.v2.utils import BadRequestError
from smartforests.models import Tag
from rest_framework.response import Response
from rest_framework import serializers, viewsets
from django.urls import path
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from smartforests.models import Tag
from logbooks.models.pages import LogbookPage
from wagtail.core.models import Page
from collections import OrderedDict

# Create the router. "wagtailapi" is the URL namespace
wagtail_api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
wagtail_api_router.register_endpoint('pages', PagesAPIViewSet)
wagtail_api_router.register_endpoint('images', ImagesAPIViewSet)
wagtail_api_router.register_endpoint('documents', DocumentsAPIViewSet)


def preprocessing_hooks(endpoints):
    # your modifications to the list of operations that are exposed in the schema
    new_endpoints = []
    for (path, path_regex, method, callback) in endpoints:
        # If path starts with /api/v2 then add it to new_endpoints
        if path.startswith('/api/v2'):
            new_endpoints.append((path, path_regex, method, callback))
    return new_endpoints

#####
# This would be the ideal solution
# but for some reason it doesn't work.
#
# class PageTagFilter(BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         if 'tag_slugs' in request.GET:
#             tag_slugs = str(request.GET['tag_slugs']).split(",")
#             if len(tag_slugs) > 0:
#                 tags = Tag.objects.filter(
#                     slug__in=tag_slugs)
#                 tag_ids = [t.pk for t in Tag.objects.filter(
#                     slug__in=tag_slugs)]
#                 # queryset = queryset.filter(tags__pk__in=tag_ids)
#                 queryset = queryset.filter(abstract_page_query_filter(
#                     ArticlePage, {'tags__in': tags}))
#         return queryset
#
# class PagesAPIViewset(BasePagesAPIViewSet):
#     filter_backends = PagesAPIViewSet.filter_backends + [PageTagFilter]
#     known_query_parameters = list(
#         PagesAPIViewSet.known_query_parameters) + ['tag_slugs']
####


class TaggedPagesViewset(viewsets.ReadOnlyModelViewSet, LocaleFromLanguageCode):
    model = Page
    serializer_class = get_serializer_class(
        Page,
        [
            "id",
            "type",
            "detail_url",
            "html_url",
            "locale",
            "title",
            "last_published_at"
        ],
        meta_fields=["type", "detail_url", "html_url", "locale"],
        base=PageSerializer,
    )
    page_types = (LogbookPage, LogbookEntryPage, StoryPage, EpisodePage,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_types = OrderedDict()

    class RequestSerializer(serializers.Serializer):
        tag = serializers.ListField(child=serializers.CharField(), default=())
        language_code = serializers.CharField(default='en')

    def get_serializer_context(self):
        """
        The serialization context differs between listing and detail views.
        """
        return {
            'request': self.request,
            'view': self,
            'router': self.request.wagtailapi_router
        }

    def get_queryset(self):
        tagged_queryset = self.get_queryset_with_tags()
        if tagged_queryset:
            return tagged_queryset
        # If no filters, return all possible pages
        return Page.objects.live().public().specific().type(*self.page_types)

    def get_queryset_with_tags(self):
        params = TaggedPagesViewset.RequestSerializer(data=self.request.GET)
        if not params.is_valid():
            raise BadRequestError()

        tag = params.data.get('tag', ())

        if tag:
            tag_ids = Tag.get_translated_tag_ids(tag)

            if tag_ids:
                tagged_pages = []
                for PageClass in self.page_types:
                    tagged_pages += PageClass.for_tag(tag_ids)
                return tagged_pages

    @extend_schema(parameters=[RequestSerializer])
    def list(self, request):
        pages = self.get_queryset()
        locale = self.get_locale()
        localized_pages = set()
        for page in pages:
            localized_page = page.get_translation_or_none(locale)
            # Show the localized page if it exists
            if localized_page:
                localized_pages.add(localized_page)
            # Otherwise show this page if it is an original, not an auto-created dummy translation
            elif not page.alias_of:
                localized_pages.add(page)
        return Response(self.serializer_class(localized_pages, many=True, context=self.get_serializer_context()).data)

    def get_object(self, request):
        page = self.get_queryset()
        locale = self.get_locale()
        localized_page = page.get_translation_or_none(locale) or page
        return Response(self.serializer_class(context=self.get_serializer_context()).to_representation(localized_page).data)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path('', cls.as_view({'get': 'list'}), name='tag.search'),
        ]


wagtail_api_router.register_endpoint('tagged-pages', TaggedPagesViewset)
