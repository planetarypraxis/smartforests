from django.utils.module_loading import import_string
from wagtail_localize.machine_translators.base import BaseMachineTranslator
from wagtail_localize.machine_translators.google import GoogleCloudTranslator as BaseGoogleCloudTranslator
from wagtail_localize.strings import StringValue

class MultiTranslator(BaseMachineTranslator):
    """
    Switch between providers based on target locale.
    """
    def __init__(self, options):
        super().__init__(options)
        self.translators = {
            key: import_string(config["CLASS"])(config["OPTIONS"])
            for key, config in options["TRANSLATORS"].items()
        }
        self.display_name = self.translators[options["DEFAULT_TRANSLATOR"]].display_name

    def get_translator(self, target_locale):
        translator_class = self.options["TRANSLATORS_BY_LOCALE"].get(
            target_locale.language_code, self.options["DEFAULT_TRANSLATOR"]
        )
        return self.translators[translator_class]

    def translate(self, source_locale, target_locale, strings):
        translator = self.get_translator(target_locale)
        return translator.translate(source_locale, target_locale, strings)

    def can_translate(self, source_locale, target_locale):
        translator = self.get_translator(target_locale)
        self.display_name = translator.display_name
        return translator.can_translate(source_locale, target_locale)


class GoogleCloudTranslator(BaseGoogleCloudTranslator):
    """
    Split up translation job into batches, to avoid going over the 30,000
    codepoint (utf8 character) limit.
    """
    def translate(self, source_locale, target_locale, strings):
        project_id = self.options["PROJECT_ID"]
        location = self.options.get("LOCATION", "global")

        batches = [[]]
        current_batch_size = 0
        for string in strings:
            strlen = len(string.data)
            if current_batch_size + strlen > 30000:
                batches.append([])
                current_batch_size = 0
            batches[-1].append(string)
            current_batch_size += strlen

        translations = []
        for batch in batches:
            response = self.client.translate_text(
                request={
                    "parent": f"projects/{project_id}/locations/{location}",
                    "contents": [string.data for string in batch],
                    "mime_type": "text/html",
                    "source_language_code": source_locale.language_code,
                    "target_language_code": target_locale.language_code,
                }
            )
            translations = translations + list(response.translations)

        return {
            string: StringValue(translation.translated_text)
            for string, translation in zip(strings, translations)
        }
