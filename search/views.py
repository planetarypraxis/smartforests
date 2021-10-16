from commonknowledge.wagtail.search.views import BasicSearchView


class SearchView(BasicSearchView):
    template_name = 'search/basic.html'
    search_highlight_field = 'indexed_streamfield_text'

    def search_queryset(self, qs, search_query):
        res = super().search_queryset(qs, search_query)
        return list(res) + list(qs.autocomplete(search_query))
