import json
from urllib.parse import urlparse, parse_qs
from generic_chooser.views import ModelChooserViewSet, ModelChooserMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from wagtail.models import Page
from wagtail.models.i18n import Locale
from logbooks.models.pages import EpisodePage
from smartforests.models import Tag
from commonknowledge.django.cache import django_cached

from smartforests.util import group_by_tag_name


def frame_content(request, page_id):
    page = get_object_or_404(Page.objects.filter(pk=page_id).specific())
    if hasattr(page, 'get_sidebar_frame_response'):
        return page.get_sidebar_frame_response(request)
    else:
        return HttpResponseNotFound()


def filters_frame(request: HttpRequest):
    cache_key = 'smartforests.views.filters_frame.get_tags.' + \
        Locale.get_active().language_code

    @django_cached(cache_key)
    def get_tags():
        return group_by_tag_name(Tag.objects.distinct())

    return render(
        request,
        "smartforests/frames/filters.html",
        {
            'tags':  get_tags(),
            'tag_filter': request.GET.get('current')
        }
    )


def tag_autocomplete_view(request: HttpRequest):
    search = request.GET.get("term", "")
    locale = request.GET.get("locale")
    tags = Tag.objects.filter(name__istartswith=search)
    if locale:
        tags = tags.filter(locale__language_code=locale)
    tags = tags.order_by("name")
    suggestions = set(tag.name for tag in tags[:10])
    suggestions = sorted(list(suggestions))
    return HttpResponse(json.dumps(suggestions), content_type='application/json; charset=utf8')


def smoke_view(request: HttpRequest):
    return HttpResponse("OK")

from wagtail.models import Site

def smoke_site_view(request: HttpRequest):
        # we need a valid Site object corresponding to this request in order to proceed
    site = Site.find_for_request(request)
    return HttpResponse(f"{site}")


def smoke_home_view(request: HttpRequest):
    page = Page.objects.filter(id=3).specific().first()
    return page.serve(request)


def smoke_about_view(request: HttpRequest):
    page = Page.objects.filter(id=208).specific().first()
    return page.serve(request)


class LocaleFromLanguageCode:
    '''
    Can be used for API requests and so on.
    '''

    def get_locale(self):
        language_code = self.request.GET.get('language_code', 'en')
        try:
            locale = Locale.objects.get(language_code=language_code)
            return locale
        except:
            try:
                # E.g. for en-gb, try en
                locale = Locale.objects.get(
                    language_code="-".split(language_code)[0])
                return locale
            except:
                return Locale.objects.get(language_code='en')


class RadioEpisodeChooserViewSetMixin(ModelChooserMixin):
    def get_unfiltered_object_list(self):
        objects = super().get_unfiltered_object_list()
        locale = Locale.get_active()
        if locale:
            objects = objects.filter(locale=locale)
        return objects


class RadioEpisodeChooserViewSet(ModelChooserViewSet):
    icon = 'audio'
    model = EpisodePage
    page_title = "Choose a radio episode"
    per_page = 10
    order_by = 'title'
    fields = ['title', 'tags']
    chooser_mixin_class = RadioEpisodeChooserViewSetMixin
