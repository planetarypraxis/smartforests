from wagtail.core.models.i18n import Locale


def wagtail_locales(request):
    return {
        'WAGTAIL_LOCALES': Locale.objects.all()
    }
