from logbooks.models.pages import LogbookPage, LogbookEntryPage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from logbooks.models import LogbookPageIndex
from logbooks.models.tag_cloud import TagCloud
from smartforests.models import Tag


class Command(BaseCommand):
    help = 'Regenerate indexes for all pages in the logbook module'

    @transaction.atomic
    def handle(self, *args, **options):
        LogbookPageIndex.objects.all().delete()

        for page in LogbookEntryPage.objects.all():
            page.save()

        for page in LogbookPage.objects.all():
            page.save()

        Tag.regenerate_thumbnails()
        TagCloud.reindex()
