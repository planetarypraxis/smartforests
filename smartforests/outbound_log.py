"""
Log every outbound HTTP request the process makes.

Patches urllib3's connection pool, which sits underneath `requests`, `boto3`
(DigitalOcean Spaces), `sentry_sdk`, `posthog` and anymail, so anything that
leaves the service over HTTP is written to stdout as a single `outbound_http`
line. Render's log search can then be aggregated by host, path and bytes.

Disable with LOG_OUTBOUND_HTTP=false.
"""
import os
import time
import traceback

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _body_size(body):
    if body is None:
        return 0
    if isinstance(body, (bytes, bytearray, str)):
        return len(body)
    try:
        return len(body)
    except TypeError:
        return -1  # streamed body, size unknown


def _caller():
    """First project (non-library) frame on the stack, so we know who triggered it."""
    for frame in reversed(traceback.extract_stack()):
        f = frame.filename
        if (
            f.startswith(PROJECT_DIR)
            and ".venv" not in f
            and "site-packages" not in f
            and "outbound_log" not in f
        ):
            return f"{os.path.relpath(f, PROJECT_DIR)}:{frame.lineno}"
    return "library"


def install():
    if os.environ.get("LOG_OUTBOUND_HTTP", "true").lower() in ("0", "false", "no"):
        return
    try:
        from urllib3.connectionpool import HTTPConnectionPool
    except ImportError:
        return
    if getattr(HTTPConnectionPool, "_outbound_log_installed", False):
        return

    original = HTTPConnectionPool.urlopen

    def urlopen(self, method, url, body=None, headers=None, *args, **kwargs):
        started = time.monotonic()
        sent = _body_size(body)
        status = "ERR"
        received = -1
        try:
            response = original(self, method, url, body, headers, *args, **kwargs)
            status = response.status
            received = int(response.headers.get("Content-Length") or -1)
            return response
        finally:
            print(
                "outbound_http"
                f" host={self.host} method={method} path={url.split('?')[0][:200]}"
                f" status={status} sent={sent} received={received}"
                f" ms={int((time.monotonic() - started) * 1000)}"
                f" caller={_caller()}",
                flush=True,
            )

    HTTPConnectionPool.urlopen = urlopen
    HTTPConnectionPool._outbound_log_installed = True
