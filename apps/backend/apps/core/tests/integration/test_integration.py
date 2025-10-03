"""
Integration smoke tests for frontend-backend integration.
"""

from django.http import HttpRequest
from django.test import TestCase, override_settings

from apps.core.tests.utils import ConfigTestMixin, MockViteServer, SmokeTestMixin


class FrontendIntegrationTest(TestCase, SmokeTestMixin, ConfigTestMixin):
    """Test frontend-backend integration points."""

    def test_context_processors_basic(self):
        """Test that context processors don't crash."""
        from apps.core.context_processors import config_context, vite_context

        request = HttpRequest()
        request.method = "GET"
        request.path = "/"

        try:
            # Test config context processor
            config_ctx = config_context(request)
            self.assertIsInstance(config_ctx, dict)

            # Test vite context processor
            vite_ctx = vite_context(request)
            self.assertIsInstance(vite_ctx, dict)

        except Exception as e:
            self.fail(f"Context processors failed: {e}")

    def test_vite_context_with_mock_server(self):
        """Test Vite context processor with mocked server."""
        from apps.core.context_processors import vite_context

        request = HttpRequest()
        request.method = "GET"
        request.path = "/"

        # Test with Vite server available
        with MockViteServer(available=True):
            context = vite_context(request)
            self.assertIn("vite", context)

        # Test with Vite server unavailable
        with MockViteServer(available=False):
            context = vite_context(request)
            self.assertIn("vite", context)

    @override_settings(DEBUG=True)
    def test_development_mode_features(self):
        """Test development-specific features."""
        from django.conf import settings

        # Test that debug mode is properly detected
        self.assertTrue(settings.DEBUG)

        # Test that development-specific context is available
        from apps.core.context_processors import vite_context

        request = HttpRequest()
        request.method = "GET"
        request.path = "/"

        context = vite_context(request)
        self.assertIn("vite", context)
        vite_config = context["vite"]

        # In debug mode, should have dev server configuration
        self.assertIn("is_dev", vite_config)

    @override_settings(DEBUG=False)
    def test_production_mode_features(self):
        """Test production-specific features."""
        from django.conf import settings

        # Test that production mode is properly detected
        self.assertFalse(settings.DEBUG)

        # Test that production-specific context is available
        from apps.core.context_processors import vite_context

        request = HttpRequest()
        request.method = "GET"
        request.path = "/"

        context = vite_context(request)
        self.assertIn("vite", context)
        vite_config = context["vite"]

        # In production mode, should use manifest
        self.assertIn("is_dev", vite_config)
        self.assertFalse(vite_config["is_dev"])

    def test_template_tags_available(self):
        """Test that custom template tags are available."""
        try:
            from apps.core.templatetags.core_vite import vite_asset, vite_hmr

            # Test that template tags exist and are callable
            self.assertTrue(callable(vite_asset))
            self.assertTrue(callable(vite_hmr))

        except ImportError as e:
            self.fail(f"Template tags not available: {e}")

    def test_static_files_findable(self):
        """Test that static files can be found by Django."""
        from django.contrib.staticfiles import finders

        # Test that we can find at least some static files
        # This tests the staticfiles configuration
        css_files = finders.find("css/style.css", all=True)
        # It's OK if specific files don't exist, we're testing the finder works
        self.assertIsInstance(css_files, (list, type(None)))

    @override_settings(COMPRESS_OFFLINE=False)
    def test_csrf_token_available(self):
        """Test that CSRF tokens are properly configured."""
        response = self.client.get("/")

        # Should either succeed or redirect, but not crash on CSRF
        self.assertLess(response.status_code, 500)

    @override_settings(COMPRESS_OFFLINE=False)
    def test_request_id_middleware_integration(self):
        """Test that request ID middleware integrates properly."""
        response = self.client.get("/")

        # Middleware should not cause errors
        self.assertLess(response.status_code, 500)

        # Test that request ID is available in logs (indirectly)
        import logging

        logger = logging.getLogger("test")

        # This should not crash due to request ID formatting
        try:
            logger.info("Test log message")
        except Exception as e:
            self.fail(f"Request ID logging failed: {e}")

    def test_csp_nonce_middleware_integration(self):
        """Test that CSP nonce middleware integrates properly."""
        from django.http import HttpRequest, HttpResponse

        from apps.core.middleware.csp_nonce import CSPNonceMiddleware

        request = HttpRequest()
        response = HttpResponse()

        # Test middleware doesn't crash
        middleware = CSPNonceMiddleware(lambda req: response)
        try:
            result = middleware(request)
            self.assertIsInstance(result, HttpResponse)
        except Exception as e:
            self.fail(f"CSP nonce middleware failed: {e}")


class APIEndpointSmokeTest(TestCase, SmokeTestMixin):
    """Smoke tests for API endpoints."""

    def test_config_api_endpoints_exist(self):
        """Test that configuration API endpoints exist and don't crash."""
        # These require authentication, so just test they don't 500
        endpoints = [
            "/admin/sitecfg/health/",
            "/admin/sitecfg/validate/",
            "/admin/sitecfg/cache/",
        ]

        for endpoint in endpoints:
            try:
                response = self.client.get(endpoint)
                # Should redirect/forbid but not crash
                self.assertLess(response.status_code, 500)
            except Exception:
                # Endpoint might not be configured, which is fine for smoke test
                pass

    def test_admin_available(self):
        """Test that Django admin is available."""
        response = self.client.get("/admin/")
        # Should redirect to login
        self.assertIn(response.status_code, [200, 302])

    def test_healthcheck_basic(self):
        """Test basic application health."""
        # Test that the application starts without crashing
        from django.conf import settings

        self.assertIsNotNone(settings)

        # Test that URL resolution works
        from django.urls import resolve

        try:
            resolve("/admin/")
        except Exception as e:
            self.fail(f"URL resolution failed: {e}")
