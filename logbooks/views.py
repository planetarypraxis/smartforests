from typing import List, Union
from django.apps import apps
from django.shortcuts import get_list_or_404, get_object_or_404, render
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from django.urls import path
from wagtail.admin.views.pages import history
from wagtail.models import Page
from wagtail.models.i18n import Locale
from smartforests.models import Tag, User
from wagtail.api.v2.utils import BadRequestError
from commonknowledge.helpers import ensure_list

from logbooks.models.pages import (
    ContributorPage,
    EpisodePage,
    LogbookEntryPage,
    LogbookPage,
    StoryPage,
)
from smartforests.views import LocaleFromLanguageCode
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


content_list_types = (
    LogbookPage,
    StoryPage,
    EpisodePage,
)
tag_panel_types = content_list_types + (ContributorPage,)


def pages_for_tag(tag: Tag, page_types=tag_panel_types):
    current_locale = Locale.get_active()
    # Expand the list of tags to include all localized versions
    #
    # This is necessary because pages can either be:
    # 1. Translated versions of original pages
    # 2. Original pages themselves
    #
    # In the first case, the translated pages will be tagged with
    # the original tag (not the translated tag).
    # In the second case, the translated pages will be tagged with
    # the translated tag.
    all_tags = Tag.objects.filter(translation_key=tag.translation_key)
    page_lists_by_type = [
        (page_type, page_type.for_tag(list(all_tags), locale=current_locale))
        for page_type in page_types
        if page_type != ContributorPage
    ]

    if ContributorPage in page_types:
        contributors = set()
        for page_type, pages in page_lists_by_type:
            for page in pages:
                contributors = contributors.union(page.real_contributors)
        page_lists_by_type.append(
            (
                ContributorPage,
                ContributorPage.objects.live().filter(
                    user__in=contributors, locale=current_locale
                ),
            )
        )

    return [
        (
            page_type,
            list(
                sorted(
                    page_list,
                    key=lambda p: p.title,
                )
            ),
        )
        for (page_type, page_list) in page_lists_by_type
        if page_list
    ]


def get_localized_title_for_page_type(page_type):
    """
    Return the title of the parent page for the page type, if it exists.
    Default to the verbose_name_plural of the model.
    """

    default = page_type.model_info().verbose_name_plural

    if not page_type.parent_page_types:
        return default

    parent_page_type = page_type.parent_page_types[0]
    [parent_page_app, parent_page_model_name] = parent_page_type.split(".")
    parent_page_model = apps.get_model(
        app_label=parent_page_app, model_name=parent_page_model_name
    )
    parent_page = parent_page_model.objects.first()
    if not parent_page:
        return default

    return parent_page.localized.title


def tag_panel(request, slug):
    locale = Locale.get_active()
    tags = Tag.objects.filter(slug=slug, locale=locale)

    pages = []

    for tag in tags:
        pages = pages + [
            (page_type, get_localized_title_for_page_type(page_type), page_list)
            for (page_type, page_list) in pages_for_tag(tag, tag_panel_types)
        ]

    if "Turbo-Frame" in request.headers:
        return render(
            request, "logbooks/frames/tags.html", {"tag": tag, "pages": pages}
        )
    else:
        # If not a turbo frame, we need to render it with page chrome
        return render(
            request,
            "logbooks/standalone-views/tags.html",
            {"tag": tag, "pages": pages},
        )


def metadata(request, page_id, **kwargs):
    page = get_object_or_404(Page.objects.filter(id=page_id).specific())

    user_id = kwargs.get("user_id", None)
    if user_id:
        user = User.objects.get(id=user_id)
        if user in page.additional_contributors.all():
            page.additional_contributors.remove(user)
        elif user in page.excluded_contributors.all():
            page.excluded_contributors.remove(user)
        else:
            page.excluded_contributors.add(user)
        page.save()

    return render(
        request,
        "logbooks/frames/metadata.html",
        {"page": page, "interactive": request.user.is_authenticated, "mobile": request.GET.get("mobile", False)},
    )


def page_tagcloud(request, page_id):
    page = get_object_or_404(Page.objects.filter(id=page_id).specific())
    return render(
        request,
        "logbooks/frames/page_tagcloud.html",
        {"page": page},
    )


class MapSearchViewset(viewsets.ReadOnlyModelViewSet, LocaleFromLanguageCode):
    """
    Query the page metadata index, filtering by tag, returning a geojson FeatureCollection
    """

    page_types = (
        LogbookPage,
        LogbookEntryPage,
        StoryPage,
        EpisodePage,
    )

    class RequestSerializer(serializers.Serializer):
        tag = serializers.ListField(child=serializers.CharField(), default=())
        language_code = serializers.CharField(default="en")

    class ResultSerializer(GeoFeatureModelSerializer):
        class Meta:
            model = LogbookPage
            geo_field = "coordinates"
            fields = (
                "id",
                "link_url",
                "title",
                "icon_class",
                "geographical_location",
                "tags",
                "page_type",
            )

        coordinates = GeometrySerializerMethodField()
        id = serializers.IntegerField()
        title = serializers.CharField()
        icon_class = serializers.CharField()
        link_url = serializers.CharField()
        page_type = serializers.CharField()
        geographical_location = serializers.CharField()
        tags = serializers.StringRelatedField(many=True)

        def get_coordinates(self, obj):
            return getattr(obj, "coordinates", None)

    model = Page
    serializer_class = ResultSerializer

    def get_queryset(self):
        locale = Locale.get_active()
        params = MapSearchViewset.RequestSerializer(data=self.request.GET)
        if not params.is_valid():
            raise BadRequestError()

        tag = params.data.get("tag", ())

        if tag:
            tag_ids = Tag.get_translated_tag_ids(tag)

            if tag_ids:
                tagged_pages = []
                for PageClass in self.page_types:
                    tagged_pages += PageClass.for_tag(tag_ids, locale=locale)
                return tagged_pages

        # If no filters, return all possible geo pages
        return (
            Page.objects.live().filter(locale=locale).specific().type(*self.page_types)
        )

    @extend_schema(parameters=[RequestSerializer])
    def list(self, request):
        pages = self.get_queryset()
        return Response(self.ResultSerializer(pages, many=True).data)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "list"}), name="geo.search"),
        ]


class PageHistoryView(history.PageHistoryView):
    template_name = "logbooks/wagtailadmin/pages/history.html"
