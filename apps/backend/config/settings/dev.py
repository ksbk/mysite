"""Development settings.

This module extends base settings; star import is intentional for Django settings.
Overrides are minimal since base.py now uses typed environment settings.
"""

# ruff: noqa: F401, F403

from .base import *
from .env import get_settings

# Get typed settings (cached from base.py)
env = get_settings()

# Force DEBUG on in development
DEBUG = True

# Development-specific feature flags
if env.ENABLE_DEBUG_TOOLBAR and DEBUG:
    INSTALLED_APPS.append("debug_toolbar")  # noqa: F405  (imported via base settings)
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

    # Debug toolbar configuration
    INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Development email configuration (override base.py)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Development compression settings (override base.py)
# Disable offline compression in development to avoid manifest issues
if env.ENABLE_COMPRESSION:
    COMPRESS_OFFLINE = False  # Generate on-the-fly in development
    COMPRESS_ENABLED = True  # Still compress, but not offline
