from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail_content_import import urls as wagtail_content_import_urls
from wagtail_footnotes import urls as footnotes_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# from commonknowledge.django import rest
from commonknowledge.django import service
from .api import wagtail_api_router

from search import views as search_views
from smartforests import views as sf_views
from logbooks import views as logbook_views
from django.views.generic.base import RedirectView


urlpatterns = [
    path("robots.txt", sf_views.robots),
    path("admin/tag-autocomplete/smartforests/tag/", sf_views.tag_autocomplete_view),
    path("django-admin/", admin.site.urls),
    re_path(r"^admin/autocomplete/", include(autocomplete_admin_urls)),
    # Override the history view to fix bug where translation history doesn't show diff buttons
    path(
        "admin/pages/<int:page_id>/history/",
        logbook_views.PageHistoryView.as_view(),
        name="history",
    ),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("footnotes/", include(footnotes_urls)),
    path("search/", search_views.SearchView.as_view(), name="search"),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/img/favicon.png", permanent=True),
    ),
    # path('api/', include(rest.get_urls())),ScheduledPublishViewSet
    path("400", TemplateView.as_view(template_name="400.html")),
    path("403", TemplateView.as_view(template_name="403.html")),
    path("404", TemplateView.as_view(template_name="404.html")),
    path("500", TemplateView.as_view(template_name="500.html")),
    path("smoke/", sf_views.smoke_view),
    path("smoke/site/", sf_views.smoke_site_view),
    path("smoke/home/", sf_views.smoke_home_view),
    path("smoke/about/", sf_views.smoke_about_view),
]

urlpatterns += i18n_patterns(
    path("_filters/", sf_views.filters_frame),
)

if settings.DEBUG:
    if settings.USE_DEBUG_TOOLBAR:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("api/v2/", wagtail_api_router.urls),
    path(
        "api/v2/geo/",
        logbook_views.MapSearchViewset.as_view({"get": "list"}),
        name="geo",
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]

urlpatterns += i18n_patterns(
    path("_frame/<page_id>/", sf_views.frame_content),
    path("_tags/<slug>/", logbook_views.tag_panel),
    path("_metadata/<page_id>/", logbook_views.metadata),
    path("_metadata/<page_id>/toggle_user/<user_id>/", logbook_views.metadata),
    path("_page_tagcloud/<page_id>/", logbook_views.page_tagcloud),
    re_path(r"^", include(wagtail_urls)),
)

urlpatterns += [
    re_path(r"", include(wagtail_content_import_urls)),
]

urlpatterns += [
    path("api/service/publish", service.publish),
]

def trigger_error(request):
    division_by_zero = 1 / 0 

urlpatterns += [
    path('api/sentry-debug/', trigger_error),
]