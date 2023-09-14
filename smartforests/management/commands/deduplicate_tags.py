from django.core.management.base import BaseCommand
from logbooks.models import (
    LogbookPage,
    LogbookEntryPage,
    StoryPage,
    EpisodePage,
)


class Command(BaseCommand):
    help = """
    Remove duplicated tags from pages (e.g. if a page has "datafication" (en) and "datafication" (fr), and it
    is an English page, remove the French tag).
    """

    def handle(self, *args, **options):
        for page_class in [LogbookPage, LogbookEntryPage, StoryPage, EpisodePage]:
            pages = page_class.objects.all().specific()
            for page in pages:
                tags = list(page.tags.all())
                ok_tags = [tag for tag in tags if tag.locale == page.locale]
                page.tags.set(ok_tags)
                page.save()
                print(f"Fixed tags for {page}")
