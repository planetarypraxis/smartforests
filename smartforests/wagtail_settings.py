from django.urls import reverse
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.models import Page
from wagtail.contrib.settings.models import BaseSetting, register_setting
from django.db import models
from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from generic_chooser.widgets import AdminChooser
from logbooks.models.pages import EpisodePage
from smartforests.models import CmsImage


from smartforests.views import RadioEpisodeChooserViewSet


class RadioEpisodeChooser(AdminChooser):
    choose_one_text = _('Choose a radio episode')
    choose_another_text = _('Choose another episode')
    link_to_chosen_text = _('Edit this episode')
    model = EpisodePage
    choose_modal_url_name = 'radio_episode_chooser:choose'

    def get_edit_item_url(self, item):
        return reverse('wagtailsnippets:edit', args=('logbooks', 'episodepage', quote(item.pk)))


@register_setting(icon='pick')
class FeaturedContent(BaseSetting):
    class Meta:
        verbose_name = 'Featured content'

    # Preload this page when using these settings in templates
    # https://docs.wagtail.org/en/latest/reference/contrib/settings.html#utilising-select-related-to-improve-efficiency
    select_related = ["radio_episode"]

    radio_episode = models.ForeignKey(
        'logbooks.EpisodePage', blank=True, null=True, on_delete=models.DO_NOTHING)

    panels = [
        FieldPanel('radio_episode', widget=RadioEpisodeChooser)
    ]


@register_setting(icon='web')
class SocialMediaSettings(BaseSetting):
    class Meta:
        verbose_name = 'Social media settings'

    default_seo_image = models.ForeignKey(
        CmsImage, blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="+"
    )

    panels = [
        ImageChooserPanel('default_seo_image')
    ]


@hooks.register('register_admin_menu_item')
def register_frank_menu_item():
    return MenuItem('Featured Content', settings_path(FeaturedContent), icon_name='pick', order=10000)


def settings_path(custom_settings_cls):
    return f'/admin/settings/{custom_settings_cls._meta.app_label}/{custom_settings_cls._meta.model_name}'
