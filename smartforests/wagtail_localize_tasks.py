from wagtail_localize.tasks import BaseJobBackend
from django.conf import settings


class DjangoDBQueueJobBackend(BaseJobBackend):
    def enqueue(self, func, args, kwargs):
        if settings.USE_BACKGROUND_WORKER and func.__name__ == 'synchronize_tree':
            print("Disabled syncing")
            pass
        else:
            func(*args, **kwargs)
