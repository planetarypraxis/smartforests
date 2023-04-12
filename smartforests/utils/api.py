from rest_framework.fields import Field
from wagtail.core.rich_text import expand_db_html
from wagtail.api import APIField


class APIRichTextField(APIField):
    def __init__(self, name):
        serializer = APIRichTextSerializer(name)
        super().__init__(name=name, serializer=serializer)


class APIRichTextSerializer(Field):
    def __init__(self, name):
        self.name = name
        super().__init__()

    def get_attribute(self, instance):
        return instance

    def to_representation(self, obj):
        value = getattr(obj, self.name)
        if value and value is not None and value is not '':
            # Expands Wagtail XML to HTML
            return expand_db_html(value)
        return None
