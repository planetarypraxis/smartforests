from django.apps import apps
from django.core.management.base import BaseCommand
from logbooks.models import GeocodedMixin
import logging

logging.basicConfig(filename='skipped_models.log', level=logging.INFO, format='%(asctime)s %(message)s')

class Command(BaseCommand):
    help = 'Update map thumbnails for all instances of models inheriting from GeocodedMixin'

    def handle(self, *args, **kwargs):
        # Get all models that inherit from GeocodedMixin
        geocoded_models = [
            model for model in apps.get_models() if issubclass(model, GeocodedMixin) and not model._meta.abstract
        ]
        
        for model in geocoded_models:
            self.stdout.write(self.style.NOTICE(f'Processing model: {model._meta.model_name}'))
            instances = model.objects.all()
            for instance in instances:
                if instance.coordinates:
                    try:
                        instance.update_map_thumbnail()
                        instance.save_revision().publish()
                        instance_title = getattr(instance, 'title', getattr(instance, 'name', 'Unknown Title'))
                        self.stdout.write(self.style.SUCCESS(
                            f'Updated map thumbnail for "{instance_title}" at {instance.coordinates} ({model._meta.model_name})'
                        ))
                    except Exception as e:
                        instance_title = getattr(instance, 'title', getattr(instance, 'name', 'Unknown Title'))
                        self.stdout.write(self.style.ERROR(
                            f'Skipped updating map thumbnail for "{instance_title}" at {instance.coordinates} ({model._meta.model_name}) due to error: {e}'
                        ))
                        logging.info(f'Skipped model {model._meta.model_name}, instance "{instance_title}" due to error: {e}')