from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import PageChooserPanel
from django.db import models
from logbooks.models.pages import LogbookIndexPage, StoryIndexPage
from smartforests.models import MapPage


# CMS settings for canonical index pages
@register_setting
class ImportantPages(BaseSetting):
    logbooks_index_page = models.ForeignKey(
        LogbookIndexPage, null=True, on_delete=models.SET_NULL, related_name='+')

    stories_index_page = models.ForeignKey(
        StoryIndexPage, null=True, on_delete=models.SET_NULL, related_name='+')

    map_page = models.ForeignKey(
        MapPage, null=True, on_delete=models.SET_NULL, related_name='+')

    panels = [
        PageChooserPanel('logbooks_index_page'),
        PageChooserPanel('stories_index_page'),
        PageChooserPanel('map_page')
    ]

    def to_dict(self):
        return {
            "logbooks": self.logbooks_index_page.localized.url,
            "stories_index_page": self.stories_index_page.localized.url,
            "map_page": self.map_page.localized.url
        }
