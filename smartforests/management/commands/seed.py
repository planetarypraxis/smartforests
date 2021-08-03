from random import randint, shuffle

from django.core.files.images import ImageFile
from smartforests.models import CmsImage
from django.core.management.base import BaseCommand
from django.core.files.temp import NamedTemporaryFile
from django.db import transaction
from wagtail.core.rich_text import RichText

from faker import Faker, providers
import requests

from logbooks.models import LogbookIndexPage, LogbookPage, StoryIndexPage, StoryPage


class Command(BaseCommand):
    help = 'Seed the forest'

    @transaction.atomic
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

        def apply_tags(x, count=10):
            shuffle(tags)
            x.tags.set(*tags[:count])

        block_generators = {
            'text': lambda: RichText(f'<p>{fake.paragraphs(2)}</p>'),
            'quote': lambda: {
                'text': RichText(f'<p>{fake.sentence()}</p>')
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

        for index in LogbookIndexPage.objects.all():
            for _ in range(100):
                logbook = LogbookPage(title=fake.sentence())
                index.add_child(instance=logbook)
                apply_tags(logbook)

                logbook.save()

        for index in StoryIndexPage.objects.all():
            for _ in range(100):
                story = StoryPage(title=fake.sentence())
                story.body = [generate_story_block()
                              for _ in range(randint(0, 20))]
                apply_tags(story)
                index.add_child(instance=story)

                story.save()
