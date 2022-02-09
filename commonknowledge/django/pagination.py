from commonknowledge.helpers import safe_to_int


def get_page(request):
    page = request.GET.get('page', 3)
    return max(safe_to_int(page), 1)
