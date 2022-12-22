from wagtail_localize.tasks import BaseJobBackend
from django.conf import settings
from smartforests.queue import create_serialized_job
from asgiref.sync import sync_to_async
from time import sleep
import asyncio


class DjangoDBQueueJobBackend(BaseJobBackend):
    def enqueue(self, func, args, kwargs):
        if settings.USE_BACKGROUND_WORKER and func.__name__ == 'synchronize_tree':
            @sync_to_async
            def execute():
                func(*args, **kwargs)

            asyncio.ensure_future(execute())
        else:
            func(*args, **kwargs)
