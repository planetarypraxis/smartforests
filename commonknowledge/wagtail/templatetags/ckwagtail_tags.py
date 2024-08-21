import re
import logging
from urllib import parse
from wagtail.blocks.base import Block

from wagtail.models import Site, Locale
from wagtailmenus.templatetags.menu_tags import main_menu, flat_menu
from django import template
from django.utils.safestring import SafeText, mark_safe
from commonknowledge.helpers import safe_to_int
from django import template
from smartforests.models import Tag
from django.utils.html import format_html

register = template.Library()

logger = logging.getLogger(__name__)


@register.inclusion_tag("ckwagtail/include/menubar.html", takes_context=True)
def menubar(context, **kwargs):
    request = context.get("request", None)
    if request is None:
        return
    site = Site.find_for_request(request)
    if site is None:
        return

    root = site.root_page
    kwargs["pages"] = root.get_children().in_menu()
    kwargs["request"] = request

    return kwargs


@register.simple_tag(takes_context=True)
def next_page_path(context):
    request = context.get("request", None)
    if not request:
        return
    params = request.GET.dict()

    # Return the next page
    params["page"] = safe_to_int(params.get("page", 1), 1) + 1

    # This informs our ChildListMixin not to return any data after the last page.
    params["empty"] = "1"

    return mark_safe("?" + parse.urlencode(params))


@register.simple_tag(takes_context=True)
def render_streamfield(context, value, *args, **kwargs):
    def get_context(self, value, *args, **kwargs):
        return dict(
            context.flatten(),
            **{
                "self": value,
                self.TEMPLATE_VAR: value,
            },
        )

    Block.get_context = get_context
    return str(value)


@register.simple_tag(takes_context=True)
def bulk_action_classes(context):
    request = context.get("request", None)
    if not request.user.is_superuser:
        return "hide_serious"
    else:
        return ""


@register.simple_tag(takes_context=True)
def safe_main_menu(context, *args, **kwargs):
    try:
        return main_menu(context, *args, **kwargs)
    except Exception as e:
        print(f"Menu error: {e}")
        return ""


@register.simple_tag(takes_context=True)
def safe_flat_menu(context, *args, **kwargs):
    try:
        return flat_menu(context, *args, **kwargs)
    except Exception as e:
        print(f"Flat menu error: {e}")
        return ""


@register.simple_tag(takes_context=True)
def highlight_tags(context, content: SafeText):
    request = context.get("request")
    if request and hasattr(request, "highlighted_tag_ids"):
        highlighted_tag_ids = request.highlighted_tag_ids
    else:
        highlighted_tag_ids = []

    locale = Locale.get_active()

    content = str(content)

    splitter = r"[ !#()\;:'\",./<>&]"

    logger.debug(f"Content to highlight: {content}")
    logger.debug(f"Already highlighted: {highlighted_tag_ids}")

    # Remove links and re-insert after highlighting tags
    # Matching tags inside <a> tags breaks them
    links = re.findall(r"<a[^<]*</a>", content, re.IGNORECASE)
    for i, link in enumerate(links):
        content = content.replace(link, f"[#~{i}~#]")

    tags = Tag.objects.filter(locale=locale).exclude(id__in=highlighted_tag_ids)

    logger.debug(f"Tags found: {list(tags)}")

    # Sort tags by length to handle multi-word tags correctly
    sorted_tags = sorted(tags, key=lambda tag: len(tag.name), reverse=True)

    for tag in sorted_tags:
        replace = rf"""
        \1<span class="filter-tag filter-tag-inline">
            <a class="text-decoration-none" 
               data-smartforests-sidepanel-open="#tagpanel-offcanvas"
               data-turbo-frame="tagpanel-turboframe"
               href="/{locale.language_code}/_tags/{tag.slug}/">
                \2
            </a>
        </span>\3
        """.strip()

        prev_content = content
        content = re.sub(
            rf"({splitter})({re.escape(tag.name)})({splitter})",
            replace,
            content,
            count=1,
            flags=re.IGNORECASE,
        )

        if content != prev_content:
            # Only highlight a tag once per request
            logger.info(f"Highlighted tag: {tag}")
            highlighted_tag_ids.append(tag.id)
        else:
            logger.debug(f"Did not find {tag.id}: {tag.name} in content")

    for i, link in enumerate(links):
        content = content.replace(f"[#~{i}~#]", link)

    if request:
        request.highlighted_tag_ids = highlighted_tag_ids

    return mark_safe(content)


@register.simple_tag
def log_fields(obj):
    if obj:
        fields = vars(obj)
        print("Fields available in page.map_image:")
        for field, value in fields.items():
            print(f"{field}: {value}")
        return fields
    return {}


@register.simple_tag
def log_page_fields(page):
    fields = vars(page).items()
    html = "<ul>"
    for field_name, value in fields:
        html += f"<li><strong>{field_name}:</strong> {value}</li>"
    html += "</ul>"
    return format_html(html)
