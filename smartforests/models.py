from django.contrib.auth.models import AbstractUser
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.documents.models import Document, AbstractDocument
from wagtail.core.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


class MapPage(RoutablePageMixin, Page):
    # Hand off all routing below this page to the frontend router (react-router)
    @route(r'^(?P<path>.*)/?$')
    def subpages(self, request, *args, **kwargs):
        return self.serve(request)


class User(AbstractUser):
    pass


class CmsImage(AbstractImage):
    import_ref = models.CharField(max_length=1024, null=True, blank=True)

    # Making blank / null explicit because you *really* need alt text
    alt_text = models.CharField(
        max_length=1024, blank=False, null=False, default="", help_text="Describe this image as literally as possible. If you can close your eyes, have someone read the alt text to you, and imagine a reasonably accurate version of the image, you're on the right track.")

    admin_form_fields = (
        'file',
        'alt_text',
        'title',
    )


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
