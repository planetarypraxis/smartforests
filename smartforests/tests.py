from django.test import TestCase, override_settings

from smartforests.util import static_file_absolute_url


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
@override_settings(STATIC_URL='/static/')
@override_settings(BASE_URL='https://atlas.smartforests.net')
class URLTestCase(TestCase):
    def test_static_file_absolute_url(self):
        self.assertEqual(
            static_file_absolute_url("img/mapicons/radio.png"),
            "https://atlas.smartforests.net/static/img/mapicons/radio.png",
        )
