from django.core.management.base import BaseCommand
from django.core.management import call_command
from background_task.models import Task
from logbooks.tasks import publish, populate_site_cache
import os


class Command(BaseCommand):
    help = "Run background tasks and publish scheduled pages"

    def handle(self, *args, **options):
        interval = int(os.environ.get("CACHE_MIDDLEWARE_SECONDS", 600)) + 10
        print("Running background tasks")
        # The site-wide link checker crawled every page (and every sort/filter
        # variant) on each run, and every worker restart queued a fresh scan on
        # top of any still-running one. That crawl was consuming most of the
        # Render bandwidth allowance, so it is disabled. Purge any queued scan
        # work left over from earlier runs so the backlog stops draining.
        purged, _ = Task.objects.filter(
            task_name__in=[
                "smartforests.management.commands.ck_process_tasks.do_linkcheck",
                "wagtaillinkchecker.tasks.check_link",
            ]
        ).delete()
        if purged:
            print(f"Removed {purged} queued link checker task(s)")
        publish(repeat=Task.HOURLY / 2)  # half-hourly
        populate_site_cache(
            repeat=Task.HOURLY * interval / 3600
        )  # every cache TTL + 10 seconds
        call_command("process_tasks")
