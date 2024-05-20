from collections import defaultdict
from django.contrib.contenttypes import models
from django.db.models.functions import Lower
from django.db.models import QuerySet
from smartforests.models import Tag
from commonknowledge.django.cache import django_cached_model
from urllib.parse import urljoin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from wagtail.models import Locale


def group_by_tag_name(qs: QuerySet):
    result = defaultdict(set)

    translation_keys = qs.values_list("translation_key", flat=True)
    localized_items = qs.model.objects.filter(
        locale=Locale.get_active(), translation_key__in=translation_keys
    )

    for item in localized_items:
        letter = item.name[0]
        result[letter].add(item)

    groups = [
        (letter, sorted(tags, key=lambda t: t.name.lower()))
        for letter, tags in result.items()
    ]
    ordered = sorted(groups, key=lambda x: x[0].lower())
    return ordered


def flatten_list(the_list):
    """
    Takes a 2D list and returns a 1D list
    """
    return [item for sublist in the_list for item in sublist]


def ensure_list(list_or_el):
    if isinstance(list_or_el, list):
        return list_or_el
    if isinstance(list_or_el, tuple):
        return list(list_or_el)
    return [
        list_or_el,
    ]


def static_file_absolute_url(filename: str) -> str:
    return urljoin(settings.BASE_URL, staticfiles_storage.url(filename))
