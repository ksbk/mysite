"""Test settings.

Optimized for fast test execution with typed environment configuration.
"""

# ruff: noqa: F401, F403

from .base import *  # noqa
from .base import BASE_DIR, DATABASES  # explicit for type checkers
from .env import get_settings

# Get typed settings (cached from base.py)
env = get_settings()

# Force DEBUG off in tests
DEBUG = False

# Speed up hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use in-memory email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Test database configuration
if env.DATABASE_URL:
    # Use test database variant of DATABASE_URL if provided
    import dj_database_url

    db_config = dj_database_url.parse(env.DATABASE_URL)
    db_config["NAME"] = f"test_{db_config["NAME"]}"
    DATABASES = {"default": db_config}
else:
    # Use separate SQLite file for tests (don't modify main db.sqlite3)
    DATABASES["default"]["NAME"] = BASE_DIR / "test_db.sqlite3"


# Disable migrations for faster test runs
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Use simpler password validators in tests
AUTH_PASSWORD_VALIDATORS = []

# Disable cache in tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Disable compression and static file processing in tests
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# Test-specific feature flags
CSP_NONCE_ENABLED = False
