from django import template
from logbooks.middleware.pages import ImportantPagesMiddleware
from wagtail.models import Locale

register = template.Library()


@register.simple_tag
def site_settings(page):
    locale = Locale.get_active()
    return ImportantPagesMiddleware.get_menu_items(locale).get(page, None)
