from django.db.models.fields.related import ManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from django.db import models
from wagtail.core.models import Page
from modelcluster.fields import ParentalManyToManyField
from logbooks.models.pages import LogbookIndexPage, StoryIndexPage
from smartforests.models import MapPage
from django import forms
from wagtailautocomplete.edit_handlers import AutocompletePanel


# CMS settings for canonical index pages
@register_setting
class ImportantPages(BaseSetting):
    logbooks_index_page = models.ForeignKey(
        LogbookIndexPage, null=True, on_delete=models.SET_NULL, related_name='+')

    stories_index_page = models.ForeignKey(
        StoryIndexPage, null=True, on_delete=models.SET_NULL, related_name='+')

    map_page = models.ForeignKey(
        MapPage, null=True, on_delete=models.SET_NULL, related_name='+')

    menu_items = ManyToManyField(
        Page, blank=True, related_name='+')

    panels = [
        PageChooserPanel('logbooks_index_page'),
        PageChooserPanel('stories_index_page'),
        PageChooserPanel('map_page'),
        AutocompletePanel('menu_items'),
    ]
