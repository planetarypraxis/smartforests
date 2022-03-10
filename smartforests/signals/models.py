from django.db.models.signals import pre_delete
from django.dispatch import receiver
from logbooks.models.mixins import ContributorMixin
from logbooks.models.pages import LogbookEntryPage
from wagtail.core.signals import page_published

from logbooks.tasks import regenerate_page_thumbnails


def contributor_edit_signal(sender, instance, **kwargs):
    '''
    Regenerate contributor lists for parent
    when a child page is updated
    '''
    # Trickle this up to higher level ContributorMixin pages
    # e.g. LogbookEntryPage -> LogbookPage
    page = instance.get_parent().specific
    while isinstance(page, ContributorMixin):
        page.update_contributors(save=True)
        page = page.get_parent().specific


page_published.connect(contributor_edit_signal)


@receiver(pre_delete, sender=LogbookEntryPage, dispatch_uid='logbookentrypage_delete_signal')
def logbookentrypage_delete_signal(sender, instance, using, **kwargs):
    '''
    Regenerate thumbnails for parent page, when a child page is deleted
    '''
    if instance.live:
        # Unpublish so its images aren't included in the parent's thumbnail
        instance.live = False
        instance.save()
    regenerate_page_thumbnails(instance.get_parent().id)
