from commonknowledge.django.cache import django_cached
from logbooks.models.pages import ContributorsIndexPage, LogbookIndexPage, RadioIndexPage, StoryIndexPage
from smartforests.models import MapPage


class ImportantPagesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # @django_cached('important_pages', ttl=60)
    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data['important_pages'] = {
                'contributors': ContributorsIndexPage.objects.first(),
                'map': MapPage.objects.first(),
                'logbooks': LogbookIndexPage.objects.first(),
                'stories': StoryIndexPage.objects.first(),
                'radio': RadioIndexPage.objects.first()
            }

        return response
