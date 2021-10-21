from django.db import models
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet


@register_snippet
class AtlasTag(TaggedItemBase):
    content_object = ParentalKey(
        Page, related_name='tagged_items', on_delete=models.CASCADE)
