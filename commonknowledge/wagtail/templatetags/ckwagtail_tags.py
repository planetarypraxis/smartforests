import re
from urllib import parse
from wagtail.blocks.base import Block

from wagtail.models import Site, Locale
from wagtailmenus.templatetags.menu_tags import main_menu, flat_menu
from django import template
from django.utils.safestring import SafeText, mark_safe
from commonknowledge.helpers import safe_to_int
from django import template
from smartforests.models import Tag

register = template.Library()


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


@register.filter()
def highlight_tags(content: SafeText):
    locale = Locale.get_active()

    content = str(content)

    words = set()
    splitter = r"[ !#()-;:'\",./<>]" if locale.language_code == "hi" else r"\b"
    for word in re.split(splitter, content):
        words.add(word)
        words.add(word.lower())

    # Remove links and re-insert after highlighting tags
    # Matching tags inside <a> tags breaks them
    links = re.findall(r"<a[^<]*</a>", content, re.IGNORECASE)
    for i, link in enumerate(links):
        content = content.replace(link, f"[#~{i}~#]")

    tags = Tag.objects.filter(locale=locale, name__in=words)
    for tag in tags:
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
        content = re.sub(
            rf"({splitter})({tag.name})({splitter})",
            replace,
            content,
            flags=re.IGNORECASE,
        )

    for i, link in enumerate(links):
        content = content.replace(f"[#~{i}~#]", link)

    return mark_safe(content)
