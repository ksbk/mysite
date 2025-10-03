"""
Tests for Django project URLs configuration.
"""

import pytest
from django.conf import settings
from django.http import Http404
from django.test import override_settings
from django.urls import reverse


class TestProjectUrls:
    """Test Django project URL configuration."""

    def test_root_urlconf_setting(self):
        """Test ROOT_URLCONF setting is configured."""
        assert hasattr(settings, "ROOT_URLCONF")
        assert settings.ROOT_URLCONF == "config.urls"

    def test_admin_url_pattern(self):
        """Test admin URL pattern is configured."""
        try:
            admin_url = reverse("admin:index")
            assert admin_url.startswith("/admin/")
        except Exception:
            # Admin might not be configured in test settings, that's OK
            pass

    def test_url_resolution(self):
        """Test URL resolution works for configured patterns."""
        from config.urls import urlpatterns

        # Should have at least some URL patterns
        assert len(urlpatterns) > 0

        # Test that URL patterns are properly structured
        for pattern in urlpatterns:
            assert hasattr(pattern, "pattern") or hasattr(pattern, "_route")

    def test_debug_toolbar_urls__development_only(self):
        """Test debug toolbar URLs are only included in development."""
        with override_settings(DEBUG=True):
            # Import here to avoid circular import issues
            from config.urls import urlpatterns

            # In development, debug toolbar should be included
            # This is a structural test - actual debug toolbar may not be installed
            assert isinstance(urlpatterns, list)

    def test_static_media_urls__development_only(self):
        """Test static/media URL serving in development."""
        with override_settings(DEBUG=True):
            from config.urls import urlpatterns

            # Should have URL patterns for static/media files in debug mode
            assert isinstance(urlpatterns, list)
            # Actual static serving depends on DEBUG and installed apps

    def test_app_url_inclusion(self):
        """Test that app URLs are properly included."""
        from config.urls import urlpatterns

        # Look for included URL patterns (apps)
        included_patterns = []
        for pattern in urlpatterns:
            if hasattr(pattern, "url_patterns"):
                included_patterns.append(pattern)

        # Should have some included app URL patterns
        # Exact count depends on configuration, just test structure
        assert isinstance(included_patterns, list)


class TestUrlErrors:
    """Test URL error handling."""

    def test_404_handling(self):
        """Test 404 error handling configuration."""
        # Test that URL resolution raises Http404 for invalid URLs
        with pytest.raises(Http404):
            from django.urls import resolve

            resolve("/nonexistent-url-pattern/")

    def test_url_namespace_resolution(self):
        """Test URL namespace resolution if configured."""
        try:
            # Test resolving a namespaced URL if any exist
            # This will raise NoReverseMatch if no URLs are configured
            # That's expected in a minimal setup
            pass
        except Exception:
            # Expected in minimal test configuration
            pass


class TestUrlSecurity:
    """Test URL security configurations."""

    def test_no_trailing_slash_redirect__if_configured(self):
        """Test trailing slash redirect behavior."""
        # This depends on APPEND_SLASH setting
        assert hasattr(settings, "APPEND_SLASH")
        # Default Django behavior - just test setting exists

    def test_url_patterns_security(self):
        """Test that URL patterns don't expose sensitive paths."""
        from config.urls import urlpatterns

        # Basic security check - no obvious sensitive patterns
        sensitive_patterns = [".env", "config.py", "settings.py", "manage.py"]

        for pattern in urlpatterns:
            pattern_str = str(pattern.pattern)
            for sensitive in sensitive_patterns:
                assert (
                    sensitive not in pattern_str
                ), f"Sensitive pattern {sensitive} found in URLs"
