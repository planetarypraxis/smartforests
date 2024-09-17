import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
if os.environ.get("DEBUG", False) == "True":
    settings = "smartforests.settings.dev"
else:
    settings = "smartforests.settings.production"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

app = Celery("smartforests")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
