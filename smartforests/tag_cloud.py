import sys
from django.db.models import Q
from wagtail.models.i18n import Locale
from logbooks import models
from smartforests.models import Tag, TagLink


def get_nodes_and_links(tags=None):
    locale = Locale.get_active()

    tag_links = TagLink.objects.select_related("source", "target").filter(
        source__locale=locale, target__locale=locale, relatedness__gt=0
    )

    if tags is not None:
        tag_links = tag_links.filter(Q(source__in=tags) | Q(target__in=tags))

    tags_by_id = {}

    links = []

    for tag_link in tag_links:
        tags_by_id[tag_link.source.id] = tag_link.source
        tags_by_id[tag_link.target.id] = tag_link.target

        links.append(
            {
                "source": tag_link.source.id,
                "target": tag_link.target.id,
                "value": tag_link.relatedness,
            }
        )

    nodes = [
        {
            "id": tag.id,
            "name": tag.name,
            "slug": tag.slug,
            "count": tag.cached_page_count,
        }
        for tag in tags_by_id.values()
    ]
    nodes = sorted(nodes, key=lambda x: x["count"], reverse=True)
    return {
        "nodes": nodes,
        "links": links,
        "max_count": nodes[0]["count"] if nodes else 0,
    }


def page_classes():
    return [
        models.LogbookPage,
        models.LogbookEntryPage,
        models.StoryPage,
        models.EpisodePage,
    ]


def recalculate_taglinks(tag_id=None):
    tags = Tag.objects.order_by("id")
    if tag_id is not None:
        tags = tags.filter(id=tag_id)

    n = len(tags)
    i = 0
    for source_tag in tags:
        source_tag.cached_page_count = count_pages(source_tag)
        source_tag.save()

        target_tags = Tag.objects.filter(
            id__gt=source_tag.id, locale=source_tag.locale
        ).order_by("id")

        for target_tag in target_tags:
            total_count = count_or(source_tag, target_tag)
            shared_count = count_and(source_tag, target_tag)
            relatedness = round(shared_count / total_count, 4) if total_count > 0 else 0
            link, created = TagLink.objects.update_or_create(
                source=source_tag,
                target=target_tag,
                defaults={"relatedness": relatedness},
            )
            TagLink.objects.update_or_create(
                source=target_tag,
                target=source_tag,
                defaults={"relatedness": relatedness},
            )
            print(f"{'Created' if created else 'Updated'} TagLink: {link}")

        i += 1
        print(f"Complete: {round(i * 100 / n, 1)}%", file=sys.stderr)


def count_pages(tag):
    count = 0
    for page_class in page_classes():
        c = len(
            page_class.objects.filter(locale=tag.locale).filter(tagged_items__tag=tag)
        )
        count += c

    return count


def count_and(tag_a, tag_b):
    count = 0
    for page_class in page_classes():
        c = len(
            page_class.objects.filter(locale=tag_a.locale)
            .filter(tagged_items__tag=tag_a)
            .filter(tagged_items__tag=tag_b)
            .distinct()
        )
        count += c
    return count


def count_or(tag_a, tag_b):
    count = 0
    for page_class in page_classes():
        c = len(
            page_class.objects.filter(
                locale=tag_a.locale, tagged_items__tag__in=[tag_a, tag_b]
            ).distinct()
        )
        count += c
    return count
