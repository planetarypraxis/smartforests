from django.core.paginator import Paginator

from commonknowledge.helpers import safe_to_int


class ChildListMixin:
    page_size = 20

    def get_page_size(self):
        return self.page_size

    def get_child_list_queryset(self, *args, **kwargs):
        return self.get_children().specific()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        paginator = Paginator(
            self.get_child_list_queryset(request), self.get_page_size())
        page = safe_to_int(request.GET.get('page'), 1)
        context['child_page_list'] = paginator.get_page(page)
        context['child_list_paginator'] = paginator

        return context
