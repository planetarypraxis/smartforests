from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail_content_import import urls as wagtail_content_import_urls
from wagtail_footnotes import urls as footnotes_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from commonknowledge.django import rest
from .api import wagtail_api_router

from search import views as search_views
from smartforests import views as sf_views
from logbooks import views as logbook_views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('django-admin/', admin.site.urls),
    re_path(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path("footnotes/", include(footnotes_urls)),
    path('search/', search_views.SearchView.as_view(), name='search'),
    path('_filters/', sf_views.filters_frame),
    path('favicon.ico',
         RedirectView.as_view(url='/static/img/favicon.png', permanent=True)),
    # path('api/', include(rest.get_urls())),
    path('400', TemplateView.as_view(template_name='400.html')),
    path('403', TemplateView.as_view(template_name='403.html')),
    path('404', TemplateView.as_view(template_name='404.html')),
    path('500', TemplateView.as_view(template_name='500.html')),
]

if settings.DEBUG:
    if settings.USE_DEBUG_TOOLBAR:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('api/v2/', wagtail_api_router.urls),
    path('api/v2/geo/',
         logbook_views.MapSearchViewset.as_view({'get': 'list'}), name='geo'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += i18n_patterns(
    path('_frame/<page_id>/', sf_views.frame_content),
    path('_tags/<slug>/', logbook_views.tag_panel),
    path('_metadata/<page_id>/', logbook_views.metadata),
    path('_metadata/<page_id>/toggle_user/<user_id>/', logbook_views.metadata),
    re_path(r'^', include(wagtail_urls)),
)

urlpatterns += [
    re_path(r'', include(wagtail_content_import_urls)),
]
