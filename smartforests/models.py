from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.dispatch.dispatcher import receiver
from taggit.models import TagBase
from wagtail.core.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.documents.models import Document, AbstractDocument
from wagtail.core.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.apps import apps
from commonknowledge.django.images import render_image_grid
import re

from wagtail.snippets.models import register_snippet


@register_snippet
class Tag(TagBase):
    description = RichTextField(blank=True, default="")
    thumbnail = models.ImageField(null=True, blank=True)

    @staticmethod
    def regenerate_thumbnails():
        for tag in Tag.objects.iterator():
            tag.regenerate_thumbnail()

    def regenerate_thumbnail(self):
        thumbnails = []

        for tagging in self.logbooks_atlastag_items.all():
            if hasattr(tagging.content_object.specific, 'get_thumbnail_images'):
                thumbnails += tagging.content_object.specific.get_thumbnail_images()

            if len(thumbnails) >= 3:
                break

        thumbnails = thumbnails[:3]

        if len(thumbnails) > 0:
            self.thumbnail = render_image_grid(
                thumbnails,
                rows=1,
                cols=len(thumbnails),
                format='JPEG',
                filename=f'tagthumb_{self.slug}.jpeg',
                width=800,
                height=400
            )
        else:
            self.thumbnail = None

        self.save()


class MapPage(RoutablePageMixin, Page):
    parent_page_types = ['home.HomePage']
    max_count = 1

    @route(r'^(?P<path>.*)/?$')
    def subpages(self, request, path, *args, **kwargs):
        '''
        Subpaths of this page will show a sidepanel with the relevant model.
        '''
        try:
            '''
            If URL points to a sidepanel, load the relevant model so the sidepanel HTML can be pre-rendered.
            Can also be used to render meta HTML for things like sharecards.
            '''
            sidepanel_route = r'(?P<app_label>[-\w_]+)/(?P<model_name>[-\w_]+)/(?P<record_id>[0-9]+).*$'
            sidepanel_match = re.match(sidepanel_route, path).groupdict()
            model = apps.get_model(
                app_label=sidepanel_match['app_label'],
                model_name=sidepanel_match['model_name']
            )
            page = model.objects.get(id=sidepanel_match['record_id'])
            return self.render(request, context_overrides={
                'sidepanel_page': page
            })
        except:
            return self.serve(request)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['mapbox_token'] = settings.MAPBOX_API_PUBLIC_TOKEN
        context['supercluster_url'] = settings.SUPERCLUSTER_URL
        return context


class User(AbstractUser):
    def autocomplete_label(self):
        return self.get_full_name() or self.username

    autocomplete_search_field = 'username'


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
