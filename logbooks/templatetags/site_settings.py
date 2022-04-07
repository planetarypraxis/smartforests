
from django import template
from logbooks.middleware.pages import ImportantPagesMiddleware
register = template.Library()


@register.simple_tag
def site_settings(page):
    return ImportantPagesMiddleware.get_menu_items().get(page, None)
