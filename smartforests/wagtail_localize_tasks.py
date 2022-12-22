from wagtail_localize.tasks import BaseJobBackend
from django.conf import settings
from smartforests.queue import create_serialized_job


class DjangoDBQueueJobBackend(BaseJobBackend):
    def enqueue(self, func, args, kwargs):
        if settings.USE_BACKGROUND_WORKER and func.__name__ == 'synchronize_tree':
            create_serialized_job(
                "wagtail_localize.synctree.synchronize_tree", args, kwargs)
        else:
            func(*args, **kwargs)
