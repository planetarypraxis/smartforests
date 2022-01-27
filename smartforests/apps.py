from django.apps import AppConfig
from django.conf import settings
import posthog


class SmartForestsConfig(AppConfig):
    name = 'smartforests'

    def ready(self):
        import smartforests.signals.models
        import smartforests.signals.analytics

        if settings.POSTHOG_PUBLIC_TOKEN:
            posthog.api_key = settings.POSTHOG_PUBLIC_TOKEN
            posthog.host = settings.POSTHOG_URL
        if settings.DEBUG:
            posthog.disabled = True
