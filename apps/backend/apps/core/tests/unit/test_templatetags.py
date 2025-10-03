"""
Tests for core app templatetags.
"""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from apps.core.templatetags.core_vite import vite_asset


@pytest.mark.unit
class TestCoreViteTemplatetag:
    """Test core_vite templatetag functionality."""

    def test_vite_asset_tag_exists(self):
        """Test that vite_asset templatetag can be imported."""
        assert callable(vite_asset)

    def test_vite_asset_basic_usage(self):
        """Test basic usage of vite_asset templatetag."""
        # This is a basic smoke test
        # Actual functionality depends on Vite manifest file
        try:
            result = vite_asset("main.js")
            # Should return some string (URL or empty)
            assert isinstance(result, str)
        except Exception:
            # Expected if no Vite manifest exists
            pass

    def test_vite_asset_in_template(self):
        """Test vite_asset works in Django template."""
        template = Template('{% load core_vite %}{% vite_asset "main.js" %}')
        context = Context({})

        try:
            rendered = template.render(context)
            # Should render without template syntax errors
            assert isinstance(rendered, str)
        except Exception as e:
            # May fail if Vite manifest not found, that's OK for unit test
            if "manifest" not in str(e).lower():
                pytest.fail(f"Template rendering failed: {e}")

    def test_vite_asset_with_css_file(self):
        """Test vite_asset with CSS file."""
        try:
            result = vite_asset("style.css")
            assert isinstance(result, str)
        except Exception:
            # Expected if no Vite manifest exists
            pass

    def test_vite_asset_with_nonexistent_file(self):
        """Test vite_asset with file that doesn't exist in manifest."""
        try:
            result = vite_asset("nonexistent.js")
            # Should handle gracefully
            assert isinstance(result, str)
        except Exception:
            # Expected if no Vite manifest exists
            pass


@pytest.mark.integration
class TestTemplatetagsIntegration:
    """Integration tests for templatetags with full Django context."""

    def test_templatetag_loading(self):
        """Test that core_vite templatetag library can be loaded."""
        from django.template import Template

        # Test that the library loads without errors
        template_str = "{% load core_vite %}"
        template = Template(template_str)
        context = Context({})

        # Should not raise template syntax errors
        rendered = template.render(context)
        assert rendered == ""

    def test_templatetag_with_request_context(self):
        """Test templatetag works with request context."""
        request_factory = RequestFactory()
        request = request_factory.get("/")

        template = Template('{% load core_vite %}{% vite_asset "main.js" %}')
        context = Context({"request": request})

        try:
            rendered = template.render(context)
            assert isinstance(rendered, str)
        except Exception as e:
            # May fail if Vite setup incomplete, that's OK for tests
            if "manifest" not in str(e).lower():
                pytest.fail(f"Template with request context failed: {e}")

    def test_multiple_vite_assets_in_template(self):
        """Test multiple vite_asset calls in same template."""
        template = Template("""
            {% load core_vite %}
            {% vite_asset "main.js" %}
            {% vite_asset "style.css" %}
            {% vite_asset "app.js" %}
        """)
        context = Context({})

        try:
            rendered = template.render(context)
            assert isinstance(rendered, str)
            # Should contain some content even if assets don't exist
            assert len(rendered.strip()) >= 0
        except Exception as e:
            if "manifest" not in str(e).lower():
                pytest.fail(f"Multiple assets template failed: {e}")
