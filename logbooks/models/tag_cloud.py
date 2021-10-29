from typing import NamedTuple, DefaultDict

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from taggit.models import Tag


class TagCloud(models.Model):
    class Item(NamedTuple):
        id: int
        index: int
        links: list
        count: int = 1

        def score(self):
            return self.count ** 2 + self.index

    class Meta:
        indexes = (models.indexes.Index(fields=('score',)),)

    tag = models.ForeignKey(
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

    @staticmethod
    def reindex():
        for tag in Tag.objects.iterator():
            TagCloud.handle_tag_association(Tag, tag)

    @staticmethod
    def get_start(limit=100, clouds=5):
        '''
        Return a merged tag cloud based on the best-scoring clouds (most densely connected nodes) we know about.
        '''

        clouds = TagCloud.objects.order_by('-score')[:clouds]
        return TagCloud.get_related([cloud.tag for cloud in clouds], limit=limit)

    @staticmethod
    def get_related(tags, limit=100):
        '''
        Given a list of start tags, merge their associated tag clouds and return a json object describing each tag.
        '''

        lookup = DefaultDict(list)

        for tag in tags:
            cloud: TagCloud = tag.tag_cloud
            if cloud is None:
                continue

            for item in cloud.tag_items:
                lookup[item.id].append(item)

        stack = [
            tag.id
            for tag in tags
            if tag.tag_cloud is not None
            and len(tag.tag_cloud.value) > 0
        ]
        merged_cloud = {}

        i = 0

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

        return TagCloud.to_json(sorted(merged_cloud.items(), reverse=True, key=TagCloud.Item.score))

    @staticmethod
    def to_json(items):
        '''
        Given a list of TagCloud.Item objects, efficiently fetch all the associated Tags and return a json object describing both the tags and their location in the tag cloud
        '''

        lookup = {
            tag.id: tag
            for tag in TagCloud.objects.filter(id__in=[item.id for item in items])
        }

        def to_json(item: TagCloud.Item):
            model = lookup[item.id]
            return {
                'name': model.name,
                'slug': model.slug,
                'id': item.id,
                'links': item.links,
                'score': item.score
            }

        return [
            to_json(item) for item in items
        ]

    @ staticmethod
    @ receiver(m2m_changed, sender=Tag)
    def handle_tag_association(sender, instance: Tag, **kwargs):
        '''
        Breadth-first search on tags related to the saved tag, limited to 100.

        Tags are assigned a score based on how densely interconnected with other tags in the cluster they are, with proximity to the start point used to distinguish.

        Metadata about the tag's surrounding graph is saved as a json object (TagCloud.Item).
        '''

        from logbooks.models.snippets import AtlasTag

        stack = [instance]
        visited = {}

        i = 0
        while len(stack) > 0 and i < 100:
            tag = stack.pop(0)
            if tag.id in visited:
                visited[tag.id].count += 1
                continue

            visited[tag.id] = TagCloud.Item(index=i, id=tag, links=[])

            pages = Page.objects.filter(tagged_items__tag=tag)

            for tagged_item in AtlasTag.objects.filter(content__object__in=pages):
                stack.append(tagged_item.tag)
                visited[tag.id].links.append(tagged_item.id)

            i += 1

        cloud, _ = TagCloud.objects.get_or_create(tag=instance)
        cloud.value = list(
            sorted(visited.items(), key=TagCloud.Item.score, reverse=True))
        cloud.score = sum(visited.items(), key=TagCloud.Item.score)
        cloud.save()
