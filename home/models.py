from wagtail.admin.panels import FieldPanel
from logbooks.models.mixins import ArticleSeoMixin
from logbooks.models.tag_cloud import TagCloud
from smartforests.models import CmsImage
from smartforests.mixins import SeoMetadataMixin
from django.db import models
from wagtail.fields import RichTextField
from wagtail.models import Page
from commonknowledge.wagtail.models import ChildListMixin


class HomePage(ChildListMixin, SeoMetadataMixin, Page):
    show_in_menus_default = True
    parent_page_types = ['wagtailcore.Page']

    @property
    def tag_cloud(self):
        return TagCloud.get_start(
            limit=30, prioritise_current_locale=True)


class InformationPage(ArticleSeoMixin, Page):
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
        FieldPanel('cover_image'),
        FieldPanel('text')
    ]

    seo_image_sources = [
        "og_image",
        "cover_image",
        "default_seo_image"
    ]
