"""
Comprehensive tests for the configuration loader system.
"""

from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from ..config import ConfigLoader
from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class ConfigLoaderTestCase(TestCase):
    """Test configuration loader functionality."""

    def setUp(self):
        """Set up test data."""
        # Clear cache before each test
        cache.clear()

        # Create test configuration instances
        self.site_config = SiteConfig.objects.create(
            site_name="Test Site",
            site_tagline="A test site",
            domain="testsite.com",
            contact_email="test@testsite.com",
            feature_flags={"feature1": True, "feature2": False},
        )

        self.seo_config = SEOConfig.objects.create(
            meta_title="Test Title",
            meta_description="Test description for SEO",
            noindex=False,
            google_analytics_id="G-TEST123",
        )

        self.theme_config = ThemeConfig.objects.create(
            primary_color="#ff0000", secondary_color="#00ff00", dark_mode_enabled=True
        )

        self.content_config = ContentConfig.objects.create(
            maintenance_mode=False,
            comments_enabled=True,
            max_upload_size_mb=5,
            allowed_file_extensions=[".jpg", ".png", ".gif"],
        )

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_get_global_config_from_database(self):
        """Test loading global config from database."""
        config = ConfigLoader.get_global_config(use_cache=False)

        # Test site config
        self.assertEqual(config.site.site_name, "Test Site")
        self.assertEqual(config.site.site_tagline, "A test site")
        self.assertEqual(config.site.domain, "testsite.com")
        self.assertEqual(config.site.contact_email, "test@testsite.com")
        self.assertEqual(config.site.feature_flags["feature1"], True)

        # Test SEO config
        self.assertEqual(config.seo.meta_title, "Test Title")
        self.assertEqual(config.seo.meta_description, "Test description for SEO")
        self.assertEqual(config.seo.noindex, False)
        self.assertEqual(config.seo.google_analytics_id, "G-TEST123")

        # Test theme config
        self.assertEqual(config.theme.primary_color, "#ff0000")
        self.assertEqual(config.theme.secondary_color, "#00ff00")
        self.assertEqual(config.theme.dark_mode_enabled, True)

        # Test content config
        self.assertEqual(config.content.maintenance_mode, False)
        self.assertEqual(config.content.comments_enabled, True)
        self.assertEqual(config.content.max_upload_size_mb, 5)
        self.assertEqual(
            config.content.allowed_file_extensions, [".jpg", ".png", ".gif"]
        )

    def test_get_global_config_with_cache(self):
        """Test config caching functionality."""
        # First call should hit database
        ConfigLoader.get_global_config(use_cache=True)

        # Update database without invalidating cache
        self.site_config.site_name = "Updated Name"
        self.site_config.save()

        # Second call should use cache (old value)
        config2 = ConfigLoader.get_global_config(use_cache=True)
        self.assertEqual(config2.site.site_name, "Test Site")  # Old cached value

        # Clear cache and try again
        ConfigLoader.invalidate_cache()
        config3 = ConfigLoader.get_global_config(use_cache=True)
        self.assertEqual(config3.site.site_name, "Updated Name")  # New value

    def test_get_config_value_dot_notation(self):
        """Test getting specific config values by dot notation."""
        # Test various paths
        self.assertEqual(ConfigLoader.get_config_value("site.site_name"), "Test Site")
        self.assertEqual(ConfigLoader.get_config_value("seo.noindex"), False)
        self.assertEqual(
            ConfigLoader.get_config_value("theme.primary_color"), "#ff0000"
        )
        self.assertEqual(ConfigLoader.get_config_value("content.max_upload_size_mb"), 5)

        # Test non-existent paths
        self.assertEqual(
            ConfigLoader.get_config_value("nonexistent.path", "default"), "default"
        )
        self.assertIsNone(ConfigLoader.get_config_value("another.missing.path"))

    def test_get_individual_config_sections(self):
        """Test getting individual config sections."""
        site_config = ConfigLoader.get_site_config()
        self.assertEqual(site_config["site_name"], "Test Site")
        self.assertEqual(site_config["feature_flags"]["feature1"], True)

        seo_config = ConfigLoader.get_seo_config()
        self.assertEqual(seo_config["meta_title"], "Test Title")

        theme_config = ConfigLoader.get_theme_config()
        self.assertEqual(theme_config["primary_color"], "#ff0000")

        content_config = ConfigLoader.get_content_config()
        self.assertEqual(content_config["maintenance_mode"], False)

    def test_fallback_on_database_error(self):
        """Test fallback to default config when database fails."""
        with patch("apps.core.config.loader.transaction") as mock_transaction:
            # Simulate database error
            mock_transaction.atomic.side_effect = Exception("Database error")

            # Should return default config
            config = ConfigLoader.get_global_config(use_cache=False)

            # Should have default values
            self.assertEqual(config.site.site_name, "My Site")
            self.assertEqual(config.seo.noindex, False)
            self.assertEqual(config.theme.primary_color, "#007bff")
            self.assertEqual(config.content.maintenance_mode, False)

    def test_convenience_functions(self):
        """Test convenience functions for common values."""
        from ..config.loader import (
            get_maintenance_mode,
            get_primary_color,
            get_site_name,
            is_noindex_enabled,
        )

        self.assertEqual(get_site_name(), "Test Site")
        self.assertEqual(get_maintenance_mode(), False)
        self.assertEqual(is_noindex_enabled(), False)
        self.assertEqual(get_primary_color(), "#ff0000")

        # Test with fallbacks
        self.assertEqual(get_site_name("Fallback"), "Test Site")
        self.assertEqual(get_maintenance_mode(True), False)  # DB value overrides

    def test_cache_invalidation(self):
        """Test cache invalidation functionality."""
        # Load config to populate cache
        ConfigLoader.get_global_config(use_cache=True)

        # Verify cache has data
        cached_data = cache.get("core:site_config:resolved:v1")
        self.assertIsNotNone(cached_data)

        # Invalidate cache
        ConfigLoader.invalidate_cache()

        # Verify cache is cleared
        cached_data = cache.get("core:site_config:resolved:v1")
        self.assertIsNone(cached_data)

    def test_model_to_dict_conversion(self):
        """Test model instance to dict conversion."""
        site_dict = ConfigLoader._model_to_dict(self.site_config)

        # Should include model fields (excluding internal ones)
        self.assertIn("site_name", site_dict)
        self.assertIn("site_tagline", site_dict)
        self.assertIn("feature_flags", site_dict)

        # Should exclude internal fields
        self.assertNotIn("id", site_dict)
        self.assertNotIn("created_at", site_dict)
        self.assertNotIn("updated_at", site_dict)

        # Values should match
        self.assertEqual(site_dict["site_name"], "Test Site")
        self.assertEqual(
            site_dict["feature_flags"], {"feature1": True, "feature2": False}
        )


