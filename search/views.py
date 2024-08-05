from commonknowledge.wagtail.search.views import BasicSearchView
from smartforests.views import LocaleFromLanguageCode


class SearchView(BasicSearchView, LocaleFromLanguageCode):
    template_name = 'search/basic.html'
    search_highlight_field = 'indexed_streamfield_text'

    def search_queryset(self, qs, search_query):
        res = super().search_queryset(qs, search_query)
        results = list(res) + list(qs.autocomplete(search_query))
        locale = self.get_locale()
        self.request.LANGUAGE_CODE = locale.language_code
        localized_pages = list(
            set([page.get_translation_or_none(locale).specific if page.get_translation_or_none(locale) else page for page in results]))
        return localized_pages

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale = self.get_locale()
        context["LANGUAGE_CODE"] = locale.language_code
        return context
