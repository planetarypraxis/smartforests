from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from wagtail.models import Page
from wagtail.models.i18n import Locale
from wagtail_localize.models import TranslationSource, MissingTranslationError


class Command(BaseCommand):
    help = "Sync translations"

    def handle(self, *args, **options):
        pages = Page.objects.all()
        locales = Locale.objects.all()
        for page in pages:
            sync_translations(page, locales)


def sync_translations(page, locales=None):

    try:
        # Can't translate the root page
        page.get_parent()
    except ObjectDoesNotExist:
        return

    if not is_original(page):
        return

    if not locales:
        locales = Locale.objects.all()

    print(f"Syncing {page}")

    source, _ = TranslationSource.update_or_create_from_instance(page)
    for locale in locales:
        success = sync_translation(page, source, locale)
        if success:
            print(f"- Synced to {locale}")
        else:
            print(f"- No translation for {locale}")


def is_original(page):
    """
    Returns True if this is the original version of the page.
    Works by checking if the TranslationSource of the page has
    the same locale.
    """
    sources = TranslationSource.objects.filter(object_id=page.translation_key)

    # No TranslationSource => no translation => is original
    if not sources:
        return True

    return sources[0].locale.id == page.locale.id


def sync_translation(page, source, locale):
    if locale == page.locale:
        return False

    try:
        source.get_translated_instance(locale)
    except ObjectDoesNotExist:
        return False

    try:
        source.create_or_update_translation(locale)
    except ObjectDoesNotExist:
        return False
    except MissingTranslationError:
        return False

    return True
