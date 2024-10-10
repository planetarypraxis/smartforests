from datetime import timedelta, datetime
from urllib import parse
import json
import human_readable

from webpack_loader.templatetags import webpack_loader
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe
from django.conf import settings
from django import template
from smartforests.models import Tag

register = template.Library()


@register.simple_tag
def webpack_bundle(name, type='js'):
    if settings.DEBUG:
        if type == 'js':
            return mark_safe(f'<script defer src="http://localhost:8080/{name}.js"></script>')
        else:
            return mark_safe('')

    else:
        return mark_safe('\n'.join(webpack_loader.utils.get_as_tags(name, type, attrs="defer")))


@register.simple_tag(takes_context=True)
def infinite_scroll_container(context, item_selector='iscroll_item', **kwargs):
    request: HttpRequest = context.get('request', None)
    if request is None:
        return

    params = request.GET.dict()
    params['page'] = '{{#}}'
    next_path_template = request.path + '?' + \
        parse.urlencode(params).replace('%7B%7B%23%7D%7D', '{{#}}')

    config = {
        'path': next_path_template,
        'append': item_selector,
        'history': False
    }

    return mark_safe(f'data-infinite-scroll=\'{json.dumps(config)}\'')


@register.simple_tag(takes_context=True)
def qs_link(context, key, value, **kwargs):
    request: HttpRequest = context.get('request', None)
    if request is None:
        return

    params = request.GET.dict()
    if value is None:
        params.pop(key, None)
    else:
        params[key] = value

    return "?" + parse.urlencode(params)


@register.simple_tag(takes_context=True)
def with_tag_filter(context, url: str, language_code: str):
    request: HttpRequest = context.get("request", None)
    if request is None:
        return url

    current_tag_slug = request.GET.get("filter")
    if not current_tag_slug:
        return url

    tag = Tag.objects.filter(slug=current_tag_slug).first()
    if not tag:
        return url

    translated_tag = Tag.objects.filter(
        translation_key=tag.translation_key, locale__language_code=language_code
    ).first()
    if not translated_tag:
        return url

    if parse.urlparse(url).query:
        return f"{url}&filter={translated_tag.slug}"

    return f"{url}?filter={translated_tag.slug}"


# https://stackoverflow.com/questions/32795907/how-to-access-the-next-and-the-previous-elements-in-a-django-template-forloop


@register.filter
def next(some_list, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) + 1]  # access the next element
    except:
        return ''  # return empty string in case of exception


@register.filter
def previous(some_list, current_index):
    """
    Returns the previous element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) - 1]  # access the previous element
    except:
        return ''  # return empty string in case of exception


def get_duration(secs):
    if type(secs) is not float and type(secs) is not int:
        secs = secs.total_seconds()
    delta = timedelta(seconds=secs)
    return delta


@register.filter()
def duration_words(secs):
    '''
    Return as "3 minutes, 20 seconds
    '''
    delta = get_duration(secs)
    string = human_readable.precise_delta(delta, minimum_unit="seconds")
    return string.replace(" and ", ", ")


@register.filter()
def duration_numbers(secs):
    '''
    Return as "0:00:00"
    '''
    delta = get_duration(secs)
    d1 = datetime(2000, 1, 1, 0, 0, 0)
    d2 = d1 + delta
    return d2-d1


@register.filter()
def get_class(value):
    return value.__class__.__name__