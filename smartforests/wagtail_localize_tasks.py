from wagtail_localize.tasks import BaseJobBackend
from wagtail_localize.synctree import synchronize_tree
from django_dbq.models import Job


def sync_tree(job):
    synchronize_tree(*job.get('args', []), **job.get('kwargs', {}))


class DjangoDBQueueJobBackend(BaseJobBackend):
    def enqueue(self, func, args, kwargs):
        if func.__name__ == 'synchronize_tree':
            Job.objects.create("wagtail_localize.synchronize_tree", workspace={
                "args": args,
                "kwargs": kwargs
            })
        else:
            func(*args, **kwargs)
