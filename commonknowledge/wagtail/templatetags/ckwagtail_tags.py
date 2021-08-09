from urllib import parse

from wagtail.core.models import Site
from django import template


register = template.Library()


@register.inclusion_tag('ckwagtail/include/menubar.html', takes_context=True)
def menubar(context, **kwargs):
    site = Site.find_for_request(context.get('request'))
    if site is None:
        return

    root = site.root_page
    kwargs['pages'] = root.get_children().in_menu()
    kwargs['request'] = context.get('request')

    return kwargs


@register.simple_tag(takes_context=True)
def next_page_path(context):
    request = context['request']
    params = request.GET.dict()
    params['page'] = '{{#}}'
    return request.path + '?' + \
        parse.urlencode(params).replace('%7B%7B%23%7D%7D', '{{#}}')
