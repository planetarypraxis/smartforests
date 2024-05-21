from commonknowledge.django.cache import django_cached
from home.models import HomePage
from logbooks.models.pages import (
    ContributorsIndexPage,
    LogbookIndexPage,
    RadioIndexPage,
    StoryIndexPage,
)
from smartforests.models import MapPage
from wagtail.models import Locale


class ImportantPagesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):
        locale = Locale.get_active()
        if response.context_data:
            response.context_data["homepage"] = HomePage.objects.filter(
                locale=locale
            ).first()
            response.context_data["important_pages"] = (
                ImportantPagesMiddleware.get_menu_items(locale)
            )

        return response

    @classmethod
    def get_menu_items(self, locale):
        return {
            "home": HomePage.objects.filter(locale=locale).first(),
            "contributors": ContributorsIndexPage.objects.filter(locale=locale).first(),
            "map": MapPage.objects.filter(locale=locale).first(),
            "logbooks": LogbookIndexPage.objects.filter(locale=locale).first(),
            "stories": StoryIndexPage.objects.filter(locale=locale).first(),
            "radio": RadioIndexPage.objects.filter(locale=locale).first(),
        }
