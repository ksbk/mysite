"""Production settings.

This module extends base settings; star import is intentional for Django settings.
"""

# ruff: noqa: F401, F403

from .base import *

DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
