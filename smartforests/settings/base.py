"""
Django settings for smartforests project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf.locale import LANG_INFO
import os
import re
import dj_database_url

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "smartforests",
    "home",
    "logbooks",
    "search",
    "commonknowledge.bootstrap",
    "commonknowledge.django",
    "commonknowledge.wagtail",
    "generic_chooser",
    "wagtail_modeladmin",
    "wagtailmenus",
    "wagtail_content_import",
    "wagtail_footnotes",
    "import_export",
    "mapwidgets",
    "wagtailautocomplete",
    "wagtailseo",
    "wagtail_localize",
    "wagtail_localize.locales",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail.contrib.settings",
    "wagtail.api.v2",
    "wagtail.contrib.routable_page",
    "modelcluster",
    "taggit",
    "wagtailmedia",
    "webpack_loader",
    "anymail",
    "rest_framework",
    "rest_framework_gis",
    "drf_spectacular",
    "background_task",
    "django.contrib.gis",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "wagtailcache",
    "wagtaillinkchecker",
    "commonknowledge.wagtail_overrides",
]

MIDDLEWARE = [
    "wagtailcache.cache.UpdateCacheMiddleware",
    "smartforests.middleware.BlockAmazonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "turbo_response.middleware.TurboMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "smartforests.middleware.LocaleMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "logbooks.middleware.pages.ImportantPagesMiddleware",
    "wagtailcache.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "smartforests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "django_settings_export.settings_export",
                "wagtailmenus.context_processors.wagtailmenus",
            ],
        },
    },
]

WSGI_APPLICATION = "smartforests.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if os.getenv("SKIP_DB") != "1":
    DATABASES = {
        "default": dj_database_url.parse(
            re.sub(r"^postgres(ql)?", "postgis", os.getenv("DATABASE_URL")),
            conn_max_age=600,
            ssl_require=False,
        )
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "smartforests.User"


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Wagtail internationalisation
# https://docs.wagtail.io/en/stable/advanced_topics/i18n.html

USE_I18N = True
WAGTAIL_I18N_ENABLED = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "dist"),
]

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "",  # must end with slash
        "STATS_FILE": os.path.join(BASE_DIR, "dist/webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# General settings

# Wagtail settings

WAGTAIL_SITE_NAME = "smartforests"
WAGTAILADMIN_BASE_URL = f"{os.getenv('BASE_URL')}"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
WAGTAILIMAGES_IMAGE_MODEL = "smartforests.CmsImage"
WAGTAILDOCS_DOCUMENT_MODEL = "smartforests.CmsDocument"

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
        "SEARCH_CONFIG": "english",
        "AUTO_UPDATE": True,
    }
}

THUMBNAIL_ENGINE = "sorl.thumbnail.engines.wand_engine.Engine"

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (("footer", "Footer"),)

# Rest settings

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Smart Forests Atlas",
    "DESCRIPTION": "Investigating how digital technologies are remaking forests, and how forests are becoming technologies for addressing environmental change",
    "VERSION": "1.0.0",
    "PREPROCESSING_HOOKS": ["smartforests.api.preprocessing_hooks"],
    # OTHER SETTINGS
}

# Logging

DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")
CK_LOG_LEVEL = os.getenv("CK_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "commonknowledge": {
            "handlers": ["console"],
            "level": CK_LOG_LEVEL,
        },
        "logbooks": {
            "handlers": ["console"],
            "level": CK_LOG_LEVEL,
        },
        "smartforests": {
            "handlers": ["console"],
            "level": CK_LOG_LEVEL,
        },
        "": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
        },
    },
}

INTERNAL_IPS = [
    "127.0.0.1",
]

# This allows you to change the maximum number of results a user can request at a time. This applies to all endpoints. Set to None for no limit.
WAGTAILAPI_LIMIT_MAX = None


MAPBOX_API_PUBLIC_TOKEN = os.getenv("MAPBOX_API_PUBLIC_TOKEN")

POSTHOG_PUBLIC_TOKEN = os.getenv("POSTHOG_PUBLIC_TOKEN", None)

POSTHOG_URL = "https://app.posthog.com"

# Settings accessible via {{ settings.XXX }} in templates
SETTINGS_EXPORT = [
    "DEBUG",
    "POSTHOG_URL",
    "POSTHOG_PUBLIC_TOKEN",
]

SETTINGS_EXPORT_VARIABLE_NAME = "environment"

MAP_WIDGETS = {
    "MapboxPointFieldWidget": (("access_token", MAPBOX_API_PUBLIC_TOKEN),),
    "MAPBOX_API_KEY": MAPBOX_API_PUBLIC_TOKEN,
}

# Allow any language that Django supports
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    (locale[0], locale[1]["name_local"] + " (" + locale[1]["name"] + ")")
    for locale in LANG_INFO.items()
    if locale[1].get("name_local", None) and locale[1].get("name", None)
]

POSTHOG_DJANGO = {
    "distinct_id": lambda request: request.user and request.user.distinct_id
}

SERVICE_API_TOKEN = os.getenv("SERVICE_API_TOKEN")

WAGTAILLOCALIZE_JOBS = {
    "BACKEND": "smartforests.wagtail_localize_tasks.DjangoDBQueueJobBackend",
}

USE_BACKGROUND_WORKER = os.getenv("USE_BACKGROUND_WORKER", "False") in (
    "True",
    "true",
    True,
    1,
    "t",
)

WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "smartforests.machine_translators.MultiTranslator",
    "OPTIONS": {
        "DEFAULT_TRANSLATOR": "DEEPL",
        "TRANSLATORS_BY_LOCALE": {
            "hi": "GOOGLE",
        },
        "TRANSLATORS": {
            "DEEPL": {
                "CLASS": "wagtail_localize.machine_translators.deepl.DeepLTranslator",
                "OPTIONS": {
                    "AUTH_KEY": os.getenv("DEEPL_AUTH_KEY"),
                },
            },
            "GOOGLE": {
                "CLASS": "smartforests.machine_translators.GoogleCloudTranslator",
                "OPTIONS": {
                    "CREDENTIALS_PATH": os.path.join(
                        BASE_DIR, "google_credentials.json"
                    ),
                    "PROJECT_ID": os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
                },
            },
        },
    },
}

LOCALE_PATHS = (
    "smartforests/locale",
    "logbooks/locale",
    "home/locale",
    "commonknowledge/locale",
)


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_database_cache",
        "TIMEOUT": os.getenv("CACHE_MIDDLEWARE_SECONDS") or 600,
        "KEY_PREFIX": "wagtailcache",
    }
}


USE_PROFILING = os.getenv("USE_PROFILING", False)


def custom_show_pyinstrument(request):
    return request.user.is_superuser


if USE_PROFILING:
    print("Profiler active. Add ?profile to URLs to view profiling.")
    MIDDLEWARE += [
        "pyinstrument.middleware.ProfilerMiddleware",
    ]
    PYINSTRUMENT_SHOW_CALLBACK = "%s.custom_show_pyinstrument" % __name__
