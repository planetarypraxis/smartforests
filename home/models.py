from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from logbooks.views import pages_for_tag
from logbooks.models.mixins import ArticleSeoMixin
from logbooks.models.tag_cloud import TagCloud
from smartforests.models import CmsImage
from smartforests.mixins import SeoMetadataMixin
from django.db import models
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from commonknowledge.wagtail.models import ChildListMixin


class HomePage(ChildListMixin, SeoMetadataMixin, Page):
    show_in_menus_default = True
    parent_page_types = ['wagtailcore.Page']

    @property
    def tag_cloud(self):
        tag_cloud = TagCloud.get_start(
            limit=30, prioritise_current_locale=True)
        return tag_cloud


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
        ImageChooserPanel('cover_image'),
        FieldPanel('text')
    ]

    seo_image_sources = [
        "og_image",
        "cover_image",
        "default_seo_image"
    ]
