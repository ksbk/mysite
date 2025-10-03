"""
Test configuration for core app.

This conftest.py provides fixtures and factories specifically for the core app,
including configuration models, middleware, templatetags, and site configuration.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.core.models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from apps.core.sitecfg.audit_models import ConfigAudit, ConfigVersion

User = get_user_model()


@pytest.fixture
def request_factory():
    """Django RequestFactory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def staff_user():
    """Create a staff user for admin/management tests."""
    return User.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="staffpass123",
        is_staff=True,
    )


@pytest.fixture
def superuser():
    """Create a superuser for admin tests."""
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def site_config():
    """Create a basic SiteConfig instance."""
    return SiteConfig.objects.create(
        site_name="Test Site",
        site_description="A test site for unit testing",
        contact_email="contact@testsite.com",
        maintenance_mode=False,
    )


@pytest.fixture
def seo_config():
    """Create a basic SEOConfig instance."""
    return SEOConfig.objects.create(
        default_title="Test Site",
        default_description="Test site description",
        default_keywords="test, site, django",
        google_analytics_id="GA-TEST-123",
        google_site_verification="test-verification-123",
    )


@pytest.fixture
def theme_config():
    """Create a basic ThemeConfig instance."""
    return ThemeConfig.objects.create(
        primary_color="#007bff",
        secondary_color="#6c757d",
        accent_color="#28a745",
        font_family="Inter, sans-serif",
        dark_mode_enabled=True,
    )


@pytest.fixture
def content_config():
    """Create a basic ContentConfig instance."""
    return ContentConfig.objects.create(
        posts_per_page=10,
        allow_comments=True,
        comment_moderation=True,
        show_author_info=True,
        enable_related_posts=True,
    )


@pytest.fixture
def config_audit():
    """Create a ConfigAudit entry for testing."""
    return ConfigAudit.objects.create(
        model_name="SiteConfig",
        object_id="1",
        action="CREATE",
        old_values={},
        new_values={"site_name": "Test Site"},
        changed_fields=["site_name"],
    )


@pytest.fixture
def config_version():
    """Create a ConfigVersion entry for testing."""
    return ConfigVersion.objects.create(
        config_type="site",
        version_number=1,
        config_data={"site_name": "Test Site v1"},
        description="Initial version",
    )


@pytest.fixture
def mock_request(request_factory, test_user):
    """Create a mock request with authenticated user."""
    request = request_factory.get("/")
    request.user = test_user
    return request


@pytest.fixture
def staff_request(request_factory, staff_user):
    """Create a mock request with staff user."""
    request = request_factory.get("/")
    request.user = staff_user
    return request


@pytest.fixture
def clean_config_data():
    """Clean configuration data for testing validation."""
    return {
        "site": {
            "site_name": "Clean Test Site",
            "site_description": "A clean test site",
            "contact_email": "clean@test.com",
            "maintenance_mode": False,
        },
        "seo": {
            "default_title": "Clean SEO Title",
            "default_description": "Clean SEO description",
            "default_keywords": "clean, test",
            "google_analytics_id": "GA-CLEAN-123",
        },
        "theme": {
            "primary_color": "#007bff",
            "secondary_color": "#6c757d",
            "dark_mode_enabled": False,
        },
        "content": {
            "posts_per_page": 10,
            "allow_comments": True,
            "comment_moderation": False,
        },
    }


@pytest.fixture
def invalid_config_data():
    """Invalid configuration data for testing validation errors."""
    return {
        "site": {
            "site_name": "",  # Invalid: empty
            "contact_email": "invalid-email",  # Invalid: not an email
            "maintenance_mode": "yes",  # Invalid: not boolean
        },
        "seo": {
            "default_title": "x" * 200,  # Invalid: too long
            "default_description": "x" * 500,  # Invalid: too long
        },
        "theme": {
            "primary_color": "not-a-color",  # Invalid: not hex color
            "dark_mode_enabled": "maybe",  # Invalid: not boolean
        },
    }
