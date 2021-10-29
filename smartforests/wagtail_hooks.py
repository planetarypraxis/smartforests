from django.conf import settings
from django.conf.urls.static import static
from django.template.loader import render_to_string
from django.utils.html import format_html
from wagtail.core import hooks


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    """Add /static/css/custom.js to the admin."""
    if not settings.POSTHOG_PUBLIC_TOKEN:
        return
    else:
        return render_to_string('posthog_snippet.html', {
            'environment': settings
        })
