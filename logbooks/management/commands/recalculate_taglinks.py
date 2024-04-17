from logbooks.models.pages import (
    ContributorPage,
)
from django.core.management.base import BaseCommand

from smartforests.tag_cloud import recalculate_taglinks


class Command(BaseCommand):
    help = "Regenerate indexes for all pages in the logbook module"

    def add_arguments(self, parser):
        parser.add_argument(
            "-l",
            "--locale",
            dest="locale",
            type=str,
            help="Process tags in this locale",
            default="",
        )

    def handle(self, *args, **options):
        print("Reindexing tag clouds")
        locale = options.get("locale")
        recalculate_taglinks(language_code=locale)
