"""
Django settings for smartforests project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import re
import dj_database_url

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'smartforests',
    'home',
    'logbooks',
    'search',

    'commonknowledge.bootstrap',
    'commonknowledge.django',
    'commonknowledge.wagtail',

    'wagtailmenus',
    'wagtail_content_import',
    "wagtail_footnotes",
    'import_export',
    'mapwidgets',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.postgres_search',
    'wagtail_transfer',
    'wagtail.contrib.settings',
    'wagtail.api.v2',
    "wagtail.contrib.routable_page",
    'wagtail.contrib.modeladmin',
    'modelcluster',
    'taggit',
    'wagtailmedia',

    'webpack_loader',
    "anymail",
    "rest_framework",
    "rest_framework_gis",
    "django_cron",
    # 'debug_toolbar',

    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'turbo_response.middleware.TurboMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'smartforests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
                'wagtailmenus.context_processors.wagtailmenus',
                'django_settings_export.settings_export',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartforests.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if os.getenv('SKIP_DB') != '1':
    DATABASES = {
        'default': dj_database_url.parse(
            re.sub(
                r"^postgres(ql)?",
                "postgis",
                os.getenv('DATABASE_URL')
            ),
            conn_max_age=600,
            ssl_require=False
        )
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'smartforests.User'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'dist'),
    os.path.join(BASE_DIR, 'smartforests', 'static')
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'dist/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Wagtail settings

WAGTAIL_SITE_NAME = "smartforests"

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
WAGTAILIMAGES_IMAGE_MODEL = 'smartforests.CmsImage'
WAGTAILDOCS_DOCUMENT_MODEL = 'smartforests.CmsDocument'

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.contrib.postgres_search.backend',
        'SEARCH_CONFIG': 'english',
        'AUTO_UPDATE': True,
    }
}

THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.wand_engine.Engine'

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (
    ('footer', 'Footer'),
)

# Rest settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ]
}


# Logging

DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
        },
    },
}

INTERNAL_IPS = [
    '127.0.0.1',
]

# This allows you to change the maximum number of results a user can request at a time. This applies to all endpoints. Set to None for no limit.
WAGTAILAPI_LIMIT_MAX = None


MAPBOX_API_PUBLIC_TOKEN = os.getenv('MAPBOX_API_PUBLIC_TOKEN')

POSTHOG_PUBLIC_TOKEN = None
POSTHOG_URL = 'https://app.posthog.com'

# Settings accessible via {{ settings.XXX }} in templates
SETTINGS_EXPORT = [
    'DEBUG',
    'POSTHOG_URL',
    'POSTHOG_PUBLIC_TOKEN',
]

SETTINGS_EXPORT_VARIABLE_NAME = 'environment'

MAP_WIDGETS = {
    "MapboxPointFieldWidget": (
        ("access_token", MAPBOX_API_PUBLIC_TOKEN),
    ),
    "MAPBOX_API_KEY": MAPBOX_API_PUBLIC_TOKEN
}

POSTHOG_DJANGO = {
    "distinct_id": lambda request: request.user and request.user.distinct_id
}
