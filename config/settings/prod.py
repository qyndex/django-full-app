"""Production settings — Postgres via DATABASE_URL, SSL controlled by env var."""
import os

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# Supabase / Postgres via DATABASE_URL
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", ""),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# SSL — default False so Docker works without TLS terminator
# Set SECURE_SSL_REDIRECT=true in env when behind a load balancer that terminates SSL
_ssl_redirect = os.environ.get("SECURE_SSL_REDIRECT", "false").lower() == "true"
SECURE_SSL_REDIRECT = _ssl_redirect
SECURE_HSTS_SECONDS = 31536000 if _ssl_redirect else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = _ssl_redirect
SECURE_HSTS_PRELOAD = _ssl_redirect
SESSION_COOKIE_SECURE = _ssl_redirect
CSRF_COOKIE_SECURE = _ssl_redirect

# Whitenoise for static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Email — configure SMTP via env in production
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
