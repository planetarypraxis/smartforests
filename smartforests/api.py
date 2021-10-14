# Public REST API to share access to Atlas content
# primarily for use by interactive components of the Atlas website

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
# from wagtail.images.api.v2.views import ImagesAPIViewSet
# from wagtail.documents.api.v2.views import DocumentsAPIViewSet

# Create the router. "wagtailapi" is the URL namespace
wagtail_api_router = WagtailAPIRouter('wagtailapi')

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
wagtail_api_router.register_endpoint('pages', PagesAPIViewSet)
# api_router.register_endpoint('images', ImagesAPIViewSet)
# api_router.register_endpoint('documents', DocumentsAPIViewSet)
