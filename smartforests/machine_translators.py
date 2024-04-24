from django.utils.module_loading import import_string
from wagtail_localize.machine_translators.base import BaseMachineTranslator


class MultiTranslator(BaseMachineTranslator):
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
