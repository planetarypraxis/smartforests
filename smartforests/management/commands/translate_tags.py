from django.core.management.base import BaseCommand
from django.utils.text import slugify
from smartforests.models import Tag, User
from wagtail.models.i18n import Locale
from wagtail_localize.models import StringTranslation, Translation, TranslationSource
from wagtail_localize.views.edit_translation import machine_translate


class MockRequest:
    """
    Used to trigger a "translate this tag" request
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
    help = "Translate tags with WAGTAILLOCALIZE_MACHINE_TRANSLATOR"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin = User.objects.filter(is_superuser=True).first()
        self.mock_request = MockRequest(user=self.admin)

    def handle(self, *args, **options):
        tags = Tag.objects.all()
        for tag in tags:
            target_locales = Locale.objects.exclude(id=tag.locale.id)
            print(f"{str(tag).title()}: ensuring translations")
            self.ensure_translations(tag, target_locales)

    def ensure_translations(self, tag, locales):
        for locale in locales:
            # Check if translation already exists
            translated_tag = Tag.objects.filter(
                translation_key=tag.translation_key, locale=locale
            ).first()

            if not translated_tag:
                print(f">>>> {locale}: translating")

                # Create translated tag first, then update it (no other way)
                translated_tag, _ = Tag.objects.get_or_create(
                    name=tag.name,
                    translation_key=tag.translation_key,
                    locale=locale,
                    defaults={"slug": tag.slug},
                )

                # Create translation
                translation_source, _ = TranslationSource.get_or_create_from_instance(
                    tag
                )
                translation, _ = Translation.objects.get_or_create(
                    source=translation_source, target_locale=locale
                )

                # Update translation
                machine_translate(self.mock_request, translation.id)

                # Fix translated slugs (slugify them)
                string_translations = StringTranslation.objects.filter(
                    context__path="slug",
                    translation_of__segments__source=translation_source,
                )
                for string_translation in string_translations:
                    string_translation.data = slugify(string_translation.data)
                    string_translation.save()

                # Update tag
                translation.save_target(user=self.admin, publish=True)

                # Refresh from db to print translated tag
                translated_tag = Tag.objects.filter(
                    translation_key=tag.translation_key, locale=locale
                ).first()
                print(f">>>> {locale}: translated to {translated_tag.name}")
            else:
                print(f">>>> {locale}: translation exists")
