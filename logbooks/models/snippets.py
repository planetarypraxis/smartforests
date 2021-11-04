from django.db import models
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet


class AtlasTag(ItemBase):
    tag = models.ForeignKey(
        'smartforests.Tag', related_name="logbooks_atlastag_items", on_delete=models.CASCADE
    )

    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)
