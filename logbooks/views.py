from django.shortcuts import get_object_or_404, render
from rest_framework import serializers, viewsets
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.urls import path
from taggit.models import Tag
from wagtail.api.v2.utils import BadRequestError
from logbooks.models.pages import LogbookEntryPage, LogbookPage, StoryPage

from logbooks.models.snippets import AtlasTag

from .models import LogbookPageIndex


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
        class PageSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            link_url = serializers.CharField()
            title = serializers.CharField()
            icon_class = serializers.CharField()
            geographical_location = serializers.CharField()
            tags = serializers.StringRelatedField(many=True)

            def to_representation(self, instance):
                # Cast to the specific page class
                return super().to_representation(instance.specific)

        class Meta:
            model = LogbookPageIndex
            geo_field = 'coordinates'
            fields = ('page',)

        coordinates = GeometrySerializerMethodField()
        page = PageSerializer()

        def get_coordinates(self, obj: LogbookPageIndex):
            page = obj.page.specific
            if hasattr(page, 'coordinates'):
                return page.coordinates

    queryset = LogbookPageIndex.objects.all().select_related('page')
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = MapSearchViewset.RequestSerializer(data=self.request.GET)
        if not params.is_valid():
            raise BadRequestError()

        tag = params.data.get('tag', ())
        content_type = params.data.get('type', ())

        if tag:
            tag_objects = tuple(x.id for x in Tag.objects.filter(slug__in=tag))
            if tag_objects:
                qs = qs.filter(metadata__tags__contains=tag_objects)
            else:
                qs = qs.none()

        return qs

    @classmethod
    def get_urlpatterns(cls):
        return [
            path('', cls.as_view({'get': 'list'}), name='geo.search'),
        ]
