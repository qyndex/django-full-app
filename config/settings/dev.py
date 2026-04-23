"""Development settings — SQLite, debug toolbar, no SSL."""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# Readable emails in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable static file manifest hashing in dev for faster reloads
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
