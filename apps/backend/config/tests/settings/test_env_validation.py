"""Test cases for environment settings validation (env.py)."""

import os
import unittest.mock
from pathlib import Path
from unittest import TestCase

import pytest
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
        expected_secret = "django-insecure-change-me-in-production"
        self.assertEqual(settings.SECRET_KEY.get_secret_value(), expected_secret)
        self.assertEqual(settings.ALLOWED_HOSTS, ["localhost", "127.0.0.1"])
        self.assertEqual(settings.APP_ENV, "local")

    def test_allowed_hosts_parsing(self):
        """Test ALLOWED_HOSTS parsing from different formats."""
        # Test JSON array string (what pydantic-settings expects for list[str])
        env_vars = {"ALLOWED_HOSTS": '["example.com", "api.example.com"]'}
        with unittest.mock.patch.dict(os.environ, env_vars):
            settings = Settings()
            expected = ["example.com", "api.example.com"]
            self.assertEqual(settings.ALLOWED_HOSTS, expected)

        # Test single host as JSON array
        with unittest.mock.patch.dict(
            os.environ, {"ALLOWED_HOSTS": '["single-host.com"]'}
        ):
            settings = Settings()
            self.assertEqual(settings.ALLOWED_HOSTS, ["single-host.com"])

        # Test with multiple hosts as JSON array
        env_vars = {"ALLOWED_HOSTS": '["host1.com", "host2.com"]'}
        with unittest.mock.patch.dict(os.environ, env_vars):
            settings = Settings()
            self.assertEqual(settings.ALLOWED_HOSTS, ["host1.com", "host2.com"])

    def test_hsts_bounds_validation(self):
        """Test HSTS seconds bounds checking."""
        # Test within bounds
        env_vars = {"SECURE_HSTS_SECONDS": "31536000"}  # 1 year
        with unittest.mock.patch.dict(os.environ, env_vars):
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
        env_vars = {"EMAIL_USE_TLS": "true", "EMAIL_USE_SSL": "true"}
        with unittest.mock.patch.dict(os.environ, env_vars):
            with self.assertRaises(PydanticValidationError) as cm:
                Settings()

            # Check that the error message mentions TLS/SSL exclusivity
            error_msg = str(cm.exception)
            expected_msg = "EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be True"
            self.assertIn(expected_msg, error_msg)

    def test_hsts_consistency_warning(self):
        """Test HSTS consistency warning when SSL redirect is disabled."""
        env_vars = {"SECURE_HSTS_SECONDS": "31536000", "SECURE_SSL_REDIRECT": "false"}
        with unittest.mock.patch.dict(os.environ, env_vars):
            with unittest.mock.patch("warnings.warn") as mock_warn:
                Settings()
                mock_warn.assert_called_once()

                # Check warning message
                warning_call = mock_warn.call_args[0][0]
                expected_warning = (
                    "SECURE_HSTS_SECONDS > 0 but SECURE_SSL_REDIRECT is False"
                )
                self.assertIn(expected_warning, warning_call)

    def test_url_normalization(self):
        """Test URL normalization for various fields."""
        env_vars = {
            "VITE_DEV_SERVER_URL": "http://localhost:5173/",
            "STATIC_URL": "static",
            "MEDIA_URL": "media",
        }
        with unittest.mock.patch.dict(os.environ, env_vars):
            settings = Settings()

            # VITE_DEV_SERVER_URL should have trailing slash removed
            self.assertEqual(settings.VITE_DEV_SERVER_URL, "http://localhost:5173")

            # STATIC_URL and MEDIA_URL should have slashes added
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
        valid_envs = ["local", "dev", "staging", "prod"]
        for env_value in valid_envs:
            with unittest.mock.patch.dict(os.environ, {"APP_ENV": env_value}):
                settings = Settings()
                self.assertEqual(settings.APP_ENV, env_value)

        # Test invalid value
        with unittest.mock.patch.dict(os.environ, {"APP_ENV": "invalid"}):
            with self.assertRaises(PydanticValidationError):
                Settings()

    def test_secret_str_redaction(self):
        """Test that SecretStr fields are properly redacted."""
        env_vars = {
            "SECRET_KEY": "super-secret-key",
            "EMAIL_HOST_PASSWORD": "email-password",
        }
        with unittest.mock.patch.dict(os.environ, env_vars):
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
        env_vars = {
            "SQLITE_PATH": "custom/path/db.sqlite3",
            "LOG_FILE_PATH": "/var/log/mysite.log",
        }
        with unittest.mock.patch.dict(os.environ, env_vars):
            settings = Settings()

            # Should convert to Path objects
            self.assertIsInstance(settings.SQLITE_PATH, Path)
            self.assertIsInstance(settings.LOG_FILE_PATH, Path)

            # Should have correct values
            self.assertEqual(str(settings.SQLITE_PATH), "custom/path/db.sqlite3")
            self.assertEqual(str(settings.LOG_FILE_PATH), "/var/log/mysite.log")


if __name__ == "__main__":
    pytest.main([__file__])
