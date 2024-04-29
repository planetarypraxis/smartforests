from commonknowledge.django.cache import django_cached
from home.models import HomePage
from logbooks.models.pages import (
    ContributorsIndexPage,
    LogbookIndexPage,
    RadioHomePage,
    StoryIndexPage,
)
from smartforests.models import MapPage


class ImportantPagesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data["homepage"] = HomePage.objects.first()
            response.context_data["important_pages"] = (
                ImportantPagesMiddleware.get_menu_items()
            )

        return response

    @classmethod
    def get_menu_items(self):
        return {
            "home": HomePage.objects.first(),
            "contributors": ContributorsIndexPage.objects.first(),
            "map": MapPage.objects.first(),
            "logbooks": LogbookIndexPage.objects.first(),
            "stories": StoryIndexPage.objects.first(),
            "radio": RadioHomePage.objects.first(),
        }
