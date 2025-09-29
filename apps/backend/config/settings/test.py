from .base import *  # noqa
from .base import BASE_DIR, DATABASES  # explicit for type checkers

# Speed up hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use in-memory email backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Test database (sqlite in-memory by default via manage.py test)
DATABASES["default"]["NAME"] = BASE_DIR / "test_db.sqlite3"

# Ensure DEBUG is off in tests
DEBUG = False

# Use a simpler password validator setup in tests if desired
AUTH_PASSWORD_VALIDATORS = []
