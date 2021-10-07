from django.contrib.auth.models import AbstractUser
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.documents.models import Document, AbstractDocument
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.snippets.models import register_snippet
from wagtail.core.models import Page


@register_snippet
class AtlasTag(TaggedItemBase):
    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)


# CMS settings for canonical index pages
@register_setting
class ImportantPages(BaseSetting):
    logbooks_index_page = models.ForeignKey(
        'logbooks.LogbookIndexPage', null=True, on_delete=models.SET_NULL, related_name='+')
    stories_index_page = models.ForeignKey(
        'stories.StoryIndexPage', null=True, on_delete=models.SET_NULL, related_name='+')

    panels = [
        PageChooserPanel('logbooks_index_page'),
        PageChooserPanel('stories_index_page'),
    ]


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
