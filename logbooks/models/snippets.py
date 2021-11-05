from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch.dispatcher import receiver
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet

from smartforests.models import Tag


class AtlasTag(ItemBase):
    tag = models.ForeignKey(
        'smartforests.Tag', related_name="logbooks_atlastag_items", on_delete=models.CASCADE
    )

    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)
