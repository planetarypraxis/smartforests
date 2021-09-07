from random import randint, shuffle

from django.core.files.images import ImageFile
from smartforests.models import CmsImage
from django.core.management.base import BaseCommand
from django.core.files.temp import NamedTemporaryFile
from django.db import transaction
from wagtail.core.rich_text import RichText
from commonknowledge.wagtail.helpers import get_children_of_type
from datetime import datetime

from faker import Faker, providers
import requests

from logbooks.models import LogbookIndexPage, LogbookPage, StoryIndexPage, StoryPage


class Command(BaseCommand):
    help = 'Seed the forest'

    def add_arguments(self, parser):
        parser.add_argument('-ss', '--storysize', dest='storysize', type=int,
                            help='Control the size distribution of stories', default=3)

        parser.add_argument('-l', '--logbooks', dest='logbooks', type=int,
                            help='How many logbooks', default=10)

        parser.add_argument('-s', '--stories', dest='stories', type=int,
                            help='How many stories', default=100)

        parser.add_argument('-t', '--tags', dest='tags', type=int,
                            help='How many tags', default=30)

        parser.add_argument('--tags_per_logbook', dest='tags_per_logbook', type=int,
                            help='How many tags per logbook', default=4)

        parser.add_argument('--tags_per_story', dest='tags_per_story', type=int,
                            help='How many tags per story', default=3)

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()

        def random_distribution():
            # Get a nice distribition for a story length
            return max(1, int(randint(0, options.get('storysize')) ** 2 / 5), max(3, options.get('storysize')))

        # https://faker.readthedocs.io/en/master/providers.html
        fake.add_provider(providers.internet)
        fake.add_provider(providers.lorem)
        fake.add_provider(providers.misc)

        tags = [
            fake.word()
            for _ in range(options.get('tags'))
        ]

        def get_image(seed):
            title = f'example_{seed}'

            try:
                return CmsImage.objects.get(title=title)
            except CmsImage.DoesNotExist:
                image_temp_file = NamedTemporaryFile(delete=True)

                width = 600
                height = randint(5, 10) * 100

                res = requests.get(
                    f'https://picsum.photos/{width}/{height}.jpg', stream=True)

                # Write the in-memory file to the temporary file
                # Read the streamed image in sections
                for block in res.iter_content(1024 * 8):

                    # If no more file then stop
                    if not block:
                        break    # Write image block to temporary file
                    image_temp_file.write(block)

                image = CmsImage(
                    title=title, alt_text=fake.sentence(), width=width, height=height, file=ImageFile(image_temp_file))
                image.save()
                return image

        def apply_tags(x, count=5):
            shuffle(tags)
            selected_tags = tags[:count]
            x.tags.set(*selected_tags)

        block_generators = {
            'text': lambda: RichText(f'<p>{" ".join(fake.paragraphs(4))}</p>'),
            'quote': lambda: {
                'text': RichText(f'<p>{fake.sentence()}</p>'),
                'author': fake.name(),
                'title': fake.sentence(),
                'date': datetime.now(),
                'link': '/'
            },
            'image': lambda: {
                'image': get_image(randint(100, 200)),
                'caption': fake.sentence()
            }
        }

        def generate_story_block():
            keys = list(block_generators.keys())
            shuffle(keys)
            type = keys[0]

            return (type, block_generators[type]())

        def populate_logbook(logbook: LogbookPage):
            apply_tags(logbook, options.get('tags_per_logbook'))
            logbook.save()

        def populate_story(story: StoryPage):
            story.body = [generate_story_block()
                          for _ in range(random_distribution())]
            apply_tags(story, options.get('tags_per_story'))

            story.save()

        for index in LogbookIndexPage.objects.all():
            if index.is_leaf():
                for _ in range(options.get('logbooks')):
                    logbook = LogbookPage(
                        title=fake.sentence(),
                        description=fake.paragraph()
                    )
                    index.add_child(instance=logbook)
                    populate_logbook(logbook)
            else:
                for logbook in get_children_of_type(index, LogbookPage):
                    populate_logbook(logbook)

        for index in StoryIndexPage.objects.all():
            if index.is_leaf():
                for _ in range(options.get('stories')):
                    story = StoryPage(title=fake.sentence())
                    index.add_child(instance=story)
                    populate_story(story)
            else:
                for story in get_children_of_type(index, StoryPage):
                    populate_story(story)
