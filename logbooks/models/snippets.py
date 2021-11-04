from django.db import models
from django.db.models.signals import m2m_changed
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


@ receiver(m2m_changed, sender=AtlasTag)
def atlas_tag_changed(_sender, instance, action: str, pk_set, reverse: bool, model, **kwargs):
    from logbooks.models.tag_cloud import TagCloud

    def handle_tag(tag: Tag):
        tag.regenerate_thumbnails()
        TagCloud.build_for_tag(instance)

    if action not in ('post_add', 'post_remove', 'post_clear'):
        return

    if not reverse:
        handle_tag(instance)
    else:
        for instance in model.objects.filter(pk__in=pk_set):
            handle_tag(instance)
