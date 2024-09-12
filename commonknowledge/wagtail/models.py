from typing import NamedTuple
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Subquery, OuterRef
from treebeard.mp_tree import get_result_class

from commonknowledge.helpers import safe_to_int


class SortOption(NamedTuple):
    label: str
    slug: str
    ordering: str

    @staticmethod
    def to_field_choices(opts):
        return tuple((opt.slug, opt.label) for opt in opts)


class ChildListMixin:
    allow_search = False
    sort_options = (
        SortOption("Newest", "most_recent", "-published_at"),
        SortOption("Oldest", "oldest", "published_at"),
        SortOption("A-Z", "a-z", "title"),
        SortOption("Z-A", "z-a", "-title"),
    )

    def get_sort(self, request):
        if len(self.sort_options) == 0:
            return None
        return next(
            (opt for opt in self.sort_options if opt.slug == request.GET.get("sort")),
            self.sort_options[0],
        )

    def get_search_queryset(self, request, qs):
        q = request.GET.get("query")
        if q and self.allow_search:
            sort = self.get_sort(request)
            return qs.search(q, order_by_relevance=sort is None)

    def get_child_list_queryset(self, *args, **kwargs):
        return self.get_children().live().specific()

    def get_page_size(self):
        return 10000

    def get_filters(self, request):
        return None

    def get_filter_form(self, request):
        return None

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        qs = self.get_child_list_queryset(request)

        if request.user.is_anonymous:
            qs = qs.public()

        filter = self.get_filters(request)
        sort = self.get_sort(request)

        if filter:
            if isinstance(filter, dict):
                qs = qs.filter(**filter)
            else:
                qs = qs.filter(filter)
            # Complex filters can introduce joins that create duplicate results
            # Fix with distinct()
            qs = qs.distinct()

        if sort:
            # For publish date orderings, order by original page publish date, not translation date
            if "published_at" in sort.ordering:
                ChildModel = get_result_class(self)
                translations = ChildModel.objects.filter(
                    translation_key=OuterRef("translation_key")
                ).order_by("first_published_at")

                qs = qs.annotate(
                    published_at=Subquery(translations.values("first_published_at")[:1])
                )
            qs = qs.order_by(sort.ordering)
            print(f"query {qs.query}")

        search = self.get_search_queryset(request, qs)

        if search is None:
            paginator = Paginator(qs, self.get_page_size())
        else:
            paginator = Paginator(search, self.get_page_size())

        page = safe_to_int(request.GET.get("page", 1), 1)

        empty = request.GET.get("empty", False)
        show_empty_page_for_no_results = empty == "1" or int(empty) >= 1
        if show_empty_page_for_no_results:
            try:
                context["child_list_page"] = paginator.page(page)
            except PageNotAnInteger:
                context["child_list_page"] = paginator.page(1)
            except EmptyPage:
                context["child_list_page"] = None

            context["child_list_paginator"] = paginator
        else:
            context["child_list_page"] = paginator.get_page(page)

        context["filter_form"] = self.get_filter_form(request)

        return context
