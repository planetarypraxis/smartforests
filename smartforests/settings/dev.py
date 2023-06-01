from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lt!8@q40mll#wdum^+n!y67i-_3k%1p-9k$5#s!ok2-o8wr7eh'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
BASE_URL = 'http://localhost:8080'

DATABASES['default']['CONN_MAX_AGE'] = 0

INSTALLED_APPS += [
    "wagtail.contrib.styleguide",
]

USE_DEBUG_TOOLBAR = False

if USE_DEBUG_TOOLBAR:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "wagtail_localize.machine_translators.dummy.DummyTranslator",
}

try:
    from .local import *
except ImportError:
    pass
