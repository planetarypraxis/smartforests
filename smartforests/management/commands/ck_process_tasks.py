from django.core.management.base import BaseCommand
from django.core.management import call_command
from background_task.models import Task
from logbooks.tasks import publish


class Command(BaseCommand):
    help = "Run background tasks and publish scheduled pages"

    def handle(self, *args, **options):
        print("Running background tasks")
        publish(repeat=Task.HOURLY / 2) # half-hourly
        call_command("process_tasks")
