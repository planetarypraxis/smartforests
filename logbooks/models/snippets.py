from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch.dispatcher import receiver
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from logbooks.tasks import regenerate_page_thumbnails, regenerate_tag_cloud, regenerate_tag_thumbnails

from smartforests.models import Tag


class AtlasTag(ItemBase):
    tag = models.ForeignKey(
        'smartforests.Tag', related_name="logbooks_atlastag_items", on_delete=models.CASCADE
    )

    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        regenerate_tag_thumbnails(self.tag.id)
        regenerate_tag_cloud(self.tag.id)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        regenerate_tag_thumbnails(self.tag.id)
        regenerate_tag_cloud(self.tag.id)

        return super().delete(*args, **kwargs)
