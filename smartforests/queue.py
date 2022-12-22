from jsonic import serialize, deserialize
from wagtail_localize.synctree import synchronize_tree
from django_dbq.models import Job


def process_serialized_func(func):
    def run(*args, **kwargs):
        func(*args, **kwargs)
    return run


serialised_funcs = {
    "wagtail_localize.synctree.synchronize_tree": process_serialized_func(synchronize_tree)
}


def serialized_job(job):
    args = deserialize(job.workspace.get("args", []))
    kwargs = deserialize(job.workspace.get('kwargs', "{}"))
    func_key = job.workspace.get("func_key", None)
    func = serialised_funcs.get(func_key, None)
    func(*args, **kwargs)


def create_serialized_job(func_key, args, kwargs):
    return Job.objects.create(
        name="smartforests.queue.serialized_job",
        workspace={
            "func_key": func_key,
            "args": serialize(args),
            "kwargs": serialize(kwargs)
        }
    )
