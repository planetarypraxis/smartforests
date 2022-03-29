from math import ceil, floor
from random import shuffle
from typing import DefaultDict
from dataclasses import dataclass

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from logbooks.tasks import regenerate_tag_cloud
from wagtail.core.models import Page
from logbooks.models.snippets import AtlasTag
from smartforests.models import Tag


class TagCloud(models.Model):
    '''
    The 'heat' (score) for a tag is calculated by counting many times other tags appear in pages that include this tag, and also further afield neighbouring.
    The further afield the neighbouring tags are (degrees of separation by page), the lower the score modifier.
    The different clouds for the different tags are combined on the homepage, so that each tag's score is an aggregate of all the clouds' scores for that tag — a tag is 'seen' by its relationship to the other tags.
    This is a bit complicated to say but, suffice to say, it's a measure of 'centrality' of a tag amongst the page content.
    '''

    @dataclass
    class Item:
        id: int
        # Index in a breadth-first search from start (approximately used as 'distance')
        index: int
        links: list
        # Number of pages with this tag
        count: int = 1

        def to_json(self, tag=None):
            if tag:
                json = self.to_json()
                json['name'] = tag.name
                json['slug'] = tag.slug
                json['score'] = self.score()
                return json

            else:
                return dict(self.__dict__)

        def score(self):
            # Taking index as an approximation for 'distance' from the starting Item
            # the further away, the smaller the distance_factor
            # and hence the lower the overall score
            distance_factor = 1 / (self.index + 1)
            # We multiple the count (of pages with this tag) by the distance_factor
            # to get a rough score of 'centrality' for this tag
            return self.count * distance_factor

    class Meta:
        indexes = (models.indexes.Index(fields=('score',)),)

    tag = models.OneToOneField(
        Tag, on_delete=models.CASCADE, related_name='tag_cloud')
    value = models.JSONField(default=list, blank=True)
    score = models.IntegerField(default=0, blank=True)

    @property
    def tag_items(self):
        return tuple(
            TagCloud.Item(**json)
            for json
            in self.value
        )

    @property
    def tag_set(self):
        return set(
            item['id']
            for item
            in self.value
        )

    @staticmethod
    def reindex():
        # Select tags that have published pages associated with them
        tags_in_use = Tag.objects.filter(
            logbooks_atlastag_items__content_object__live=True
        )

        # Delete tag clouds without a published page
        TagCloud.objects.exclude(tag__in=tags_in_use).delete()

        # Reindex the tag clouds for these tags
        for tag in tags_in_use:
            TagCloud.build_for_tag(tag)

    @staticmethod
    def get_start(limit=100, clouds=100):
        '''
        Return a merged tag cloud based on the best-scoring clouds (most densely connected nodes) we know about.
        '''

        clouds = TagCloud.objects\
            .order_by('-score')\
            .filter(score__gt=1)[:clouds]

        cloud_tags = [cloud.tag for cloud in clouds]
        shuffle(cloud_tags)
        return TagCloud.get_related(cloud_tags[:25], limit=limit)

    @staticmethod
    def get_related(tags, limit=100):
        '''
        Given a list of start tags, merge their associated tag clouds and return a json object describing each tag.
        '''

        lookup = DefaultDict(list)

        def get_cloud(tag) -> TagCloud:
            try:
                return tag.tag_cloud
            except ObjectDoesNotExist:
                return None

        for tag in tags:
            cloud = get_cloud(tag)

            if cloud is None:
                continue

            for item in cloud.tag_items:
                lookup[item.id].append(item)

        stack = [
            tag.id
            for tag in tags
            if get_cloud(tag) is not None
            and len(get_cloud(tag).value) > 0
        ]
        merged_cloud = {}

        i = 0

        # Note that this is a very hot loop, so don't make any database queries here!
        while len(stack) > 0 and i < limit:
            tag_id = stack.pop(0)

            if tag_id in merged_cloud:
                merged_cloud[tag_id].count += 1
                continue

            merged_links = set()

            for item in lookup[tag_id]:
                for link in item.links:
                    merged_links.add(link)
                    stack.append(link)

            merged_cloud[tag_id] = TagCloud.Item(
                id=item.id, index=i, links=list(merged_links))
            i += 1

        # Filter out any tags where the pages don't exist
        # Do it here in bulk as otherwise we make potentially 10,000s of database queries!
        empty_tags = set(
            tag.id for tag in Tag.objects.filter(
                id__in=[val.id for val in merged_cloud.values()],
            ).exclude(
                logbooks_atlastag_items__content_object__live=True
            )
        )
        ok_tags = (val for val in merged_cloud.values()
                   if val.id not in empty_tags)

        # If there were tags where the paged didn't exist, mark the source clouds for regeneration
        if len(empty_tags) > 0:
            for tag in tags:
                regenerate_tag_cloud(tag.id)

        return TagCloud.to_json(sorted(ok_tags, reverse=True, key=TagCloud.Item.score))

    @staticmethod
    def to_json(items):
        '''
        Given a list of TagCloud.Item objects, efficiently fetch all the associated Tags and return a json object describing both the tags and their location in the tag cloud
        '''

        lookup = {
            tag.id: tag
            for tag in Tag.objects.filter(id__in=[item.id for item in items])
        }

        return [
            item.to_json(lookup[item.id]) for item in items
            if item.id in lookup
        ]

    @staticmethod
    def build_for_tag(instance: Tag):
        '''
        Breadth-first search on tags related to the saved tag, limited to 100.

        Tags are assigned a score based on how densely interconnected with other tags in the cluster they are, with proximity to the start point used to distinguish.

        Metadata about the tag's surrounding graph is saved as a json object (TagCloud.Item).
        '''
        from logbooks.models.snippets import AtlasTag

        stack = [instance]
        visited = {}

        i = 0
        # Note that this is a very hot loop, so don't make any database queries here!
        while len(stack) > 0 and i < 100:
            tag = stack.pop(0)

            if tag.id in visited:
                # Increment the score for this related tag
                visited[tag.id].count += 1
                continue

            visited[tag.id] = TagCloud.Item(index=i, id=tag.id, links=[])

            # Get all pages for this tag
            pages = Page.objects.filter(tagged_items__tag=tag).live()

            # Pages that link to — or are tagged with — with this tag
            taggings = AtlasTag.objects.filter(content_object__in=pages)

            # Get all tags that are linked to by these pages
            # so that their score can be incremented
            for tagged_item in taggings:
                if tagged_item.tag_id != tag.id:
                    stack.append(tagged_item.tag)
                    visited[tag.id].links.append(tagged_item.tag_id)

            i += 1

        cloud, _ = TagCloud.objects.get_or_create(tag=instance)
        cloud.value = list(
            item.to_json() for item
            in sorted(visited.values(), key=TagCloud.Item.score, reverse=True)
            if item.id != instance.id
        )

        cloud.score = sum(x.score() for x in visited.values())
        cloud.save()
        return cloud
