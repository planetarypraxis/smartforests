"""
Rate limiting and automatic network bans.

Requests that miss the page cache are counted per client IP, per small network
(IPv4 /24, IPv6 /64) and per large network (IPv4 /16, IPv6 /48), in fixed
60-second windows, separately in each gunicorn worker. Going over a limit
returns 429. A key that goes over its limit RATE_LIMIT_STRIKES times within
RATE_LIMIT_STRIKE_WINDOW seconds is banned: a BlockedNetwork row is written,
and BlockNetworksMiddleware rejects it with 403 until the ban expires. Ban
length doubles with each repeat (1h, 2h, 4h ... capped at 7 days).

RATE_LIMIT_MODE controls behaviour:
  - "observe" (default): log what would be limited/banned, change nothing
  - "enforce": return 429s and write bans
  - "off": do nothing
"""

import ipaddress
import logging
import os
import threading
import time
from collections import deque
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)

WINDOW_SECONDS = 60
BAN_LIST_REFRESH_SECONDS = 30
BASE_BAN = timedelta(hours=1)
MAX_BAN = timedelta(days=7)


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def get_mode():
    mode = os.getenv("RATE_LIMIT_MODE", "observe").strip().lower()
    return mode if mode in ("observe", "enforce", "off") else "observe"


def get_client_ip(request):
    """
    The address of the client as seen by our own proxy (Render).

    Clients can send any X-Forwarded-For they like; proxies append to it. With
    REMOTE_ADDR as the final hop, the chain is [client-supplied..., client,
    proxy...]. TRUSTED_PROXY_HOPS (default 1) is the number of proxy hops at
    the right of the chain, so the entry just left of them is the real client,
    whether or not the proxy overwrote the header.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    chain = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
    chain.append(request.META.get("REMOTE_ADDR", ""))
    hops = max(_env_int("TRUSTED_PROXY_HOPS", 1), 0)
    index = max(len(chain) - 1 - hops, 0)
    try:
        return ipaddress.ip_address(chain[index])
    except ValueError:
        return None


def network_keys(ip):
    """(label, network) pairs to count a request against, smallest first."""
    if ip.version == 4:
        prefixes = (("ip", 32), ("small", 24), ("large", 16))
    else:
        prefixes = (("ip", 128), ("small", 64), ("large", 48))
    return [
        (label, ipaddress.ip_network(f"{ip}/{prefix}", strict=False))
        for label, prefix in prefixes
    ]


def ban_duration(ban_count):
    return min(BASE_BAN * (2 ** max(ban_count - 1, 0)), MAX_BAN)


class BanList:
    """Active BlockedNetwork rows, cached in memory and refreshed periodically."""

    def __init__(self):
        self.lock = threading.Lock()
        self.networks = []  # [(network, automatic)]
        self.loaded_at = 0.0

    def invalidate(self):
        self.loaded_at = 0.0

    def refresh(self):
        from django.db.models import Q
        from smartforests.models import BlockedNetwork

        now = timezone.now()
        rows = BlockedNetwork.objects.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ).values_list("network", "automatic")
        networks = []
        for network, automatic in rows:
            try:
                networks.append((ipaddress.ip_network(network, strict=False), automatic))
            except ValueError:
                logger.warning("blocked_network_invalid network=%s", network)
        self.networks = networks

    def get(self):
        if time.monotonic() - self.loaded_at > BAN_LIST_REFRESH_SECONDS:
            with self.lock:
                if time.monotonic() - self.loaded_at > BAN_LIST_REFRESH_SECONDS:
                    try:
                        self.refresh()
                    except Exception:
                        # Never take the site down because the ban list can't
                        # be read (e.g. migration not applied yet): keep the
                        # last known list and retry on the next refresh.
                        logger.exception("blocked_network_refresh_failed")
                    self.loaded_at = time.monotonic()
        return self.networks

    def match(self, ip):
        for network, automatic in self.get():
            if ip.version == network.version and ip in network:
                return network, automatic
        return None


ban_list = BanList()


class RateLimiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.window = None
        self.counts = {}
        self.strikes = {}  # network -> deque of strike times
        self.limits = {
            "ip": _env_int("RATE_LIMIT_IP", 30),
            "small": _env_int("RATE_LIMIT_SMALL_NETWORK", 60),
            "large": _env_int("RATE_LIMIT_LARGE_NETWORK", 60),
        }
        self.strikes_to_ban = _env_int("RATE_LIMIT_STRIKES", 3)
        self.strike_window = _env_int("RATE_LIMIT_STRIKE_WINDOW", 600)

    def _roll_window(self, now):
        window = int(now // WINDOW_SECONDS)
        if window != self.window:
            self.window = window
            self.counts = {}
            cutoff = now - self.strike_window
            for network in list(self.strikes):
                times = self.strikes[network]
                while times and times[0] < cutoff:
                    times.popleft()
                if not times:
                    del self.strikes[network]

    def hit(self, ip, now=None):
        """
        Count one request from `ip`. Returns (label, network, should_ban) for
        the first limit exceeded, or None if the request is within limits.
        """
        now = time.time() if now is None else now
        exceeded = None
        with self.lock:
            self._roll_window(now)
            for label, network in network_keys(ip):
                count = self.counts.get(network, 0) + 1
                self.counts[network] = count
                if exceeded is None and count > self.limits[label]:
                    exceeded = (label, network, count)
            if exceeded is None:
                return None
            label, network, count = exceeded
            # One strike per network per window: the first request over the limit.
            if count == self.limits[label] + 1:
                times = self.strikes.setdefault(network, deque())
                times.append(now)
                while times and times[0] < now - self.strike_window:
                    times.popleft()
                should_ban = len(times) >= self.strikes_to_ban
                if should_ban:
                    del self.strikes[network]
            else:
                should_ban = False
        return label, network, should_ban


def record_ban(network, reason):
    """Create or extend an automatic ban. Returns the ban's expiry."""
    from smartforests.models import BlockedNetwork

    now = timezone.now()
    ban, created = BlockedNetwork.objects.get_or_create(
        network=str(network),
        defaults={"automatic": True, "reason": reason, "ban_count": 1},
    )
    if not created:
        if not ban.automatic and (ban.expires_at is None or ban.expires_at > now):
            return ban.expires_at  # an active manual ban takes precedence
        ban.ban_count += 1
        ban.automatic = True
        ban.reason = reason
    ban.expires_at = now + ban_duration(ban.ban_count)
    ban.save()
    ban_list.invalidate()
    return ban.expires_at
