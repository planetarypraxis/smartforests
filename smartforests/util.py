from django.contrib.contenttypes import models
from django.db.models.functions import Lower
from smartforests.models import Tag

from commonknowledge.django.cache import django_cached_model


def group_by_title(qs, key='title'):
    def get(x): return getattr(x, key)[0].lower()

    letter = None
    result = []
    head = []

    for item in qs.annotate(lower_title=Lower(key)).order_by('lower_title'):
        l = get(item)
        if letter is None or l != letter:
            letter = l
            head = []
            result.append((letter, head))

        head.append(item)

    return result


def flatten_list(the_list):
    '''
    Takes a 2D list and returns a 1D list
    '''
    return [item for sublist in the_list for item in sublist]
