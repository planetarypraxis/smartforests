from logbooks.models.pages import ContributorPage, LogbookPage, LogbookEntryPage, StoryPage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from logbooks.models.tag_cloud import TagCloud
from smartforests.models import Tag, User


class Command(BaseCommand):
    help = 'Regenerate indexes for all pages in the logbook module'

    @transaction.atomic
    def handle(self, *args, **options):
        for page in LogbookEntryPage.objects.all():
            page.save()

        for page in LogbookPage.objects.all():
            page.save()

        for page in StoryPage.objects.all():
            page.save()

        Tag.regenerate_thumbnails()
        TagCloud.reindex()

        for user in User.objects.all():
            ContributorPage.create_for_user(user)
