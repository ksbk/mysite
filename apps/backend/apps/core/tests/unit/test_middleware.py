"""
Tests for core app middleware.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from apps.core.sitecfg.middleware import ConfigAuditMiddleware

User = get_user_model()


class TestConfigAuditMiddleware(SimpleTestCase):
    """Test ConfigAuditMiddleware functionality without database."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = ConfigAuditMiddleware(get_response=lambda r: HttpResponse())

    def test_middleware_initialization(self):
        """Test middleware can be initialized."""
        assert self.middleware is not None
        assert hasattr(self.middleware, "get_response")

    def test_middleware_process_request__anonymous_user(self):
        """Test middleware processes requests from anonymous users."""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        # Should not raise any exceptions
        result = self.middleware.process_request(request)
        assert result is None

    def test_middleware_process_request__authenticated_user(self):
        """Test middleware processes requests from authenticated users."""
        request = self.factory.get("/")
        # Create a mock user without database
        request.user = User(username="testuser", email="test@example.com")

        # Should not raise any exceptions
        result = self.middleware.process_request(request)
        assert result is None

    def test_middleware_process_response(self):
        """Test middleware processes responses correctly."""
        request = self.factory.get("/")
        request.user = AnonymousUser()
        response = HttpResponse("Test response")

        # Should return the same response
        result = self.middleware.process_response(request, response)
        assert result == response

    def test_middleware_in_request_response_cycle(self):
        """Test middleware works in full request/response cycle."""

        def simple_view(request):
            return HttpResponse("OK")

        middleware = ConfigAuditMiddleware(get_response=simple_view)
        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_middleware_callable(self):
        """Test middleware is callable."""
        self.assertTrue(callable(self.middleware))

    def test_middleware_get_response_attribute(self):
        """Test middleware stores get_response correctly."""

        def get_response(request):
            return HttpResponse()

        middleware = ConfigAuditMiddleware(get_response=get_response)
        self.assertEqual(middleware.get_response, get_response)
