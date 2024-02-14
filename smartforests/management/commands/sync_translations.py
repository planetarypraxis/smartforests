from django.core.management.base import BaseCommand
from wagtail.models import Page
from wagtail_localize.models import TranslationSource


class Command(BaseCommand):
    help = 'Sync translations'

    def handle(self, *args, **options):
        pages = Page.objects.all()
        for page in pages:
            print("Updating " + str(page))
            TranslationSource.update_or_create_from_instance(page)
