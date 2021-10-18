# import debug_toolbar
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail_transfer import urls as wagtailtransfer_urls
from wagtail_content_import import urls as wagtail_content_import_urls

from commonknowledge.django import rest
from .api import wagtail_api_router

from search import views as search_views


urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.SearchView.as_view(), name='search'),
    # path('api/', include(rest.get_urls())),
    # path('__debug__/', include(debug_toolbar.urls)),
]


if settings.DEBUG:
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('api/v2/', wagtail_api_router.urls),
    re_path(r'^wagtail-transfer/', include(wagtailtransfer_urls)),
    re_path(r'^', include(wagtail_urls)),
]

urlpatterns += [
    re_path(r'', include(wagtail_content_import_urls)),
]
