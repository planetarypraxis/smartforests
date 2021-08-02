from wagtail.core.models import Page
from commonknowledge.wagtail.models import ChildListMixin


class HomePage(ChildListMixin, Page):
    subpage_types = [
        'logbooks.StoryIndexPage',
        'logbooks.LogbookIndexPage',
    ]
    pass
