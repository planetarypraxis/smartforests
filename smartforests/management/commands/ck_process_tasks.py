from django.core.management.base import BaseCommand
from django.core.management import call_command
from background_task.models import Task
from logbooks.tasks import publish


class Command(BaseCommand):
    help = "Run background tasks and publish scheduled pages"

    def handle(self, *args, **options):
        print("Running background tasks")
        # Two self-inflicted crawlers used to run here and are now disabled:
        #
        # - The site-wide link checker crawled every page on each run, and every
        #   worker restart queued a fresh scan on top of any still-running one.
        # - The cache warmer (populate_site_cache) re-fetched 84 index pages
        #   every cache TTL, around the clock. Each fetch is ~250-340 KB of
        #   uncompressed HTML leaving the web service, plus the same again
        #   written into the DB-backed page cache, and it made up ~80% of all
        #   requests to the site.
        #
        # Repeating tasks persist in the DB, so any existing rows are purged
        # on boot as well, otherwise they would keep firing.
        purged, _ = Task.objects.filter(
            task_name__in=[
                "smartforests.management.commands.ck_process_tasks.do_linkcheck",
                "wagtaillinkchecker.tasks.check_link",
                "logbooks.tasks.populate_site_cache",
            ]
        ).delete()
        if purged:
            print(f"Removed {purged} queued link checker / cache warmer task(s)")
        publish(repeat=Task.HOURLY / 2)  # half-hourly
        call_command("process_tasks")
