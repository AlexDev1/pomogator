import ast
import os
import warnings
from pathlib import Path
from pathlib import Path
import dj_database_url
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def get_list(text):
    return [item.strip() for item in text.split(",")]


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value


DEBUG = get_bool_from_env("DEBUG", False)
SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    warnings.warn("SECRET_KEY not configured, using a random temporary key.")
    SECRET_KEY = get_random_secret_key()

# SECRET_KEY = 'django-insecure-^vv-*lpng&z5qh$#=klt+su8!tx_4q6g#5lw8m0_5yg%wxu+)l'
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

INTERNAL_IPS = get_list(os.environ.get("INTERNAL_IPS", "127.0.0.1"))
ALLOWED_HOSTS = get_list(os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0"))

# Application definition

INSTALLED_APPS = [
    'filebrowser',
    'liststyle',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    # Core
    'trumbowyg',
    'photologue',
    'sortedm2m',
    'daterangefilter',
    'django_extensions',
    'tinymce',
    'compressor',
    'sorl.thumbnail',
    'mptt',
    'adminsortable2',
    'robots',
    'watson',
    'captcha',
    'django_toggle_switch_widget',
    # Apps
    'core',
    'banner',
    'news',
    'partners',
    'comments',
    'countries.apps.CountriesConfig',
]

SITE_ID = 1


def get_host():
    from django.contrib.sites.models import Site

    return Site.objects.get_current().domain


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'pomogator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pomogator.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default="postgres://pomogator:pomogator@localhost:5432/pomogator", conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
# USE_TZ = True

# Settings Apps
MIN_SEARCH_CHARS = 2
MAX_PHOTO_WIDTH = 1100
MAX_PHOTO_HEIGHT = 1100
USER_PHOTO_WIDTH = 468
USER_PHOTO_HEIGHT = 468
NOIMAGE_URL = "images/noimage.png"
# Aliases
NO_IMAGE_URL = NOIMAGE_URL
NO_IMAGE = NOIMAGE_URL
NOIMAGE = NOIMAGE_URL

FILEBROWSER_SHOW_IN_DASHBOARD = False
FILE_UPLOAD_PERMISSIONS = 0o775
# Static and Media
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media/")
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATIC_ROOT_FILES = os.path.join(PROJECT_ROOT, 'static_src')
STATIC_URL = os.environ.get("STATIC_URL", "/static/")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if not os.path.exists(os.path.join(STATIC_ROOT, "images")):  # ToDo проверить!
    os.mkdir(os.path.join(STATIC_ROOT, "images"))

STATICFILES_DIRS = [
    ("images", os.path.join(PROJECT_ROOT, "static", "images")),
    ('static_src')
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]


SITE_URL = 'https://pomogator.travel'
FEEDBACK_EMAIL = 'smi@tourprom.ru'

# django-compressor
COMPRESS_CSS_FILTERS = [
    #    'compressor.filters.cssmin.CSSCompressorFilter',
    'compressor.filters.css_default.CssAbsoluteFilter',
]

# Django-robots
ROBOTS_USE_SITEMAP = False
ROBOTS_USE_SCHEME_IN_HOST = True
ROBOTS_CACHE_TIMEOUT = 60 * 60 * 24

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/3'
CELERY_CACHE_BACKEND = 'redis'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/5'
CELERY_TRACK_STARTED = True

from celery.schedules import crontab

CELERY_TIMEZONE = TIME_ZONE

try:
    from .local_settings import *
except ImportError:
    print("Error import local settings")

# Settings ReCaptcha
RECAPTCHA_PUBLIC_KEY = "6Ld2Az0aAAAAAIIoCbwZT4y6twZ_FukAz4b4TDVI"
RECAPTCHA_PRIVATE_KEY = "6Ld2Az0aAAAAAMtq60zd-YnppKBl3trIQ-CvFdzH"
NOCAPTCHA = True
# RECAPTCHA_DOMAIN = 'zoj.news'

# Email SMTP Settings
SMTP_SERVER = 'localhost'
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'smi@newmailserver.tourprom.ru'
SUBSCRIPTION_FROM_EMAIL = 'news@newmailserver.tourprom.ru'
FEEDBACK_EMAIL = 'smi@tourprom.ru'

EMAIL_TITLE_TPL = 'ЗОЖ.news <%s>'

DEFAULT_FROM_EMAIL_TITLED = EMAIL_TITLE_TPL % DEFAULT_FROM_EMAIL
SUBSCRIPTION_FROM_EMAIL_TITLED = EMAIL_TITLE_TPL % SUBSCRIPTION_FROM_EMAIL

TINYMCE_DEFAULT_CONFIG = {
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': 'link image preview codesample contextmenu table code lists powerpaste fullscreen wordcount ',
    'toolbar1': 'formatselect | wordcount | bold italic underline | alignleft aligncenter alignright alignjustify '
                '| bullist numlist | outdent indent | table | link image | pastetext | codesample | preview code '
                '| fullscreen',
    'contextmenu': 'formats | link image | pastetext',
    'menubar': False,
    # 'paste_as_text': True,
    'powerpaste_word_import': 'merge',
    'inline': False,
    'statusbar': True,
    'width': 'auto',
    'height': 460,
}
