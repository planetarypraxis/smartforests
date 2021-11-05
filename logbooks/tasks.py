from wagtail.core.models import Page
from background_task import background

from smartforests.models import Tag


@background(schedule=15, remove_existing_tasks=True)
def regenerate_page_thumbnails(page_id: int):
    from logbooks.models.mixins import ThumbnailMixin
    try:
        page = Page.objects.get(pk=page_id).specific
    except Page.DoesNotExist:
        return

    if isinstance(page, ThumbnailMixin):
        page.regenerate_thumbnail()
        page.save(regenerate_thumbnails=False)


@background(schedule=15, remove_existing_tasks=True)
def regenerate_tag_thumbnails(tag_id: int):
    try:
        tag = Tag.objects.get(pk=tag_id)
    except Tag.DoesNotExist:
        return

    tag.regenerate_thumbnail()
    tag.save()


@background(schedule=15, remove_existing_tasks=True)
def regenerate_tag_cloud(tag_id: int):
    from logbooks.models import TagCloud
    try:
        tag = Tag.objects.get(pk=tag_id)
    except Tag.DoesNotExist:
        return

    TagCloud.build_for_tag(tag)
