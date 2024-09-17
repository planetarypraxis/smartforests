from django.core.management.base import BaseCommand
from django.core.management import call_command
from background_task import background
from background_task.models import Task
from logbooks.tasks import publish, populate_site_cache
import os


class Command(BaseCommand):
    help = "Run background tasks and publish scheduled pages"

    def handle(self, *args, **options):
        interval = int(os.environ.get("CACHE_MIDDLEWARE_SECONDS", 600)) + 10
        print("Running background tasks")
        publish(repeat=Task.HOURLY / 2)  # half-hourly
        populate_site_cache(
            repeat=Task.HOURLY * interval / 3600
        )  # every cache TTL + 10 seconds
        linkchecker(repeat=Task.DAILY)
        call_command("process_tasks")


@background(schedule=5, remove_existing_tasks=True)
def linkchecker():
    call_command("linkchecker")
