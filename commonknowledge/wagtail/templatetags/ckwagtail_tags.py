from urllib import parse
from wagtail.blocks.base import Block

from wagtail.models import Site
from django import template
from django.utils.safestring import mark_safe
from commonknowledge.helpers import safe_to_int
from django import template

register = template.Library()


@register.inclusion_tag('ckwagtail/include/menubar.html', takes_context=True)
def menubar(context, **kwargs):
    request = context.get('request', None)
    if request is None:
        return
    site = Site.find_for_request(request)
    if site is None:
        return

    root = site.root_page
    kwargs['pages'] = root.get_children().in_menu()
    kwargs['request'] = request

    return kwargs


@register.simple_tag(takes_context=True)
def next_page_path(context):
    request = context.get('request', None)
    if not request:
        return
    params = request.GET.dict()

    # Return the next page
    params['page'] = safe_to_int(params.get('page', 1), 1) + 1

    # This informs our ChildListMixin not to return any data after the last page.
    params['empty'] = '1'

    return mark_safe("?" + parse.urlencode(params))


@register.simple_tag(takes_context=True)
def render_streamfield(context, value, *args, **kwargs):
    def get_context(self, value, *args, **kwargs):
        return dict(context.flatten(), **{
            'self': value,
            self.TEMPLATE_VAR: value,
        })
    Block.get_context = get_context
    return str(value)


@register.simple_tag(takes_context=True)
def bulk_action_classes(context):
    request = context.get('request', None)
    if not request.user.is_superuser:
        return 'hide_serious'
    else:
        return ''

