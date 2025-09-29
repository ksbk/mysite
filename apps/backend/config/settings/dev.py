"""Development settings.

This module extends base settings; star import is intentional for Django settings.
"""

# ruff: noqa: F401, F403

import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *

# Load environment variables from .env file
ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

DEBUG = True

# Email in development: print emails to the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@mysite.local")

# Vite dev server URL for template tag helpers
VITE_DEV_SERVER_URL = os.environ.get("VITE_DEV_SERVER_URL", "http://localhost:5173")
