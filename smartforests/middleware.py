import logging
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

from smartforests import rate_limit

logger = logging.getLogger(__name__)


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


class BlockNetworksMiddleware:
    """
    Reject requests from networks in the BlockedNetwork table with 403, before
    any other work is done. Rows are added by RateLimitMiddleware or by hand
    in the Django admin (/django-admin/smartforests/blockednetwork/).

    Automatic bans don't apply to the admin, so editors on a shared network
    that got banned can still log in (and lift the ban).
    """

    ADMIN_PREFIXES = ("/admin/", "/django-admin/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = rate_limit.get_client_ip(request)
        match = ip and rate_limit.ban_list.match(ip)
        if match:
            _network, automatic = match
            if not (automatic and request.path.startswith(self.ADMIN_PREFIXES)):
                return HttpResponseForbidden()
        return self.get_response(request)


class RateLimitMiddleware:
    """
    Count requests that reach the view, i.e. miss the page cache, and return
    429 for clients over the limit. Networks that keep going over the limit
    are banned via BlockedNetwork. Logged-in users are never limited. Must sit
    after wagtailcache's FetchFromCacheMiddleware. See smartforests/rate_limit.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.limiter = rate_limit.RateLimiter()

    def __call__(self, request):
        mode = rate_limit.get_mode()
        if mode == "off":
            return self.get_response(request)

        ip = rate_limit.get_client_ip(request)
        if ip is None or request.user.is_authenticated:
            return self.get_response(request)

        result = self.limiter.hit(ip)
        if result is None:
            return self.get_response(request)

        label, network, should_ban = result
        enforce = mode == "enforce"
        prefix = "" if enforce else "would_"
        if should_ban:
            expires_at = None
            if enforce:
                try:
                    expires_at = rate_limit.record_ban(
                        network, f"Rate limit ({label}) exceeded repeatedly"
                    )
                except Exception:
                    # e.g. both workers banning the same network at once.
                    # Still return the 429 below; the ban is retried on the
                    # next strike.
                    logger.exception("auto_block_failed network=%s", network)
            logger.warning(
                "%sauto_blocked network=%s limit=%s expires_at=%s",
                prefix,
                network,
                label,
                expires_at,
            )
        logger.warning(
            "%srate_limited ip=%s network=%s limit=%s path=%s xff=%r remote_addr=%s",
            prefix,
            ip,
            network,
            label,
            request.path,
            request.META.get("HTTP_X_FORWARDED_FOR", ""),
            request.META.get("REMOTE_ADDR", ""),
        )
        if not enforce:
            return self.get_response(request)

        response = HttpResponse("Too many requests", status=429)
        response["Retry-After"] = str(rate_limit.WINDOW_SECONDS)
        response["Cache-Control"] = "private, no-store"
        return response


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
