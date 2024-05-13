import re
from django.http import HttpRequest, HttpResponseForbidden
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
            return HttpResponseForbidden()
        return self.get_response(request)
