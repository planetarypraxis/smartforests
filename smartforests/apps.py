from django.apps import AppConfig
from django.conf import settings
import posthog
import sentry_sdk

sentry_sdk.init(
    dsn="https://aceb18d18bd284141a5bf45248493e8a@o1060355.ingest.us.sentry.io/4507231782764544",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)   

class SmartForestsConfig(AppConfig):
    name = 'smartforests'

    def ready(self):
        import smartforests.signals.models
        import smartforests.signals.analytics
        import smartforests.wagtail_settings

        if settings.POSTHOG_PUBLIC_TOKEN:
            posthog.api_key = settings.POSTHOG_PUBLIC_TOKEN
            posthog.host = settings.POSTHOG_URL
        if settings.DEBUG:
            posthog.api_key = ""
            posthog.disabled = True
