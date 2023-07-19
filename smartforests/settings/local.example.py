# Local settings go here
# DO NOT import from base - it has already been imported in dev.py or production.py

# local does not import from base, as it is imported from

WAGTAILTRANSFER_SOURCES = {
    'production': {
        'BASE_URL': 'https://atlas.smartforests.net/admin/wagtail-transfer',
        'SECRET_KEY': 'XXXXXX',
    },
}

MAPBOX_API_PUBLIC_TOKEN = 'XXXXXX'
MAPBOX_STYLE = 'XXXXXX'

POSTHOG_PUBLIC_TOKEN = 'XXXXXX'

MAP_WIDGETS = {
    "MapboxPointFieldWidget": (
        ("access_token", MAPBOX_API_PUBLIC_TOKEN),
    ),
    "MAPBOX_API_KEY": MAPBOX_API_PUBLIC_TOKEN
}

USE_BACKGROUND_WORKER = True
