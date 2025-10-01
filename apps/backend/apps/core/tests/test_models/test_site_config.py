"""
Tests for SiteConfig model functionality.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ...models import SiteConfig


class SiteConfigModelTest(TestCase):
    """Test SiteConfig model behavior."""

    def test_singleton_behavior(self):
        """Test that SiteConfig enforces singleton pattern."""
        # Create first instance
        config1 = SiteConfig.objects.create(site_name="Site 1")
        self.assertEqual(config1.pk, 1)

        # Create second instance - should overwrite first
        config2 = SiteConfig.objects.create(site_name="Site 2")
        self.assertEqual(config2.pk, 1)

        # Should only be one instance
        self.assertEqual(SiteConfig.objects.count(), 1)

        # Should have latest values
        latest = SiteConfig.objects.get()
        self.assertEqual(latest.site_name, "Site 2")

    def test_load_method_creates_instance(self):
        """Test that load() creates instance if none exists."""
        self.assertEqual(SiteConfig.objects.count(), 0)

        config = SiteConfig.load()
        self.assertEqual(SiteConfig.objects.count(), 1)
        self.assertEqual(config.site_name, "My Site")  # Default value

    def test_load_method_returns_existing(self):
        """Test that load() returns existing instance."""
        # Create instance
        created = SiteConfig.objects.create(site_name="Existing Site")

        # Load should return same instance
        loaded = SiteConfig.load()
        self.assertEqual(created.pk, loaded.pk)
        self.assertEqual(loaded.site_name, "Existing Site")

    def test_default_values(self):
        """Test model default values."""
        config = SiteConfig.load()
        self.assertEqual(config.site_name, "My Site")
        self.assertEqual(config.site_tagline, "")
        self.assertEqual(config.domain, "")
        self.assertEqual(config.contact_email, "")
        self.assertEqual(config.feature_flags, {})
        self.assertEqual(config.navigation, [])

    def test_feature_flags_json_field(self):
        """Test feature flags JSON field."""
        config = SiteConfig.objects.create(
            site_name="Test Site",
            feature_flags={"dark_mode": True, "beta_features": False},
        )

        # Reload from database
        config.refresh_from_db()
        self.assertEqual(config.feature_flags["dark_mode"], True)
        self.assertEqual(config.feature_flags["beta_features"], False)

    def test_navigation_json_field(self):
        """Test navigation JSON field."""
        nav_data = [
            {"label": "Home", "url": "/", "active": True},
            {"label": "About", "url": "/about/", "active": False},
        ]

        config = SiteConfig.objects.create(site_name="Test Site", navigation=nav_data)

        # Reload from database
        config.refresh_from_db()
        self.assertEqual(len(config.navigation), 2)
        self.assertEqual(config.navigation[0]["label"], "Home")
        self.assertEqual(config.navigation[1]["url"], "/about/")

    def test_str_representation(self):
        """Test string representation."""
        config = SiteConfig.objects.create(site_name="My Awesome Site")
        self.assertEqual(str(config), "My Awesome Site")
