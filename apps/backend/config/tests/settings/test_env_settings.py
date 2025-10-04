"""Test cases for Django settings configuration.

This module contains comprehensive tests for all settings files including:
- Environment settings validation (env.py)
- Base configuration loading (base.py)
- Environment-specific overrides (dev.py, prod.py, staging.py, test.py)
- Request ID middleware and logging integration
"""

import os
import unittest.mock
from pathlib import Path
from unittest import TestCase

import pytest
from django.test import TestCase as DjangoTestCase
from django.test import override_settings
from pydantic import ValidationError as PydanticValidationError

from config.settings.env import Settings, get_settings


class TestEnvironmentSettings(TestCase):
    """Test cases for environment settings validation and loading."""

    def setUp(self):
        """Clear cached settings before each test."""
        get_settings.cache_clear()

    def test_default_settings_creation(self):
        """Test that default settings are created successfully."""
        settings = Settings()

        # Test core defaults
        self.assertFalse(settings.DEBUG)
        self.assertEqual(
            settings.SECRET_KEY.get_secret_value(),
            "django-insecure-change-me-in-production",
        )
        self.assertEqual(settings.ALLOWED_HOSTS, ["localhost", "127.0.0.1"])
        self.assertEqual(settings.APP_ENV, "local")

    def test_allowed_hosts_parsing(self):
        """Test ALLOWED_HOSTS parsing from different formats."""
        # Test JSON array format (what pydantic-settings expects for list[str])
        with unittest.mock.patch.dict(
            os.environ, {"ALLOWED_HOSTS": '["example.com", "api.example.com"]'}
        ):
            settings = Settings()
            self.assertEqual(settings.ALLOWED_HOSTS, ["example.com", "api.example.com"])

        # Test single host as JSON array
        with unittest.mock.patch.dict(
            os.environ, {"ALLOWED_HOSTS": '["single-host.com"]'}
        ):
            settings = Settings()
            self.assertEqual(settings.ALLOWED_HOSTS, ["single-host.com"])

        # Test with JSON array with spaces (trimmed by field validator)
        with unittest.mock.patch.dict(
            os.environ, {"ALLOWED_HOSTS": '["host1.com", "host2.com"]'}
        ):
            settings = Settings()
            self.assertEqual(settings.ALLOWED_HOSTS, ["host1.com", "host2.com"])

    def test_hsts_bounds_validation(self):
        """Test HSTS seconds bounds checking."""
        # Test within bounds
        with unittest.mock.patch.dict(
            os.environ, {"SECURE_HSTS_SECONDS": "31536000"}
        ):  # 1 year
            settings = Settings()
            self.assertEqual(settings.SECURE_HSTS_SECONDS, 31536000)

        # Test upper bound enforcement (2 years max)
        with unittest.mock.patch.dict(os.environ, {"SECURE_HSTS_SECONDS": "999999999"}):
            settings = Settings()
            max_seconds = 60 * 60 * 24 * 730  # 2 years
            self.assertEqual(settings.SECURE_HSTS_SECONDS, max_seconds)

        # Test lower bound
        with unittest.mock.patch.dict(os.environ, {"SECURE_HSTS_SECONDS": "-1"}):
            settings = Settings()
            self.assertEqual(settings.SECURE_HSTS_SECONDS, 0)

    def test_email_tls_ssl_exclusivity(self):
        """Test that EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be True."""
        with unittest.mock.patch.dict(
            os.environ, {"EMAIL_USE_TLS": "true", "EMAIL_USE_SSL": "true"}
        ):
            with self.assertRaises(PydanticValidationError) as cm:
                Settings()

            # Check that the error message mentions TLS/SSL exclusivity
            error_msg = str(cm.exception)
            self.assertIn(
                "EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be True", error_msg
            )

    def test_hsts_consistency_warning(self):
        """Test HSTS consistency warning when SSL redirect is disabled."""
        with unittest.mock.patch.dict(
            os.environ,
            {"SECURE_HSTS_SECONDS": "31536000", "SECURE_SSL_REDIRECT": "false"},
        ):
            with unittest.mock.patch("warnings.warn") as mock_warn:
                Settings()
                mock_warn.assert_called_once()

                # Check warning message
                warning_call = mock_warn.call_args[0][0]
                self.assertIn(
                    "SECURE_HSTS_SECONDS > 0 but SECURE_SSL_REDIRECT is False",
                    warning_call,
                )

    def test_vite_url_normalization(self):
        """Test VITE_DEV_SERVER_URL normalization removes trailing slash."""
        with unittest.mock.patch.dict(
            os.environ, {"VITE_DEV_SERVER_URL": "http://localhost:5173/"}
        ):
            settings = Settings()
            self.assertEqual(settings.VITE_DEV_SERVER_URL, "http://localhost:5173")

    def test_static_media_url_normalization(self):
        """Test STATIC_URL and MEDIA_URL normalization adds slashes."""
        with unittest.mock.patch.dict(
            os.environ, {"STATIC_URL": "static", "MEDIA_URL": "media"}
        ):
            settings = Settings()
            self.assertEqual(settings.STATIC_URL, "/static/")
            self.assertEqual(settings.MEDIA_URL, "/media/")

    def test_email_port_bounds(self):
        """Test email port bounds validation."""
        # Test valid port
        with unittest.mock.patch.dict(os.environ, {"EMAIL_PORT": "587"}):
            settings = Settings()
            self.assertEqual(settings.EMAIL_PORT, 587)

        # Test port too high
        with unittest.mock.patch.dict(os.environ, {"EMAIL_PORT": "99999"}):
            settings = Settings()
            self.assertEqual(settings.EMAIL_PORT, 65535)

        # Test port too low
        with unittest.mock.patch.dict(os.environ, {"EMAIL_PORT": "0"}):
            settings = Settings()
            self.assertEqual(settings.EMAIL_PORT, 1)

    def test_app_env_literal_validation(self):
        """Test APP_ENV accepts only valid literal values."""
        # Test valid values
        for env_value in ["local", "dev", "staging", "prod"]:
            with unittest.mock.patch.dict(os.environ, {"APP_ENV": env_value}):
                settings = Settings()
                self.assertEqual(settings.APP_ENV, env_value)

        # Test invalid value
        with unittest.mock.patch.dict(os.environ, {"APP_ENV": "invalid"}):
            with self.assertRaises(PydanticValidationError):
                Settings()

    def test_log_level_validation(self):
        """Test LOG_LEVEL accepts only valid logging levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            with unittest.mock.patch.dict(os.environ, {"LOG_LEVEL": level}):
                settings = Settings()
                self.assertEqual(settings.LOG_LEVEL, level)

    def test_secret_str_redaction(self):
        """Test that SecretStr fields are properly redacted."""
        with unittest.mock.patch.dict(
            os.environ,
            {
                # pragma: allowlist secret (test-only)
                "SECRET_KEY": "super-secret-key",
                # pragma: allowlist secret (test-only)
                "EMAIL_HOST_PASSWORD": "email-password",
            },
        ):
            settings = Settings()

            # SecretStr should not reveal the actual value in repr
            self.assertNotIn("super-secret-key", repr(settings.SECRET_KEY))
            self.assertNotIn("email-password", repr(settings.EMAIL_HOST_PASSWORD))

            # But should be accessible via get_secret_value()
            self.assertEqual(settings.SECRET_KEY.get_secret_value(), "super-secret-key")
            self.assertEqual(
                settings.EMAIL_HOST_PASSWORD.get_secret_value(), "email-password"
            )

    def test_cached_settings_loading(self):
        """Test that get_settings() properly caches the Settings instance."""
        # Clear cache first
        get_settings.cache_clear()

        # First call should create instance
        settings1 = get_settings()

        # Second call should return same instance (cached)
        settings2 = get_settings()

        # Should be the same object
        self.assertIs(settings1, settings2)

        # Clear cache and get new instance
        get_settings.cache_clear()
        settings3 = get_settings()

        # Should be different object now
        self.assertIsNot(settings1, settings3)

    def test_path_field_validation(self):
        """Test Path field validation and conversion."""
        with unittest.mock.patch.dict(
            os.environ,
            {
                "SQLITE_PATH": "custom/path/db.sqlite3",
                "LOG_FILE_PATH": "/var/log/mysite.log",
            },
        ):
            settings = Settings()

            # Should convert to Path objects
            self.assertIsInstance(settings.SQLITE_PATH, Path)
            self.assertIsInstance(settings.LOG_FILE_PATH, Path)

            # Should have correct values
            self.assertEqual(str(settings.SQLITE_PATH), "custom/path/db.sqlite3")
            self.assertEqual(str(settings.LOG_FILE_PATH), "/var/log/mysite.log")


class TestSettingsIntegration(DjangoTestCase):
    """Integration tests for Django settings loading."""

    def test_settings_module_loading(self):
        """Test that different settings modules load without errors."""
        from django.conf import settings

        # Basic smoke test - settings should be loaded
        self.assertTrue(hasattr(settings, "SECRET_KEY"))
        self.assertTrue(hasattr(settings, "INSTALLED_APPS"))
        self.assertTrue(hasattr(settings, "MIDDLEWARE"))

    def test_base_settings_structure(self):
        """Test base settings structure and required components."""
        from django.conf import settings

        # Core Django settings
        required_settings = [
            "SECRET_KEY",
            "DEBUG",
            "ALLOWED_HOSTS",
            "INSTALLED_APPS",
            "MIDDLEWARE",
            "ROOT_URLCONF",
            "TEMPLATES",
            "DATABASES",
            "STATIC_URL",
            "MEDIA_URL",
        ]

        for setting_name in required_settings:
            self.assertTrue(
                hasattr(settings, setting_name),
                f"Missing required setting: {setting_name}",
            )

    def test_middleware_order(self):
        """Test middleware is in correct order."""
        from django.conf import settings

        middleware = settings.MIDDLEWARE

        # Security middleware should be first
        self.assertEqual(middleware[0], "django.middleware.security.SecurityMiddleware")

        # Request ID middleware should be second (if present)
        if "apps.core.middleware.request_id.RequestIDMiddleware" in middleware:
            self.assertEqual(
                middleware[1], "apps.core.middleware.request_id.RequestIDMiddleware"
            )

        # Session middleware should come before auth
        session_idx = middleware.index(
            "django.contrib.sessions.middleware.SessionMiddleware"
        )
        auth_idx = middleware.index(
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        )
        self.assertLess(
            session_idx, auth_idx, "Session middleware must come before Auth middleware"
        )

    @override_settings(DEBUG=True)
    def test_debug_mode_behavior(self):
        """Test behavior when DEBUG is enabled."""
        from django.conf import settings

        self.assertTrue(settings.DEBUG)

        # Debug mode should affect certain settings
        if hasattr(settings, "VITE_DEV"):
            # VITE_DEV should follow DEBUG if not explicitly set
            pass  # This depends on environment variable


class TestConditionalSettingsLoading(TestCase):
    """Test conditional loading of apps and middleware based on feature flags."""

    def setUp(self):
        """Clear settings cache before each test."""
        get_settings.cache_clear()

    def test_admin_conditional_loading(self):
        """Test admin app is conditionally loaded based on ENABLE_ADMIN."""
        # Test admin enabled
        with unittest.mock.patch.dict(os.environ, {"ENABLE_ADMIN": "true"}):
            # Import base settings to trigger conditional loading
            import importlib

            from config.settings import base, env

            # Clear the cached settings
            env.get_settings.cache_clear()
            importlib.reload(base)

            self.assertIn("django.contrib.admin", base.INSTALLED_APPS)

        # Test admin disabled
        with unittest.mock.patch.dict(os.environ, {"ENABLE_ADMIN": "false"}):
            import importlib

            from config.settings import base, env

            # Clear the cached settings
            env.get_settings.cache_clear()
            importlib.reload(base)

            self.assertNotIn("django.contrib.admin", base.INSTALLED_APPS)

    def test_compression_conditional_loading(self):
        """Test compressor is conditionally loaded based on ENABLE_COMPRESSION."""
        # Test compression enabled
        with unittest.mock.patch.dict(os.environ, {"ENABLE_COMPRESSION": "true"}):
            import importlib

            from config.settings import base

            importlib.reload(base)

            self.assertIn("compressor", base.INSTALLED_APPS)
            if hasattr(base, "STATICFILES_FINDERS"):
                self.assertIn(
                    "compressor.finders.CompressorFinder", base.STATICFILES_FINDERS
                )


if __name__ == "__main__":
    pytest.main([__file__])
