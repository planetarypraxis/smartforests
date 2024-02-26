from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.core.models import Page

class Command(BaseCommand):
    help = 'Manually regenerate a specific page thumbnail'

    def add_arguments(self, parser):
        parser.add_argument('-pk', '--pk', dest='pk', type=int,
                            help='Page ID to test', default=-1)

    @transaction.atomic
    def handle(self, *args, **options):
        page = Page.objects.get(pk=options.get('pk')).specific
        page.regenerate_thumbnail()
        page.save(regenerate_thumbnails=False)