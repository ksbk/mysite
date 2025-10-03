"""
Test configuration for pages app.

This conftest.py provides fixtures and factories specifically for the pages app,
including page models, views, and URL routing tests.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory

User = get_user_model()


@pytest.fixture
def request_factory():
    """Django RequestFactory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def mock_request(request_factory, test_user):
    """Create a mock request with authenticated user."""
    request = request_factory.get("/")
    request.user = test_user
    return request


@pytest.fixture
def anonymous_request(request_factory):
    """Create a mock request without authenticated user."""
    from django.contrib.auth.models import AnonymousUser

    request = request_factory.get("/")
    request.user = AnonymousUser()
    return request


# Add page-specific fixtures here when page models are created
# Example:
# @pytest.fixture
# def sample_page():
#     """Create a sample page for testing."""
#     from apps.pages.models import Page
#     return Page.objects.create(
#         title='Test Page',
#         slug='test-page',
#         content='Test page content',
#         is_published=True
#     )
