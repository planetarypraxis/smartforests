from django.shortcuts import get_object_or_404, render
from rest_framework import serializers, viewsets
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.urls import path
from wagtail.core.models import Page
from smartforests.models import Tag
from wagtail.api.v2.utils import BadRequestError

from logbooks.models.pages import EpisodePage, LogbookEntryPage, LogbookPage, StoryPage


def tag_panel(request, slug):
    tag = get_object_or_404(Tag.objects.filter(slug=slug))
    page_types = (LogbookPage, StoryPage, LogbookEntryPage)

    return render(
        request,
        'logbooks/frames/tags.html',
        {
            'tag': tag,
            'pages': (
                (
                    page_type,
                    page_type.objects.filter(
                        tagged_items__tag__slug=slug
                    )
                )
                for page_type
                in page_types
            )
        }
    )


class MapSearchViewset(viewsets.ReadOnlyModelViewSet):
    '''
    Query the page metadata index, filtering by tag, returning a geojson FeatureCollection
    '''

    class RequestSerializer(serializers.Serializer):
        tag = serializers.ListField(child=serializers.CharField(), default=())

    class ResultSerializer(GeoFeatureModelSerializer):
        class Meta:
            model = LogbookPage
            geo_field = 'coordinates'
            fields = ('id', 'link_url', 'title', 'icon_class',
                      'geographical_location', 'tags')

        coordinates = GeometrySerializerMethodField()
        id = serializers.IntegerField()
        title = serializers.CharField()
        icon_class = serializers.CharField()
        link_url = serializers.CharField()
        geographical_location = serializers.CharField()
        tags = serializers.StringRelatedField(many=True)

        def get_coordinates(self, obj):
            return getattr(obj, 'coordinates', None)

    queryset = Page.objects.live().specific().type(
        LogbookPage, LogbookEntryPage, StoryPage, EpisodePage
    )
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = MapSearchViewset.RequestSerializer(data=self.request.GET)
        if not params.is_valid():
            raise BadRequestError()

        tag = params.data.get('tag', ())

        if tag:
            tag_objects = tuple(x.id for x in Tag.objects.filter(slug__in=tag))
            if tag_objects:
                qs = qs.filter(tagged_items__tag_id__in=tag_objects)
            else:
                qs = qs.none()

        return qs

    @classmethod
    def get_urlpatterns(cls):
        return [
            path('', cls.as_view({'get': 'list'}), name='geo.search'),
        ]
