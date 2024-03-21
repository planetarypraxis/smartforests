from io import StringIO
import sys
from collections import defaultdict
from django.core.management.base import BaseCommand
from logbooks.models import (
    LogbookPage,
    LogbookEntryPage,
    StoryPage,
    EpisodePage,
)
from smartforests.models import Tag


class Command(BaseCommand):
    help = """
    Calculate the similarity matrix of tags and print it.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tag_count_cache = {}

    def handle(self, *args, **options):
        matrix = defaultdict(dict)
        tags = Tag.objects.order_by("id")
        tags_by_id = {}
        n = len(tags)
        i = 0
        for tag in tags:
            tags_by_id[tag.id] = tag
            tag_count = self.count_articles(tag)
            other_tags = Tag.objects.filter(id__gt=tag.id).order_by("id")
            for other_tag in other_tags:
                tags_by_id[other_tag.id] = other_tag
                other_tag_count = self.count_articles(other_tag)
                total_count = self.count_or(tag, other_tag)
                shared_count = self.count_and(tag, other_tag)
                similarity = (
                    round(shared_count / total_count, 4) if tag_count > 0 else 0
                )
                matrix[tag.id][other_tag.id] = {
                    "tag_count": tag_count,
                    "other_tag_count": other_tag_count,
                    "total_count": total_count,
                    "shared_count": shared_count,
                    "similarity": similarity,
                }
                if similarity > 0:
                    print(
                        f"Tag {tag} <-> {other_tag}: {matrix[tag.id][other_tag.id]}",
                        file=sys.stderr,
                    )
            i += 1
            print(f"Complete: {round(i * 100 / n, 1)}%", file=sys.stderr)
        print(
            "Tag A ID,Tag A Name,Tag A Locale,Tag A Count,Tag B ID,Tag B Name,Tag B Locale,Tag B Count,Shared Count,Total Count,Similarity"
        )
        for tag_id, other_ids in matrix.items():
            for other_id, scores in other_ids.items():
                tag = tags_by_id[tag_id]
                other_tag = tags_by_id[other_id]
                print(
                    f"{tag.id},{tag.name},{tag.locale.language_code},{scores['tag_count']},"
                    f"{other_tag.id},{other_tag.name},{other_tag.locale.language_code},{scores['other_tag_count']},"
                    f"{scores['shared_count']},{scores['total_count']},{scores['similarity']}"
                )

    def count_articles(self, tag_a):
        if tag_a.id in self.tag_count_cache:
            return self.tag_count_cache[tag_a.id]

        count = 0
        for page_class in [LogbookPage, LogbookEntryPage, StoryPage, EpisodePage]:
            c = len(page_class.objects.filter(tagged_items__tag=tag_a))
            count += c

        self.tag_count_cache[tag_a.id] = count

        return count

    def count_and(self, tag_a, tag_b):
        count = 0
        for page_class in [LogbookPage, LogbookEntryPage, StoryPage, EpisodePage]:
            c = len(
                page_class.objects.filter(tagged_items__tag=tag_a)
                .filter(tagged_items__tag=tag_b)
                .distinct()
            )
            count += c
        return count

    def count_or(self, tag_a, tag_b):
        count = 0
        for page_class in [LogbookPage, LogbookEntryPage, StoryPage, EpisodePage]:
            c = len(
                page_class.objects.filter(
                    tagged_items__tag__in=[tag_a, tag_b]
                ).distinct()
            )
            count += c
        return count
