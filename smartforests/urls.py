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
from wagtail_footnotes import urls as footnotes_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from django.conf.urls.i18n import i18n_patterns

from commonknowledge.django import rest
from .api import wagtail_api_router

from search import views as search_views
from smartforests import views as sf_views
from logbooks import views as logbook_views


urlpatterns = [
    path('django-admin/', admin.site.urls),
    re_path(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.SearchView.as_view(), name='search'),
    path("footnotes/", include(footnotes_urls)),
    path('_frame/<page_id>/', sf_views.frame_content),
    path('_tags/<slug>/', logbook_views.tag_panel),
    path('_filters/', sf_views.filters_frame),
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
]

urlpatterns += i18n_patterns(
    re_path(r'^', include(wagtail_urls)),
)

urlpatterns += [
    re_path(r'', include(wagtail_content_import_urls)),
]
