from django.urls import reverse
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.core.models import Page
from wagtail.contrib.settings.models import BaseSetting, register_setting
from django.db import models


@register_setting(icon='pick')
class FeaturedContent(BaseSetting):
    class Meta:
        verbose_name = 'Featured Content'

    # Preload this page when using these settings in templates
    # https://docs.wagtail.org/en/latest/reference/contrib/settings.html#utilising-select-related-to-improve-efficiency
    select_related = ["radio_episode"]

    radio_episode = models.ForeignKey(
        'logbooks.EpisodePage', blank=True, null=True, on_delete=models.DO_NOTHING)

    panels = [
        FieldPanel('radio_episode')
        # Using this instead of
        # PageChooserPanel('radio_episode', 'logbooks.EpisodePage')
        # because you shouldn't have to navigate through the page tree to find relevant pages.
        # Is there a PageChooserPanel that shows a flat list of relevant pages?
    ]


@hooks.register('register_admin_menu_item')
def register_frank_menu_item():
    return MenuItem('Featured Content', settings_path(FeaturedContent), icon_name='pick', order=10000)


def settings_path(custom_settings_cls):
    return f'/admin/settings/{custom_settings_cls._meta.app_label}/{custom_settings_cls._meta.model_name}'
