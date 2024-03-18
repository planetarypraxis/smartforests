from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from wagtail.models import Page
from wagtail.models.i18n import Locale
from wagtail_localize.models import TranslationSource, MissingTranslationError


class Command(BaseCommand):
    help = "Sync translations"

    def handle(self, *args, **options):
        locales = Locale.objects.all()
        pages = Page.objects.all()
        for page in pages:
            if page.get_parent() == None:
                continue

            print(f"Syncing {page}")

            source, _ = TranslationSource.update_or_create_from_instance(page)
            for locale in locales:
                success = self.sync_translation(page, source, locale)
                if success:
                    print(f"- Synced to {locale}")
                else:
                    print(f"- No translation for {locale}")

    def sync_translation(self, page, source, locale):
        if locale == page.locale:
            return False

        try:
            source.get_translated_instance(locale)
        except ObjectDoesNotExist:
            return False

        try:
            source.create_or_update_translation(locale)
        except MissingTranslationError:
            return False

        return True
