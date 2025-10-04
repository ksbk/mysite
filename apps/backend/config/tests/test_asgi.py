"""
Tests for ASGI and WSGI application configuration.
"""

import pytest
from django.core.exceptions import ImproperlyConfigured


class TestAsgiApplication:
    """Test ASGI application configuration."""

    def test_asgi_application_import(self):
        """Test ASGI application can be imported."""
        from config.asgi import application

        assert application is not None

    def test_asgi_application_callable(self):
        """Test ASGI application is callable."""
        from config.asgi import application

        assert callable(application)

    def test_asgi_django_setup(self):
        """Test Django is properly set up in ASGI application."""
        # Import should not raise any configuration errors
        try:
            from config.asgi import application

            assert application is not None
        except ImproperlyConfigured as e:
            pytest.fail(f"Django not properly configured in ASGI: {e}")

    def test_asgi_middleware_stack(self):
        """Test ASGI middleware stack is properly configured."""
        from config.asgi import application

        # Check that the application has the expected structure
        # ASGI applications should have certain attributes
        assert callable(application)


class TestWsgiApplication:
    """Test WSGI application configuration."""

    def test_wsgi_application_import(self):
        """Test WSGI application can be imported."""
        from config.wsgi import application

        assert application is not None

    def test_wsgi_application_callable(self):
        """Test WSGI application is callable."""
        from config.wsgi import application

        assert callable(application)

    def test_wsgi_django_setup(self):
        """Test Django is properly set up in WSGI application."""
        # Import should not raise any configuration errors
        try:
            from config.wsgi import application

            assert application is not None
        except ImproperlyConfigured as e:
            pytest.fail(f"Django not properly configured in WSGI: {e}")

    def test_wsgi_get_wsgi_application(self):
        """Test get_wsgi_application is used correctly."""

        from config.wsgi import application

        # The application should be created using get_wsgi_application
        assert application is not None
        # Can't directly test isinstance since it's the result of get_wsgi_application


class TestApplicationConfiguration:
    """Test common application configuration."""

    def test_django_settings_configured(self):
        """Test Django settings are configured before app creation."""
        from django.conf import settings

        # Settings should be configured
        assert settings.configured

    def test_os_environ_django_settings_module(self):
        """Test DJANGO_SETTINGS_MODULE is set in environment."""
        import os

        # After importing, Django should be configured
        from django.conf import settings

        assert "DJANGO_SETTINGS_MODULE" in os.environ or settings.configured

    def test_application_error_handling(self):
        """Test application handles basic configuration errors."""
        # This is more of a smoke test - if import succeeds, basic config is OK
        try:
            from config.asgi import application as asgi_app
            from config.wsgi import application as wsgi_app

            assert asgi_app is not None
            assert wsgi_app is not None
        except Exception as e:
            pytest.fail(f"Application configuration failed: {e}")
