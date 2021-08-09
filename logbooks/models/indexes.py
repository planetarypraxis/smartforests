from functools import reduce
from django.contrib.contenttypes.models import ContentType
from logbooks.models.pages import LogbookIndexPage, LogbookPage, StoryPage
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
from django.contrib.postgres.indexes import GinIndex
from wagtail.core.models import Page


class LogbookPageIndex(models.Model):

    '''
    Denormalized information about pages in this app for fast filtering and retreval.

    Also allows for metadata fields shared between different concrete page types (such as tags) to be
    used to filter for multiple page types.

    Listens to post_save hooks for relevant page models and stores relevant filter metadata.
    '''

    class MetadataType:
        content_type = 'content_type'
        tags = 'tags'

    class Meta:
        indexes = (
            # Inverted image for fast, flexible
            GinIndex(fields=['metadata']),
        )

    related_page_indexes = models.ManyToManyField(
        'LogbookPageIndex', related_name='related_to_page_indexes')
    page = models.OneToOneField(
        Page, on_delete=models.CASCADE, related_name='index_entry')
    metadata = models.JSONField(default=dict, blank=True)
    thumbnail_image = models.ImageField(null=True, blank=True)

    def save(self, *args, regenerate_thumbnails=True, **kwargs):
        super().save(*args, **kwargs)

        if regenerate_thumbnails and hasattr(self.page.specific, 'regenerate_thumbnail'):
            self.thumbnail_image = self.page.specific.regenerate_thumbnail(
                self)
            self.save(regenerate_thumbnails=False)

    @staticmethod
    def get_for_instance(instance: Page):
        idx: LogbookPageIndex
        idx, _ = LogbookPageIndex.objects.get_or_create(page=instance, defaults={
            'metadata': {
                'content_type': ContentType.objects.get_for_model(
                    instance.specific).id
            }
        })

        return idx

    @staticmethod
    @receiver(post_save, sender=StoryPage)
    def handle_story_updated(sender, instance: StoryPage, *args, **kwargs):
        idx = LogbookPageIndex.get_for_instance(instance)

        idx.update_tags(instance)
        idx.update_pages_related_to(LogbookPage)
        idx.update_related_pages(LogbookPage)
        idx.save()

    @staticmethod
    @receiver(post_save, sender=LogbookPage)
    def handle_logbook_updated(sender, instance: StoryPage, *args, **kwargs):
        idx = LogbookPageIndex.get_for_instance(instance)

        idx.update_tags(instance)
        idx.update_pages_related_to(StoryPage)
        idx.update_related_pages(StoryPage)
        idx.save()

    def get_related_page_indexes(self, related_type):
        return LogbookPageIndex.objects.filter(
            ~models.Q(page=self.page),
            or_all(models.Q(metadata__tags__contains=tag)
                   for tag in self.metadata.get('tags', [])),
            metadata__content_type=ContentType.objects.get_for_model(
                related_type).id,
        )

    @staticmethod
    def filter_pages(**filter):
        return LogbookPageIndex._metadata_query(filter, start=LogbookPageIndex.objects)

    def get_related_pages(self, **filter):
        '''
        Return a queryset for a filtered subset of pages related to this one.
        Returns the concrete page type, not the index entry.
        '''
        return LogbookPageIndex._metadata_query(filter, start=self.related_page_indexes)

    def update_tags(self, page):
        '''
        Update the index's tag ids from the main model.
        '''
        self.metadata['tags'] = list(
            tag.id for tag in page.tags.all())
        self.save()

    def update_pages_related_to(self, related_type):
        '''
        Find all pages of type related_type that this one is related to and update them to reference this.

        TODO: Clear out old ones that are no longer related
        '''
        for page in self.get_related_page_indexes(related_type):
            page.related_page_indexes.add(self)

    def update_related_pages(self, related_type):
        '''
        Find all pages of type related_type that this one is related to make sure we reference them.
        '''

        self.related_page_indexes.set(
            self.get_related_page_indexes(related_type))

    @staticmethod
    def _metadata_query(filter, start):
        query = {'metadata__' + key: value for key, value in filter.items()}
        pages = start.filter(**query)

        return Page.objects.filter(index_entry__in=pages).specific()


def or_all(terms):
    terms = tuple(terms)
    q = terms[0]
    for term in terms[1:]:
        q = q | term

    return q