class SingletonModelTestCase(TestCase):
    """Test singleton model functionality."""

    def test_site_config_singleton(self):
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

    def test_load_method(self):
        """Test the load() class method."""
        # First call should create instance
        config1 = SiteConfig.load()
        self.assertEqual(SiteConfig.objects.count(), 1)

        # Second call should return same instance
        config2 = SiteConfig.load()
        self.assertEqual(config1.pk, config2.pk)

        # Should still be only one instance
        self.assertEqual(SiteConfig.objects.count(), 1)


class ModelValidationTestCase(TestCase):
    """Test model validation functionality."""

    def test_theme_config_color_validation(self):
        """Test color format validation."""
        # Valid colors should work
        theme = ThemeConfig(primary_color="#ff0000", secondary_color="#00FF00")
        theme.full_clean()  # Should not raise

        # Invalid colors should raise validation error
        theme_invalid = ThemeConfig(
            primary_color="red",  # Not hex format
            secondary_color="#00FF00",
        )

        with self.assertRaises(Exception):  # ValidationError or similar
            theme_invalid.full_clean()

    def test_content_config_validation(self):
        """Test content config validation."""
        # Valid config should work
        content = ContentConfig(max_upload_size_mb=10)
        content.full_clean()  # Should not raise

        # Invalid size should raise error
        content_invalid = ContentConfig(max_upload_size_mb=0)
        with self.assertRaises(Exception):
            content_invalid.full_clean()

        # Too large size should raise error
        content_too_large = ContentConfig(max_upload_size_mb=200)
        with self.assertRaises(Exception):
            content_too_large.full_clean()
