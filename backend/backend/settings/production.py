import os
from .base import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

# No default — a missing ALLOWED_HOSTS should fail loudly at startup,
# not silently resolve to [''] (which the .get()+split() pattern does).
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "fpw"),
        "USER": os.environ.get("DB_USER", "fpw"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# split(",") on an unset/empty env var produces [''], which fails
# Django's system check (an empty string isn't a valid origin) — filter
# it out so an unset var correctly means "no origins", not one blank one.
CORS_ALLOWED_ORIGINS = [
    origin for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if origin
]

# Needed for the subscribe form's CSRF check to accept POSTs once this
# sits behind a real HTTPS domain.
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]

# Tells Django to trust nginx's X-Forwarded-Proto header when nginx
# terminates TLS and proxies plain HTTP to gunicorn. Without this,
# SECURE_SSL_REDIRECT causes a redirect loop behind a reverse proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
