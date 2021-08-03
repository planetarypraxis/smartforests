from random import randint, shuffle
from django.core.management.base import BaseCommand, CommandError
from faker import Faker, providers

from logbooks.models import LogbookIndexPage, LogbookPage, StoryIndexPage, StoryPage


class Command(BaseCommand):
    help = 'Seed the forest'

    def handle(self, *args, **options):
        fake = Faker()

        # https://faker.readthedocs.io/en/master/providers.html
        fake.add_provider(providers.internet)
        fake.add_provider(providers.lorem)
        fake.add_provider(providers.misc)

        tags = [
            fake.word()
            for _ in range(100)
        ]

        for index in LogbookIndexPage.objects.all():
            for _ in range(100):
                shuffle(tags)

                logbook = LogbookPage(title=fake.sentence())
                logbook.tags.add(*tags[:10])
                index.add_child(instance=logbook)
                logbook.save()

                for _ in range(randint(0, 100)):
                    story = StoryPage(title=fake.sentence())
                    logbook.add_child(instance=story)
                    story.save()

        for index in StoryIndexPage.objects.all():
            for _ in range(100):
                shuffle(tags)

                logbook = StoryPage(title=fake.sentence())
                logbook.tags.add(*tags[:10])
                index.add_child(instance=logbook)
                logbook.save()

                for _ in range(randint(0, 100)):
                    story = StoryPage(title=fake.sentence())
                    logbook.add_child(instance=story)
                    story.save()
