"""Production settings.

This module extends base settings; star import is intentional for Django settings.
Uses typed environment settings for secure production configuration.
"""

# ruff: noqa: F401, F403

from .base import *
from .env import get_settings

# Get typed settings (cached from base.py)
env = get_settings()

# Force DEBUG off in production
DEBUG = False

# Security settings from typed environment
SESSION_COOKIE_SECURE = env.SESSION_COOKIE_SECURE or True
CSRF_COOKIE_SECURE = env.CSRF_COOKIE_SECURE or True
SECURE_SSL_REDIRECT = env.SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS = env.SECURE_HSTS_SECONDS

# Additional production security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Production email configuration (SMTP)
if env.APP_ENV == "prod":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Logging configuration for production
if env.LOG_FORMAT == "json":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": (
                    "%(asctime)s %(name)s %(levelname)s %(request_id)s %(message)s"
                ),
            },
        },
        "filters": {
            "request_id": {
                "()": "apps.core.logging.RequestIDFilter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": ["request_id"],
            },
        },
        "root": {
            "level": env.LOG_LEVEL,
            "handlers": ["console"],
        },
    }

# Cache configuration for production
if env.CACHE_URL:
    try:
        import django_redis

        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": env.CACHE_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
                "TIMEOUT": env.CACHE_TIMEOUT,
                "KEY_PREFIX": "mysite:prod",  # Multi-tenant cache isolation
            }
        }
        SESSION_ENGINE = "django.contrib.sessions.backends.cache"
        SESSION_CACHE_ALIAS = "default"
    except ImportError:
        # Fallback to database cache if django-redis not installed
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.db.DatabaseCache",
                "LOCATION": "cache_table",
                "TIMEOUT": env.CACHE_TIMEOUT,
                "KEY_PREFIX": "mysite:prod",  # Multi-tenant cache isolation
            }
        }

# Static files optimization for production
if env.ENABLE_WHITENOISE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Disable admin in production if configured
if not env.ENABLE_ADMIN:
    try:
        INSTALLED_APPS.remove("django.contrib.admin")  # noqa: F405
    except ValueError:
        pass  # Already removed
