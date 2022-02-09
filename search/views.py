from commonknowledge.wagtail.search.views import BasicSearchView
from smartforests.views import LocaleFromLanguageCode


class SearchView(BasicSearchView, LocaleFromLanguageCode):
    template_name = 'search/basic.html'
    search_highlight_field = 'indexed_streamfield_text'

    def search_queryset(self, qs, search_query):
        res = super().search_queryset(qs, search_query)
        results = list(res) + list(qs.autocomplete(search_query))
        locale = self.get_locale()
        localized_pages = list(
            set([page.get_translation_or_none(locale).specific or page for page in results]))
        return localized_pages
