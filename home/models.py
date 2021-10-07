from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from smartforests.models import CmsImage
from django.db import models
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from commonknowledge.wagtail.models import ChildListMixin


class HomePage(ChildListMixin, Page):
    show_in_menus_default = True
    subpage_types = [
        'stories.StoryIndexPage',
        'logbooks.LogbookIndexPage',
        'home.InformationPage'
    ]
    pass


class InformationPage(Page):
    show_in_menus_default = True
    parent_page_types = [
        'home.HomePage',
        'home.InformationPage'
    ]

    cover_image = models.ForeignKey(
        CmsImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    text = RichTextField()

    content_panels = Page.content_panels + [
        ImageChooserPanel('cover_image'),
        FieldPanel('text')
    ]
