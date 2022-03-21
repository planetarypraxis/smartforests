from django.shortcuts import get_object_or_404, render
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.urls import path
from wagtail.core.models import Page
from wagtail.core.models.i18n import Locale
from logbooks.models.mixins import Person
from smartforests.models import Tag, User
from wagtail.api.v2.utils import BadRequestError

from logbooks.models.pages import ContributorPage, EpisodePage, LogbookEntryPage, LogbookPage, StoryPage
from smartforests.views import LocaleFromLanguageCode
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


tag_panel_types = (LogbookPage, StoryPage, EpisodePage, ContributorPage,)


def pages_for_tag(tag: Tag, page_types=tag_panel_types):
    return [
        (
            page_type,
            set(map(lambda p: p.localized, page_type.for_tag(tag)))
        )
        for page_type
        in page_types
    ]


def tag_panel(request, slug):
    tag = get_object_or_404(Tag.objects.filter(slug=slug))

    return render(
        request,
        'logbooks/frames/tags.html',
        {
            'tag': tag,
            'pages': pages_for_tag(tag, tag_panel_types)
        }
    )



def metadata(request, page_id, **kwargs):
    page = get_object_or_404(Page.objects.filter(id=page_id).specific())

    user_id = kwargs.get('user_id', None)
    class_name = kwargs.get('class_name', None)
    if user_id:
        if class_name == 'User':
            user = User.objects.get(id=user_id)
            page.additional_contributing_users.remove(user)
            page.excluded_contributors.add(user)
        else:
            person = Person.objects.get(id=user_id)
            page.additional_contributing_people.remove(person)
        page.save()

    return render(
        request,
        'logbooks/frames/metadata.html',
        {
            'page': page,
            'interactive': request.user.is_authenticated
        }
    )


class MapSearchViewset(viewsets.ReadOnlyModelViewSet, LocaleFromLanguageCode):
    '''
    Query the page metadata index, filtering by tag, returning a geojson FeatureCollection
    '''

    page_types = (LogbookPage, LogbookEntryPage, StoryPage, EpisodePage,)

    class RequestSerializer(serializers.Serializer):
        tag = serializers.ListField(child=serializers.CharField(), default=())
        language_code = serializers.CharField(default='en')

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

    model = Page
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = Page.objects.live().specific().type(*self.page_types)
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

    @extend_schema(parameters=[RequestSerializer])
    def list(self, request):
        list = self.get_queryset()
        locale = self.get_locale()
        localized_pages = set([page.get_translation_or_none(
            locale) or page for page in list])
        return Response(self.ResultSerializer(localized_pages, many=True).data)

    def get_object(self, request):
        page = self.get_queryset()
        locale = self.get_locale()
        localized_page = page.get_translation_or_none(locale) or page
        return Response(self.ResultSerializer(localized_page).data)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path('', cls.as_view({'get': 'list'}), name='geo.search'),
        ]
