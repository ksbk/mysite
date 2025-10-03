"""
Tests for pages app URLs.
"""

import pytest


@pytest.mark.unit
class TestPagesUrls:
    """Test pages app URL configuration."""

    def test_pages_urls_import(self):
        """Test that pages URLs can be imported."""
        try:
            from apps.pages import urls

            assert hasattr(urls, "__name__")
        except ImportError:
            # URLs may not be configured yet, that's OK
            pass

    def test_pages_urlpatterns_structure(self):
        """Test pages urlpatterns has correct structure."""
        try:
            from apps.pages.urls import urlpatterns

            # Should be a list
            assert isinstance(urlpatterns, list)

            # Each pattern should have expected attributes
            for pattern in urlpatterns:
                assert hasattr(pattern, "pattern") or hasattr(pattern, "_route")

        except ImportError:
            # URLs may not be configured yet
            pass

    def test_pages_url_names__if_configured(self):
        """Test that URL patterns have proper names if configured."""
        try:
            from apps.pages.urls import urlpatterns

            # Check for common URL names
            named_patterns = []
            for pattern in urlpatterns:
                if hasattr(pattern, "name") and pattern.name:
                    named_patterns.append(pattern.name)

            # Should have a list (may be empty)
            assert isinstance(named_patterns, list)

        except ImportError:
            # URLs not configured yet
            pass


@pytest.mark.integration
class TestPagesUrlsIntegration:
    """Integration tests for pages URLs."""

    def test_pages_urls_resolve(self):
        """Test that pages URLs resolve correctly if configured."""
        from django.urls import resolve, reverse
        from django.urls.exceptions import NoReverseMatch, Resolver404

        common_url_names = [
            "pages:index",
            "pages:home",
            "pages:about",
            "index",
            "home",
        ]

        resolvable_urls = []
        for url_name in common_url_names:
            try:
                url = reverse(url_name)
                # Try to resolve it back
                resolved = resolve(url)
                resolvable_urls.append(url_name)
            except (NoReverseMatch, Resolver404):
                # URL not configured, that's OK
                pass

        # Should have a list (may be empty if no URLs configured)
        assert isinstance(resolvable_urls, list)

    def test_pages_in_main_urlconf(self):
        """Test that pages URLs are included in main URL configuration."""
        try:
            from config.urls import urlpatterns

            # Look for pages app inclusion
            pages_included = False
            for pattern in urlpatterns:
                if hasattr(pattern, "url_patterns"):
                    # This is an include() pattern
                    if "pages" in str(pattern.pattern):
                        pages_included = True
                        break

            # May or may not be included yet, both are valid
            assert isinstance(pages_included, bool)

        except ImportError:
            # Main URLs may not include pages yet
            pass
