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


import os
from unittest import mock

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from smartforests.middleware import (
    BlockIPRangesMiddleware,
    RejectJunkRequestsMiddleware,
)


def ok_response(request):
    return HttpResponse("ok")


class BlockIPRangesMiddlewareTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = BlockIPRangesMiddleware(ok_response)

    def status(self, **meta):
        return self.middleware(self.factory.get("/", **meta)).status_code

    def test_blocks_forwarded_ip_in_range(self):
        self.assertEqual(self.status(HTTP_X_FORWARDED_FOR="145.223.144.86"), 403)
        self.assertEqual(self.status(HTTP_X_FORWARDED_FOR="84.75.148.68, 10.0.0.1"), 403)
        self.assertEqual(self.status(HTTP_X_FORWARDED_FOR="1.2.3.4, 82.38.180.89"), 403)

    def test_blocks_remote_addr_in_range(self):
        self.assertEqual(self.status(REMOTE_ADDR="145.223.1.1"), 403)

    def test_allows_other_ips(self):
        self.assertEqual(self.status(HTTP_X_FORWARDED_FOR="81.2.69.160"), 200)
        self.assertEqual(self.status(HTTP_X_FORWARDED_FOR="garbage"), 200)

    def test_env_override(self):
        with mock.patch.dict(os.environ, {"BLOCKED_IP_RANGES": ""}):
            middleware = BlockIPRangesMiddleware(ok_response)
        request = self.factory.get("/", HTTP_X_FORWARDED_FOR="145.223.144.86")
        self.assertEqual(middleware(request).status_code, 200)


class RejectJunkRequestsMiddlewareTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RejectJunkRequestsMiddleware(ok_response)

    def status(self, path, **meta):
        return self.middleware(self.factory.get(path, **meta)).status_code

    def test_junk_path_suffixes(self):
        self.assertEqual(self.status("/en/logbooks/civtech/''"), 404)
        self.assertEqual(self.status('/en/_tags/landscape/""'), 404)
        self.assertEqual(self.status("/en/logbooks/civtech/"), 200)

    def test_query_values(self):
        self.assertEqual(self.status("/en/logbooks/x/?sort=a-z"), 200)
        self.assertEqual(self.status("/en/logbooks/x/?sort=bogus"), 404)
        self.assertEqual(self.status("/en/logbooks/x/?filter=carbon"), 200)

    def test_metadata_requires_turbo_frame(self):
        self.assertEqual(self.status("/hi/_metadata/3891/?mobile=true"), 404)
        self.assertEqual(self.status("/_metadata/3891/"), 404)
        frame = {"HTTP_TURBO_FRAME": "metadata-turboframe"}
        self.assertEqual(self.status("/hi/_metadata/3891/?mobile=true", **frame), 200)
        self.assertEqual(self.status("/_metadata/3891/", **frame), 200)
        self.assertEqual(self.status("/_metadata/3891/?mobile=yes", **frame), 404)

    def test_metadata_concurrency_cap(self):
        frame = {"HTTP_TURBO_FRAME": "metadata-turboframe"}
        self.middleware.metadata_slots.acquire()
        self.middleware.metadata_slots.acquire()
        try:
            self.assertEqual(self.status("/en/_metadata/1/", **frame), 503)
            self.assertEqual(self.status("/en/logbooks/", **frame), 200)
        finally:
            self.middleware.metadata_slots.release()
            self.middleware.metadata_slots.release()
        self.assertEqual(self.status("/en/_metadata/1/", **frame), 200)
