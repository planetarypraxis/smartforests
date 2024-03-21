from logbooks.models.pages import ContributorPage, EpisodePage, LogbookPage, LogbookEntryPage, StoryPage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from smartforests.models import Tag, User
from smartforests.tag_cloud import recalculate_taglinks


class Command(BaseCommand):
    help = 'Regenerate indexes for all pages in the logbook module'

    @transaction.atomic
    def handle(self, *args, **options):
        # for page in LogbookEntryPage.objects.all():
        #     page.save()

        # for page in LogbookPage.objects.all():
        #     page.save()

        # for page in StoryPage.objects.all():
        #     page.save()

        # for page in EpisodePage.objects.all():
        #     page.save()

        print("Regenerating thumbnails")
        # Tag.regenerate_thumbnails()

        print("Reindexing tag clouds")
        recalculate_taglinks()

        for user in User.objects.all():
            print("Creating contributor page for", user)
            ContributorPage.create_for_user(user)
