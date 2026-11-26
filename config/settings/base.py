"""Base settings shared by all environments.

All environment-specific values are read from environment variables
(optionally loaded from a local `.env` file) via django-environ.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
)

# Load .env if present (never committed). Real environment variables win.
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    # Project apps
    "core",
    "home",
    "navigation",
    # Wagtail
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
    "modelcluster",
    "taggit",
    "django_filters",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database: PostgreSQL via psycopg 3, configured with DATABASE_URL.
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# Static & media
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Complex page models can exceed Django's default of 1000 fields.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000

# Email (used by the contact form). Default: print to console.
# e.g. EMAIL_URL=smtp+tls://user:password@smtp.example.com:587
_email = env.email("EMAIL_URL", default="consolemail://")
EMAIL_BACKEND = _email["EMAIL_BACKEND"]
EMAIL_HOST = _email.get("EMAIL_HOST", "localhost")
EMAIL_PORT = _email.get("EMAIL_PORT", 25)
EMAIL_HOST_USER = _email.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = _email.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _email.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = _email.get("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Wagtail
WAGTAIL_SITE_NAME = env("WAGTAIL_SITE_NAME", default="Wagtail Home")
WAGTAILADMIN_BASE_URL = env("WAGTAILADMIN_BASE_URL", default="http://localhost:8000")
WAGTAILSEARCH_BACKENDS = {
    "default": {"BACKEND": "wagtail.search.backends.database"},
}
WAGTAILDOCS_EXTENSIONS = ["csv", "docx", "key", "odt", "pdf", "pptx", "rtf", "txt", "xlsx", "zip"]
WAGTAILDOCS_MAX_UPLOAD_SIZE = 10 * 1024 * 1024

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO")},
    "loggers": {
        # Wagtail's background tasks log every run at INFO; keep only warnings.
        "django_tasks": {"level": "WARNING"},
    },
}
