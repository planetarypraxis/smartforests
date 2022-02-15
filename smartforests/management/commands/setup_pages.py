from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from wagtail.core.models import Page, Site

from home.models import HomePage
from logbooks.models.pages import ContributorsIndexPage, LogbookIndexPage, RadioIndexPage, StoryIndexPage
from smartforests.models import MapPage


class Command(BaseCommand):
    help = 'Set up basic pages'

    def add_arguments(self, parser):
        parser.add_argument('-H', '--host', dest='host',
                            type=str, default="localhost")
        parser.add_argument('-p', '--port', dest='port',
                            type=int, default=8000)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            site = Site.objects\
                .get(
                    root_page__content_type=ContentType.objects.get_for_model(
                        HomePage),
                    root_page__locale_id=1
                )
            home = site.root_page
            print("Site and homepage already set up", site, home)
        except:
            home = HomePage(
                title="Smart Forests Atlas",
                slug="smartforests",
            )
            root = Page.get_first_root_node()
            root.add_child(instance=home)

            site = Site.objects.get_or_create(
                hostname=options.get('host'),
                port=options.get('port'),
                is_default_site=True,
                site_name="Smart Forests Atlas",
                root_page=home,
            )

        # Set up website sections
        slug = "stories"
        if StoryIndexPage.objects.filter(slug=slug).descendant_of(home).exists() is False:
            stories = StoryIndexPage(
                title="stories",
                slug=slug
            )
            home.add_child(instance=stories)

        slug = "logbooks"
        if LogbookIndexPage.objects.filter(slug=slug).descendant_of(home).exists() is False:
            logbooks = LogbookIndexPage(
                title="logbooks",
                slug=slug
            )
            home.add_child(instance=logbooks)

        slug = "contributors"
        if ContributorsIndexPage.objects.filter(slug=slug).descendant_of(home).exists() is False:
            contributors = ContributorsIndexPage(
                title="contributors",
                slug=slug
            )
            home.add_child(instance=contributors)

        slug = "map"
        if MapPage.objects.filter(slug=slug).descendant_of(home).exists() is False:
            map = MapPage(
                title="Map",
                slug=slug
            )
            home.add_child(instance=map)

        slug = "radio"
        if RadioIndexPage.objects.filter(slug=slug).descendant_of(home).exists() is False:
            radio = RadioIndexPage(
                title="Radio",
                slug=slug
            )
            home.add_child(instance=radio)
