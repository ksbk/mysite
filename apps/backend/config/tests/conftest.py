"""
Test configuration for Django project-level components.

This conftest.py provides fixtures and settings overrides for testing
the Django project configuration (settings, URLs, ASGI/WSGI, env parsing).
"""

import os
import tempfile
from unittest.mock import patch

import pytest
from django.test import override_settings


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing env parsing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("""# Test environment variables
DEBUG=True
SECRET_KEY=test-secret-key-for-testing
DATABASE_URL=sqlite:///test.db
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
""")
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "DEBUG": "False",
        "SECRET_KEY": "mock-secret-key",
        "DATABASE_URL": "sqlite:///mock.db",
        "ALLOWED_HOSTS": "testserver",
        "CORS_ALLOWED_ORIGINS": "http://testserver",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def minimal_settings():
    """Minimal Django settings for testing configuration loading."""
    return {
        "SECRET_KEY": "test-key",
        "DEBUG": True,
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        "INSTALLED_APPS": [
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        "USE_TZ": True,
    }


@pytest.fixture
def settings_override():
    """Helper to create settings overrides easily in tests."""

    def _override(**kwargs):
        return override_settings(**kwargs)

    return _override


@pytest.fixture
def django_settings_module():
    """Fixture to test different Django settings modules."""
    original = os.environ.get("DJANGO_SETTINGS_MODULE")

    def _set_module(module_name):
        os.environ["DJANGO_SETTINGS_MODULE"] = module_name
        return module_name

    yield _set_module

    if original:
        os.environ["DJANGO_SETTINGS_MODULE"] = original
    elif "DJANGO_SETTINGS_MODULE" in os.environ:
        del os.environ["DJANGO_SETTINGS_MODULE"]
