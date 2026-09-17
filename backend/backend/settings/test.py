import os
from .base import *

DEBUG = False

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

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

# Deliberately no SECURE_SSL_REDIRECT / HSTS / secure-cookie flags here —
# those assume a TLS-terminating proxy in front of the app. Django's test
# client (and a bare runserver/gunicorn) only speaks plain HTTP, so
# inheriting production.py's settings would 301-redirect every request
# the test suite makes.
