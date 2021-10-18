from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import PageChooserPanel
from django.db import models


# CMS settings for canonical index pages
@register_setting
class ImportantPages(BaseSetting):
    logbooks_index_page = models.ForeignKey(
        'logbooks.LogbookIndexPage', null=True, on_delete=models.SET_NULL, related_name='+')
    stories_index_page = models.ForeignKey(
        'logbooks.StoryIndexPage', null=True, on_delete=models.SET_NULL, related_name='+', verbose_name="Logbook Entries Index Page")

    panels = [
        PageChooserPanel('logbooks_index_page'),
        PageChooserPanel('stories_index_page'),
    ]
