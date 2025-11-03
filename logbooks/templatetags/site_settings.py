from django import template
from logbooks.context_processors import get_menu_items
from wagtail.models import Locale

register = template.Library()


@register.simple_tag
def site_settings(page):
    locale = Locale.get_active()
    return get_menu_items(locale).get(page, None)
