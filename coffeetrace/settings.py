"""Django settings for CoffeeTrace.

The project connects only to an existing Microsoft SQL Server database. It does
not create databases, logins, users, or switch automatically to another engine.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from coffeetrace.config import Environment, SqlServerConfiguration

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = Environment.get_bool("DJANGO_DEBUG", True)
SECRET_KEY = (
    Environment.get(
        "DJANGO_SECRET_KEY",
        "unsafe-development-key-change-before-production",
    )
    if DEBUG
    else Environment.require("DJANGO_SECRET_KEY")
)
ALLOWED_HOSTS = Environment.get_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)
CSRF_TRUSTED_ORIGINS = Environment.get_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "apps.common",
    "apps.accounts",
    "apps.producers",
    "apps.receptions",
    "apps.lots",
    "apps.traceability",
    "apps.audit",
    "apps.reports",
    "apps.frontend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "coffeetrace.urls"
WSGI_APPLICATION = "coffeetrace.wsgi.application"
ASGI_APPLICATION = "coffeetrace.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.frontend.context_processors.user_profile",
            ]
        },
    }
]

SQL_SERVER = SqlServerConfiguration.from_environment()
DATABASES = {"default": SQL_SERVER.as_django_database()}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-cr"
TIME_ZONE = Environment.get("DJANGO_TIME_ZONE", "America/Costa_Rica")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "apps.common.pagination.StandardResultsSetPagination"
    ),
    "PAGE_SIZE": Environment.get_int("DEFAULT_PAGE_SIZE", 20, minimum=1),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": Environment.get("API_ANON_RATE", "100/hour"),
        "user": Environment.get("API_USER_RATE", "2000/hour"),
    },
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.common.exceptions.api_exception_handler",
}

EMAIL_BACKEND = Environment.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = Environment.get(
    "DEFAULT_FROM_EMAIL",
    "noreply@coffeetrace.local",
)
WEIGHT_TOLERANCE_KG = Environment.get("WEIGHT_TOLERANCE_KG", "0.50")

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = Environment.get_bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    not DEBUG,
)
SECURE_HSTS_SECONDS = 31_536_000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

LOG_LEVEL = Environment.get("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{asctime} {levelname} {name}: {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

# Prevent Python from buffering output when the project is run in containers.
os.environ.setdefault("PYTHONUNBUFFERED", "1")
