from urllib.parse import urlencode, urlparse, urlunparse, quote_plus
import requests
from django.contrib.gis.geos import Point


def get_coordinates_data(coordinates: Point, username: str, zoom=14):
    data = requests.get("https://nominatim.openstreetmap.org/reverse", {
        'lon': coordinates.x,
        'lat': coordinates.y,
        'format': 'json',
        # https://nominatim.org/release-docs/develop/api/Reverse/#result-limitation
        'zoom': zoom,
        'email': username
    })
    return data.json()


def static_map_marker_image_url(coordinates: Point, access_token: str, zoom=12, bearing=0, pitch=0, width=250, height=None, overlay=None, username='mapbox', style_id='streets-v11', marker_url="https://docs.mapbox.com/api/img/custom-marker.png") -> str:
    if coordinates is None:
        return
    lon = coordinates.x
    lat = coordinates.y
    if overlay is None:
        overlay = f'url-{quote_plus(marker_url)}({lon},{lat})'
    if height is None:
        height = width

    # Construct URL
    parsed = urlparse(
        f"https://api.mapbox.com/styles/v1/{username}/{style_id}/static/{overlay}/{lon},{lat},{zoom},{bearing},{pitch}/{width}x{height}")

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(dict({
                "access_token": access_token
            }), doseq=True),
            parsed.fragment,
        )
    )
