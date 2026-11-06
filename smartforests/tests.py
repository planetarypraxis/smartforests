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


import ipaddress
import os
from datetime import timedelta
from unittest import mock

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from smartforests import rate_limit
from smartforests.middleware import (
    BlockNetworksMiddleware,
    RateLimitMiddleware,
    RejectJunkRequestsMiddleware,
)


def ok_response(request):
    return HttpResponse("ok")


class ClientIPTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def ip(self, xff=None, remote="10.0.0.5"):
        meta = {"REMOTE_ADDR": remote}
        if xff is not None:
            meta["HTTP_X_FORWARDED_FOR"] = xff
        return str(rate_limit.get_client_ip(self.factory.get("/", **meta)))

    def test_proxy_overwrites_header(self):
        self.assertEqual(self.ip("81.2.69.160"), "81.2.69.160")

    def test_ignores_client_supplied_entries(self):
        self.assertEqual(self.ip("1.1.1.1, 2.2.2.2, 81.2.69.160"), "81.2.69.160")

    def test_no_proxy_header(self):
        self.assertEqual(self.ip(None, remote="81.2.69.160"), "81.2.69.160")

    def test_trusted_hops(self):
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_HOPS": "2"}):
            self.assertEqual(self.ip("spoof, 81.2.69.160, 172.16.0.1"), "81.2.69.160")

    def test_garbage(self):
        self.assertEqual(self.ip("not-an-ip"), "None")


class RateLimiterTestCase(SimpleTestCase):
    def setUp(self):
        env = {
            "RATE_LIMIT_IP": "3",
            "RATE_LIMIT_SMALL_NETWORK": "5",
            "RATE_LIMIT_LARGE_NETWORK": "8",
            "RATE_LIMIT_STRIKES": "2",
            "RATE_LIMIT_STRIKE_WINDOW": "600",
        }
        with mock.patch.dict(os.environ, env):
            self.limiter = rate_limit.RateLimiter()

    def hits(self, ip, n, now=1000.0):
        return [self.limiter.hit(ipaddress.ip_address(ip), now=now) for _ in range(n)]

    def test_per_ip_limit(self):
        results = self.hits("81.2.69.160", 4)
        self.assertEqual(results[:3], [None, None, None])
        label, network, should_ban = results[3]
        self.assertEqual((label, str(network), should_ban), ("ip", "81.2.69.160/32", False))

    def test_rotating_ips_hit_network_limits(self):
        results = [
            self.limiter.hit(ipaddress.ip_address(f"145.223.{i}.{i}"), now=1000.0)
            for i in range(1, 10)
        ]
        self.assertEqual(results[:8], [None] * 8)
        label, network, _ = results[8]
        self.assertEqual((label, str(network)), ("large", "145.223.0.0/16"))

    def test_window_resets(self):
        self.hits("81.2.69.160", 4, now=1000.0)
        self.assertIsNone(self.hits("81.2.69.160", 1, now=1061.0)[0])

    def test_repeated_strikes_ban(self):
        first = self.hits("81.2.69.160", 5, now=1000.0)
        self.assertFalse(any(r[2] for r in first if r))
        second = self.hits("81.2.69.160", 4, now=1070.0)
        self.assertTrue(second[3][2])
        # The ban is reported once, not on every later request.
        self.assertFalse(self.hits("81.2.69.160", 1, now=1071.0)[0][2])

    def test_old_strikes_expire(self):
        self.hits("81.2.69.160", 4, now=1000.0)
        later = self.hits("81.2.69.160", 4, now=1000.0 + 700)
        self.assertFalse(later[3][2])

    def test_ipv6(self):
        results = self.hits("2001:db8::1", 4)
        self.assertEqual(str(results[3][1]), "2001:db8::1/128")

    def test_ban_duration(self):
        self.assertEqual(rate_limit.ban_duration(1), timedelta(hours=1))
        self.assertEqual(rate_limit.ban_duration(3), timedelta(hours=4))
        self.assertEqual(rate_limit.ban_duration(20), timedelta(days=7))


class FakeBanList:
    def __init__(self, networks):
        self.networks = [(ipaddress.ip_network(n), auto) for n, auto in networks]

    def match(self, ip):
        for network, automatic in self.networks:
            if ip in network:
                return network, automatic
        return None


class BlockNetworksMiddlewareTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = BlockNetworksMiddleware(ok_response)
        fake = FakeBanList([("145.223.0.0/16", False), ("84.75.0.0/16", True)])
        patcher = mock.patch.object(rate_limit, "ban_list", fake)
        patcher.start()
        self.addCleanup(patcher.stop)

    def status(self, ip, path="/"):
        request = self.factory.get(path, HTTP_X_FORWARDED_FOR=ip, REMOTE_ADDR="10.0.0.5")
        return self.middleware(request).status_code

    def test_blocks_banned_networks(self):
        self.assertEqual(self.status("145.223.144.86"), 403)
        self.assertEqual(self.status("84.75.148.68"), 403)

    def test_allows_other_ips(self):
        self.assertEqual(self.status("81.2.69.160"), 200)

    def test_spoofed_header_cannot_get_others_blocked(self):
        self.assertEqual(self.status("145.223.144.86, 81.2.69.160"), 200)

    def test_automatic_bans_skip_admin(self):
        self.assertEqual(self.status("84.75.148.68", "/admin/login/"), 200)
        self.assertEqual(self.status("145.223.144.86", "/admin/login/"), 403)


class RateLimitMiddlewareTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        env = {"RATE_LIMIT_IP": "2", "RATE_LIMIT_STRIKES": "1"}
        with mock.patch.dict(os.environ, env):
            self.middleware = RateLimitMiddleware(ok_response)

    def statuses(self, n, authenticated=False):
        out = []
        for _ in range(n):
            request = self.factory.get("/", REMOTE_ADDR="81.2.69.160")
            request.user = mock.Mock(is_authenticated=authenticated)
            out.append(self.middleware(request).status_code)
        return out

    def test_observe_mode_only_logs(self):
        with mock.patch.dict(os.environ, {"RATE_LIMIT_MODE": "observe"}), \
                mock.patch.object(rate_limit, "record_ban") as record_ban, \
                self.assertLogs("smartforests.middleware", "WARNING") as logs:
            self.assertEqual(self.statuses(3), [200, 200, 200])
        record_ban.assert_not_called()
        self.assertTrue(any("would_auto_blocked" in line for line in logs.output))

    def test_enforce_mode(self):
        with mock.patch.dict(os.environ, {"RATE_LIMIT_MODE": "enforce"}), \
                mock.patch.object(rate_limit, "record_ban") as record_ban, \
                self.assertLogs("smartforests.middleware", "WARNING"):
            self.assertEqual(self.statuses(3), [200, 200, 429])
        record_ban.assert_called_once()
        self.assertEqual(str(record_ban.call_args[0][0]), "81.2.69.160/32")

    def test_authenticated_users_exempt(self):
        with mock.patch.dict(os.environ, {"RATE_LIMIT_MODE": "enforce"}):
            self.assertEqual(self.statuses(5, authenticated=True), [200] * 5)

    def test_off(self):
        with mock.patch.dict(os.environ, {"RATE_LIMIT_MODE": "off"}):
            self.assertEqual(self.statuses(5), [200] * 5)


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
