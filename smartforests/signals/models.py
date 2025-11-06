from django.db.models.signals import pre_delete
from django.dispatch import receiver
from logbooks.models.pages import LogbookEntryPage
from wagtail.models import Page

from logbooks.tasks import regenerate_page_thumbnails


@receiver(pre_delete, sender=LogbookEntryPage, dispatch_uid='logbookentrypage_delete_signal')
def logbookentrypage_delete_signal(sender, instance, using, **kwargs):
    '''
    Regenerate thumbnails for parent page, when a child page is deleted
    '''
    try:
        if instance.live:
            # Unpublish so its images aren't included in the parent's thumbnail
            instance.live = False
            instance.save()
            regenerate_page_thumbnails(instance.get_parent().id)
    except Page.DoesNotExist:
        pass
