import ipaddress
import os
import re
import threading

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseGone,
    HttpResponseNotFound,
)
from django.shortcuts import redirect
from django.middleware.locale import LocaleMiddleware as _LocaleMiddleware
from django.utils import translation


class LocaleMiddleware(_LocaleMiddleware):
    def process_request(self, request: HttpRequest):
        path = request.path.lower()
        pattern = r"^/en-([a-z]+)"

        if re.search(pattern, path, re.IGNORECASE):
            new_path = re.sub(pattern, "/en", path)
            return redirect(new_path, permanent=True)

        super().process_request(request)

        language_code = request.GET.get("language_code")
        if language_code is not None:
            translation.activate(language_code)


class BlockAmazonMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "Amazonbot" in request.META.get(
            "HTTP_USER_AGENT", ""
        ) and not request.path.lower().endswith("robots.txt"):
            return HttpResponseGone()
        return self.get_response(request)


def _parse_networks(value):
    networks = []
    for cidr in value.split(","):
        cidr = cidr.strip()
        if cidr:
            networks.append(ipaddress.ip_network(cidr, strict=False))
    return networks


# Proxy networks used by the Nov 2026 scraper flood that took the site down.
DEFAULT_BLOCKED_IP_RANGES = "145.223.0.0/16,84.75.0.0/16,82.38.0.0/16"


class BlockIPRangesMiddleware:
    """
    Reject requests from blocked IP ranges before any other work is done.

    Override the list with the BLOCKED_IP_RANGES env var (comma-separated CIDRs,
    empty string to disable). Every address in X-Forwarded-For is checked, so a
    client can only spoof its way *into* the block, never out of it.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.networks = _parse_networks(
            os.getenv("BLOCKED_IP_RANGES", DEFAULT_BLOCKED_IP_RANGES)
        )

    def client_ips(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        candidates = [ip.strip() for ip in forwarded.split(",")]
        candidates.append(request.META.get("REMOTE_ADDR", ""))
        for candidate in candidates:
            try:
                yield ipaddress.ip_address(candidate)
            except ValueError:
                continue

    def is_blocked(self, request):
        return any(
            ip in network for ip in self.client_ips(request) for network in self.networks
        )

    def __call__(self, request):
        if self.networks and self.is_blocked(request):
            return HttpResponseForbidden()
        return self.get_response(request)


VALID_QUERY_VALUES = {
    "sort": {"most_recent", "oldest", "a-z", "z-a"},
    "mobile": {"true"},
}

METADATA_PATH = re.compile(r"^(/[a-z]{2}(-[a-z]+)?)?/_metadata/")
JUNK_PATH_SUFFIXES = ("''", '""')


class RejectJunkRequestsMiddleware:
    """
    Cheaply 404 requests that only crawlers make, so they never reach a full
    (uncached) page render and can't tie up the gunicorn threads.

    - paths ending in '' or "" (scraped from broken HTML attributes)
    - invalid values for enumerated query params (sort, mobile)
    - /_metadata/ frames requested outside Turbo (real ones always send the
      Turbo-Frame header), plus a per-process cap on concurrent renders
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.metadata_slots = threading.BoundedSemaphore(
            int(os.getenv("METADATA_MAX_CONCURRENT", 2))
        )

    def is_junk(self, request):
        if request.path.endswith(JUNK_PATH_SUFFIXES):
            return True
        for key, allowed in VALID_QUERY_VALUES.items():
            if any(value not in allowed for value in request.GET.getlist(key)):
                return True
        return False

    def __call__(self, request):
        if self.is_junk(request):
            return HttpResponseNotFound()

        if not METADATA_PATH.match(request.path):
            return self.get_response(request)

        if "HTTP_TURBO_FRAME" not in request.META:
            return HttpResponseNotFound()

        if not self.metadata_slots.acquire(blocking=False):
            response = HttpResponse(status=503)
            response["Retry-After"] = "5"
            return response
        try:
            return self.get_response(request)
        finally:
            self.metadata_slots.release()
