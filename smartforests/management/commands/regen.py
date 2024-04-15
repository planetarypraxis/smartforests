from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page


class Command(BaseCommand):
    help = "Manually regenerate a specific page thumbnail"

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--all",
            dest="all",
            help="Regen ALL pages?",
            default=False,
            action="store_true",
        )

        parser.add_argument(
            "-k", "--pk", dest="pk", type=int, help="Page ID to test", default=-1
        )

        parser.add_argument(
            "-s",
            "--slug",
            dest="slug",
            type=str,
            help="Page slug to test",
            default="",
        )

        parser.add_argument(
            "-f",
            "--force",
            dest="force",
            help="Force regenerate and re-save",
            default=False,
            action="store_true",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options.get("force")
        pk = options.get("pk")
        slug = options.get("slug")
        if options.get("all"):
            pages = [
                page
                for page in Page.objects.all().specific()
                if hasattr(page.specific, "regenerate_thumbnail")
            ]
            for page in pages:
                try:
                    print("Regenerating thumbnail for", page)
                    page.specific.regenerate_thumbnail(force=force)
                    page.specific.save(regenerate_thumbnails=False)
                except Exception as e:
                    print("Ignored error when regenerating thumbnail for", page, e)
        elif pk > -1:
            page = Page.objects.get(pk=pk).specific
            print("Regenerating thumbnail for", page)
            page.regenerate_thumbnail(force=force)
            page.save(regenerate_thumbnails=False)
        elif slug != "":
            print("Regenerating thumbnail for", slug)
            page = Page.objects.get(slug=slug).specific
            page.regenerate_thumbnail(force=force)
            page.save(regenerate_thumbnails=False)
