from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.core.models import Page

class Command(BaseCommand):
    help = 'Manually regenerate a specific page thumbnail'

    def add_arguments(self, parser):
        parser.add_argument('-all', '--all', dest='all', type=bool,
                            help='Regen ALL pages?', default=False)

        parser.add_argument('-pk', '--pk', dest='pk', type=int,
                            help='Page ID to test', default=-1)

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get('all'):
            pages = [page for page in Page.objects.all().specific() if hasattr(page.specific, 'regenerate_thumbnail')]
            for page in pages:
                try:
                    print("Regenerating thumbnail for", page)
                    page.specific.regenerate_thumbnail()
                    page.specific.save(regenerate_thumbnails=False)
                except Exception as e:
                    print("Ignored error when regenerating thumbnail for", page, e)
        else:
            page = Page.objects.get(pk=options.get('pk')).specific
            page.regenerate_thumbnail()
            page.save(regenerate_thumbnails=False)