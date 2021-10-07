from django.contrib.contenttypes import models
from django.db.models.functions import Lower


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
