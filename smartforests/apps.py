from django.apps import AppConfig
from django.conf import settings
import posthog
import sentry_sdk
import willow
from io import BytesIO
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

sentry_sdk.init(
    dsn="https://aceb18d18bd284141a5bf45248493e8a@o1060355.ingest.us.sentry.io/4507231782764544",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)   

class SmartForestsConfig(AppConfig):
    name = 'smartforests'

    def ready(self):
        if settings.POSTHOG_PUBLIC_TOKEN:
            posthog.api_key = settings.POSTHOG_PUBLIC_TOKEN
            posthog.host = settings.POSTHOG_URL
        if settings.DEBUG:
            posthog.api_key = ""
            posthog.disabled = True

        # Override ImageFieldFile to automatically resize uploaded files
        ImageFieldFile.MAX_WIDTH = 1024

        original_save = ImageFieldFile.save

        def resize_and_save(self, name, content, save=True):
            name = self.field.generate_filename(self.instance, name)
    
            try:
                size = self.width * self.height
            except Exception as e:
                logger.debug(f"Cannot get image size: {e}")
                return original_save(self, name=name, content=content, save=save)

            max_size = self.MAX_WIDTH * self.MAX_WIDTH
            if size > max_size:
                content = self.resize(content)
            self.name = self.storage.save(name, content, max_length=self.field.max_length)
            setattr(self.instance, self.field.attname, self.name)
            self._committed = True

            # Save the object because it has changed, unless save is False
            if save:
                self.instance.save()
        resize_and_save.alters_data = True

        def resize(self, content):
            image = willow.Image.open(content)
            if self.width > self.height:
                new_width = self.MAX_WIDTH
                new_height = int(self.height * self.MAX_WIDTH / self.width)
            else:
                new_height = self.MAX_WIDTH
                new_width = int(self.width * self.MAX_WIDTH / self.height)
            image = image.resize((new_width, new_height))
            image_bytes = BytesIO()
            image.save_as_png(image_bytes)
            return image_bytes

        ImageFieldFile.save = resize_and_save
        ImageFieldFile.resize = resize
