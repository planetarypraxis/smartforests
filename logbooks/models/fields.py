from wagtail.admin.panels import FieldPanel
from wagtail.admin.widgets.tags import AdminTagWidget
from modelcluster.contrib.taggit import ClusterTaggableManager
from smartforests.models import Tag


class TagFieldWidget(AdminTagWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.attrs["locale"]:
            context["widget"]["attrs"]["data-w-tag-url-value"] = (
                context["widget"]["attrs"]["data-w-tag-url-value"]
                + "?locale="
                + self.attrs["locale"]
            )
        return context


class TagFieldPanel(FieldPanel):
    """
    Filter the tags so that tags in the locale of the page being edited are displayed.
    """

    def __init__(self, field_name, *args, **kwargs):
        kwargs["widget"] = TagFieldWidget
        super().__init__(field_name, *args, **kwargs)

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            locale = (
                self.form.instance.locale.language_code
                if self.form.instance and self.form.instance.locale
                else None
            )
            tag_field = self.form.fields["tags"]
            tag_field.widget.attrs["locale"] = locale


class LocalizedTaggableManager(ClusterTaggableManager):
    """
    Create new tags in the locale of the page being edited.
    """

    def save_form_data(self, instance, value):
        locale = instance.locale if instance else None
        if locale:
            for name in value:
                existing_tag = Tag.objects.filter(name=name).first()
                if not existing_tag:
                    Tag.objects.create(name=name, locale=locale)
        super().save_form_data(instance, value)
        # The tag field updates tags by name, which means we get duplicate tags associated
        # with the instance (e.g. datafication (en) and datafication (fr)).
        # The below line deduplicates those tags.
        instance.tags.set(tag for tag in instance.tags.all() if tag.locale == locale)
