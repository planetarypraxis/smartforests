from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db.models import Q, Subquery


def get_children_of_type(parent, *types):
    if len(types) == 1:
        t = types[0]
        return t.objects.live().child_of(parent)

    content_types = tuple(ContentType.objects.get_for_model(t) for t in types)
    return parent.get_children().filter(content_type__in=content_types)


def model_subclasses(mclass):
    '''	Retrieve all model subclasses for the provided class
    '''
    return [m for m in apps.get_models() if issubclass(m, mclass)]


def abstract_page_query_filter(mclass, filter_params, pk_attr='page_ptr'):
    '''
    Create a filter query that will be applied to all children of the provided
    abstract model class. Returns None if a query filter cannot be created.

    @returns Query or None
    '''
    if not mclass._meta.abstract:
        raise ValueError('Provided model class must be abstract')

    pclasses = model_subclasses(mclass)

    # Filter for pages which are marked as features
    if len(pclasses):

        qf = Q(pk__in=Subquery(pclasses[0].objects.filter(
            **filter_params).values(pk_attr)))
        for c in pclasses[1:]:
            qf |= Q(pk__in=Subquery(c.objects.filter(
                **filter_params).values(pk_attr)))

        return qf

    return None
