from urllib.parse import urlparse, parse_qs

from django.http.request import HttpRequest
from django.http.response import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from wagtail.core.models import Page
from smartforests.models import Tag
from commonknowledge.django.cache import django_cached

from smartforests.util import group_by_title


def frame_content(request, page_id):
    page = get_object_or_404(Page.objects.filter(pk=page_id).specific())
    if hasattr(page, 'get_sidebar_frame_response'):
        return page.get_sidebar_frame_response(request)
    else:
        return HttpResponseNotFound()


def filters_frame(request: HttpRequest):
    @django_cached('smartforests.views.filters_frame.get_tags')
    def get_tags():
        return group_by_title(Tag.objects.distinct(), key='name')

    return render(
        request,
        "smartforests/frames/filters.html",
        {
            'tags':  get_tags(),
            'tag_filter': request.GET.get('current')
        }
    )
