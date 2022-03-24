from urllib.parse import urlparse, parse_qs
from generic_chooser.views import ModelChooserViewSet, ModelChooserMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from wagtail.core.models import Page
from wagtail.core.models.i18n import Locale
from logbooks.models.pages import EpisodePage
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
        return list(set(o.localized for o in objects))


class RadioEpisodeChooserViewSet(ModelChooserViewSet):
    icon = 'audio'
    model = EpisodePage
    page_title = "Choose a radio episode"
    per_page = 10
    order_by = 'title'
    fields = ['title', 'tags']
    chooser_mixin_class = RadioEpisodeChooserViewSetMixin
