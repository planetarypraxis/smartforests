from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.widgets.tags import AdminTagWidget
from rich import inspect


class TagFieldWidget(AdminTagWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.attrs['locale']:
            context['widget']['autocomplete_url'] = context['widget']['autocomplete_url'] + \
                "?locale=" + self.attrs["locale"]
        return context


class TagFieldPanel(FieldPanel):
    """
    Filter the tags so that tags in the locale of the page being edited are displayed.
    """

    def __init__(self, field_name, *args, **kwargs):
        kwargs["widget"] = TagFieldWidget
        super().__init__(field_name, *args, **kwargs)

    def on_form_bound(self):
        locale = self.form.instance.locale.language_code if self.form.instance and self.form.instance.locale else None
        self.form.fields['tags'].widget.attrs['locale'] = locale
        super().on_form_bound()
