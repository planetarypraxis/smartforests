from django.http.request import HttpRequest
from django.http.response import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from wagtail.core.models import Page


def frame_content(request, page_id):
    page = get_object_or_404(Page.objects.filter(pk=page_id).specific())
    if hasattr(page, 'get_sidebar_frame_response'):
        return page.get_sidebar_frame_response(request)
    else:
        return HttpResponseNotFound()
