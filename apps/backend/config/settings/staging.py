"""Staging settings.

Production-like configuration for staging/testing environments.
Uses typed environment settings with staging-specific overrides.
"""

# ruff: noqa: F401, F403

from .base import *
from .env import get_settings

# Get typed settings (cached from base.py)
env = get_settings()

# Staging should behave like production but with some debugging enabled
DEBUG = False

# Security settings (less strict than production)
SESSION_COOKIE_SECURE = env.SESSION_COOKIE_SECURE or True
CSRF_COOKIE_SECURE = env.CSRF_COOKIE_SECURE or True
SECURE_SSL_REDIRECT = env.SECURE_SSL_REDIRECT

# HSTS with shorter duration for staging
SECURE_HSTS_SECONDS = min(env.SECURE_HSTS_SECONDS, 86400)  # Max 1 day

# Staging-specific features
if env.ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1", "10.0.0.0/8"]  # Include private networks

# Email configuration (usually console or test SMTP for staging)
EMAIL_BACKEND = env.EMAIL_BACKEND

# Allow staging-specific logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "level": env.LOG_LEVEL,
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Cache configuration (simpler than production)
if env.CACHE_URL:
    try:
        import django_redis

        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": env.CACHE_URL,
                "TIMEOUT": env.CACHE_TIMEOUT,
                "KEY_PREFIX": "mysite:staging",  # Multi-tenant cache isolation
            }
        }
    except ImportError:
        # Fallback to local memory cache
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "TIMEOUT": env.CACHE_TIMEOUT,
                "KEY_PREFIX": "mysite:staging",  # Multi-tenant cache isolation
            }
        }

# Static files optimization for staging (production parity)
if env.ENABLE_WHITENOISE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
