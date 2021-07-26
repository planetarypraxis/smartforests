from django.contrib.auth.models import AbstractUser
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.documents.models import Document, AbstractDocument


class User(AbstractUser):
    pass


class CmsImage(AbstractImage):
    import_ref = models.CharField(max_length=1024, null=True, blank=True)

    admin_form_fields = Image.admin_form_fields


class ImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CmsImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )


class CmsDocument(AbstractDocument):
    import_ref = models.CharField(max_length=1024, null=True, blank=True)
    admin_form_fields = Document.admin_form_fields


def pre_save_image_or_doc(sender, instance, *args, **kwargs):
    if instance.file is not None:
        if instance.file.name.startswith('import_'):
            instance.import_ref = instance.file.name


models.signals.pre_save.connect(pre_save_image_or_doc, sender=CmsImage)
models.signals.pre_save.connect(
    pre_save_image_or_doc, sender=CmsDocument)
