from random import randint
from django.core.management.base import BaseCommand, CommandError
from faker import Faker, providers

from logbooks.models import LogbookIndexPage, LogbookPage, StoryPage


class Command(BaseCommand):
    help = 'Seed the forest'

    def handle(self, *args, **options):
        fake = Faker()

        # https://faker.readthedocs.io/en/master/providers.html
        fake.add_provider(providers.internet)
        fake.add_provider(providers.lorem)
        fake.add_provider(providers.misc)

        for index in LogbookIndexPage.objects.all():
            for _ in range(100):
                logbook = LogbookPage(title=fake.sentence())
                index.add_child(instance=logbook)
                logbook.save()

                for _ in range(randint(0, 100)):
                    story = StoryPage(title=fake.sentence())
                    logbook.add_child(instance=story)
                    story.save()
