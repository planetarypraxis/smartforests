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


def important_pages(request):
    locale = Locale.get_active()
    
    menu_items = get_menu_items(locale)

    return {
        "homepage": HomePage.objects.filter(locale=locale).first(),
        "important_pages": menu_items,
    }

def get_menu_items(locale):
    return {
        "home": HomePage.objects.filter(locale=locale).first(),
        "contributors": ContributorsIndexPage.objects.filter(locale=locale).first(),
        "map": MapPage.objects.filter(locale=locale).first(),
        "logbooks": LogbookIndexPage.objects.filter(locale=locale).first(),
        "stories": StoryIndexPage.objects.filter(locale=locale).first(),
        "radio": RadioIndexPage.objects.filter(locale=locale).first(),
    }
