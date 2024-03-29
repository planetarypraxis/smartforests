from django.core.management.base import BaseCommand, CommandParser
from django.utils.text import slugify
from logbooks.models import (
    LogbookPage,
    LogbookEntryPage,
    StoryPage,
    EpisodePage,
    ContributorPage,
)
from smartforests.models import User
from wagtail.models.i18n import Locale
from wagtail_localize.models import StringTranslation, Translation, TranslationSource
from wagtail_localize.operations import translate_object
from wagtail_localize.views.edit_translation import machine_translate
from smartforests.management.commands.sync_translations import is_original


class MockRequest:
    """
    Used to trigger a "translate this page" request
    """

    class MockMessages:
        def add(self, *args, **kwargs):
            pass

    def __init__(self, user):
        self.user = user
        self.method = "POST"
        self._messages = MockRequest.MockMessages()
        self.POST = {"next": "https://example.com"}

    def get_host(self):
        return "example.com"


class Command(BaseCommand):
    help = """
    Translate pages with WAGTAILLOCALIZE_MACHINE_TRANSLATOR. Note: if you get an error like
    'StringSegmentValue does not exist', try running "s
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin = User.objects.filter(is_superuser=True).first()
        self.mock_request = MockRequest(user=self.admin)

    def add_arguments(self, parser):
        parser.add_argument(
            "-n",
            "--count",
            dest="count",
            type=int,
            help="Limit the number of translated pages",
            default=None,
        )

    def handle(self, *args, **options):
        count = options.get("count")
        checked = 0
        translated = 0
        total = 0

        for page_class in [
            LogbookPage,
            LogbookEntryPage,
            StoryPage,
            EpisodePage,
            ContributorPage,
        ]:
            pages = page_class.objects.live().specific()
            total += len(pages)
            try:
                for page in pages:
                    checked += 1
                    if count is not None and count == translated:
                        break
                    # Can't translate the root page
                    if not page.get_parent():
                        continue

                    if not is_original(page):
                        continue

                    target_locales = Locale.objects.exclude(id=page.locale.id)
                    print(f"{page.title}: ensuring translations")
                    did_translation = self.ensure_translations(page, target_locales)
                    if did_translation:
                        translated += 1
            except KeyError as error:
                print(error)
        print(f"Processed {checked} of {total}")

    def ensure_translations(self, page, locales):
        did_translation = False
        for locale in locales:
            # Check if translation already exists
            translated_page = page.specific_class.objects.filter(
                translation_key=page.translation_key, locale=locale, alias_of=None
            ).first()

            print(f">>>> {locale}: translating")

            # Create translation source (or sync with the latest model version)
            (
                translation_source,
                _,
            ) = TranslationSource.update_or_create_from_instance(page)

            # Create translated page
            translate_object(page, locales=[locale])

            # Create translation
            translation, _ = Translation.objects.get_or_create(
                source=translation_source, target_locale=locale
            )

            # Update translation
            # This skips already translated segments, so safe to re-run on the same page
            machine_translate(self.mock_request, translation.id)

            # Fix translated slugs (slugify them)
            string_translations = StringTranslation.objects.filter(
                context__path="slug",
                translation_of__segments__source=translation_source,
            )
            for string_translation in string_translations:
                string_translation.data = slugify(string_translation.data)
                string_translation.save()

            # Update page
            translation.save_target(user=self.admin, publish=True)

            # Refresh from db to print translated page
            translated_page = page.specific_class.objects.filter(
                translation_key=page.translation_key, locale=locale
            ).first()
            print(f">>>> {locale}: translated to {translated_page.title}")
            did_translation = True

        return did_translation
