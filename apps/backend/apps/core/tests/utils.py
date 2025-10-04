"""
Test utilities and fixtures for smoke tests.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model

User = get_user_model()


class SmokeTestMixin:
    """Mixin providing common smoke test utilities."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",  # pragma: allowlist secret (test-only)
        )

        cls.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="staffpass123",  # nosec B106 (test-only)
            is_staff=True,
        )

    def assert_response_ok_or_redirect(self, response):
        """Assert response is either OK or a redirect (not an error)."""
        self.assertIn(response.status_code, [200, 201, 301, 302, 304])

    def assert_no_server_error(self, response):
        """Assert response is not a server error."""
        self.assertLess(response.status_code, 500)


class MockViteServer:
    """Mock Vite development server for testing."""

    def __init__(self, available=True):
        self.available = available

    def __enter__(self):
        """Mock Vite server availability check."""

        def mock_check_vite_available(url):
            return self.available

        self.patcher = patch("apps.core.context_processors._check_vite_available")
        self.mock_check = self.patcher.start()
        self.mock_check.side_effect = mock_check_vite_available
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop mocking."""
        self.patcher.stop()


class ConfigTestMixin:
    """Mixin for testing configuration system."""

    def create_test_config(self):
        """Create test configuration data."""
        from apps.core.models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig

        site_config = SiteConfig.objects.create(
            site_name="Test Site",
            site_description="A test site",
            contact_email="admin@test.com",
        )

        seo_config = SEOConfig.objects.create(
            title="Test Site - Home",
            description="Test site description",
            keywords="test, site, django",
        )

        theme_config = ThemeConfig.objects.create(
            primary_color="#007bff",
            secondary_color="#6c757d",
            font_family="Inter, sans-serif",
        )

        content_config = ContentConfig.objects.create(
            maintenance_mode=False, show_coming_soon=False
        )

        return {
            "site": site_config,
            "seo": seo_config,
            "theme": theme_config,
            "content": content_config,
        }

    def mock_config_loader(self, config_data=None):
        """Mock the configuration loader."""
        if config_data is None:
            config_data = {
                "site": {"site_name": "Test Site"},
                "seo": {"title": "Test Title"},
                "theme": {"primary_color": "#007bff"},
                "content": {"maintenance_mode": False},
            }

        return patch("apps.core.sitecfg.get_config", return_value=config_data)


class DatabaseTestMixin:
    """Mixin for database testing utilities."""

    def assert_model_exists(self, model_class):
        """Assert that a model class exists and has a table."""
        self.assertTrue(hasattr(model_class, "_meta"))
        self.assertTrue(hasattr(model_class._meta, "db_table"))

    def assert_field_exists(self, model_class, field_name):
        """Assert that a model has a specific field."""
        self.assertTrue(hasattr(model_class, field_name))
        field = model_class._meta.get_field(field_name)
        self.assertIsNotNone(field)
