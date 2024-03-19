from django.utils.functional import cached_property
from wagtail import hooks
from wagtail.models import Page
from wagtail.admin.widgets.button import ButtonWithDropdownFromHook
from wagtail_localize.models import Translation, TranslationSource
from smartforests.views import RadioEpisodeChooserViewSet
from django.utils.html import format_html
from django.templatetags.static import static


@hooks.register("construct_page_action_menu")
def customise_page_actions(menu_items, request, context):
    """
    Disallow non-admins from deleting pages via the Page Editor
    """
    if not request.user.is_superuser:
        try:
            for index, item in enumerate(menu_items):
                if item.name == "action-delete":
                    menu_items.pop(index)
                    break
        except:
            pass

    """
    Make 'publish' the default action in Page Editor
    """
    try:
        for index, item in enumerate(menu_items):
            if item.name == "action-publish" or item.name == "action-submit":
                menu_items.pop(index)
                menu_items.insert(0, item)
                break
    except:
        pass


@hooks.register("construct_page_listing_buttons")
def remove_page_listing_button_item(buttons, page, page_perms, context=None):
    """
    Disallow non-admins from deleting pages via the listing
    """
    is_superuser = "request" in context and context["request"].user.is_superuser
    if not is_superuser:
        more_actions_dropdown = buttons.pop()
        buttons.append(ButtonWithDropdownFromHookExcludingDelete(more_actions_dropdown))
    return buttons


class ButtonWithDropdownFromHookExcludingDelete(ButtonWithDropdownFromHook):
    template_name = "wagtailadmin/pages/listing/_button_with_dropdown.html"

    def __init__(self, base_class, **kwargs):
        self.hook_name = base_class.hook_name
        self.page = base_class.page
        self.page_perms = base_class.page_perms
        self.next_url = base_class.next_url

        super().__init__(
            base_class.label,
            hook_name=base_class.hook_name,
            page=base_class.page,
            page_perms=base_class.page_perms,
            next_url=base_class.next_url,
            **kwargs
        )

    @cached_property
    def dropdown_buttons(self):
        buttons = super().dropdown_buttons
        try:
            for index, item in enumerate(buttons):
                if item.label == "Delete":
                    buttons.pop(index)
                    break
        except:
            pass
        return buttons


@hooks.register("register_admin_viewset")
def register_person_chooser_viewset():
    return RadioEpisodeChooserViewSet(
        "radio_episode_chooser", url_prefix="radio-episode-chooser"
    )


@hooks.register("insert_global_admin_css")
def insert_global_admin_css():
    return format_html(
        '<link rel="stylesheet" type="text/css" href="{}">',
        static("admin.css"),
    )


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    return format_html(
        '<script type="module" src="{}"></script>', static("js/radio_wagtailmedia.js")
    )


@hooks.register("after_publish_page")
def after_publish_page_update_translations(request, page):
    """Update translations when original page is saved."""
    if hasattr(page, "translation_key"):
        # Update translation source (this stores synched fields, e.g. tags and coordinates)
        TranslationSource.update_or_create_from_instance(page)

        translated_pages = Page.objects.filter(
            translation_key=page.translation_key
        ).exclude(id=page.id)
        for translated_page in translated_pages:
            # Update each translation with the new synched field values
            translation = Translation.objects.filter(
                source__object_id=page.translation_key,
                target_locale_id=translated_page.locale_id,
                enabled=True,
            ).first()
            if translation:
                translation.save_target(request.user)
