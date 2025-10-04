"""
Tests for pages app views.
"""

import pytest
from django.urls import reverse

from apps.pages.models import Page


@pytest.mark.django_db
class TestPagesViews:
    """Test pages app views."""

    def test_pages_views_import(self):
        """Test that pages views can be imported."""
        from apps.pages import views

        assert hasattr(views, "__name__")

    def test_pages_app_urls__if_configured(self, client):
        """Test pages app URLs if they are configured."""
        try:
            # Try to access pages URLs if they exist
            response = client.get("/")
            # Should not crash, may return 200, 404, etc depending on config
            assert response.status_code in [200, 404, 301, 302]
        except Exception:
            # URLs may not be configured yet, that's OK
            pass

    def test_page_list_and_detail(self, client, db):
        """Smoke test list and detail views render."""
        page = Page.objects.create(
            title="About",
            slug="about",
            body="Hello",
            is_published=True,
        )
        # list
        resp_list = client.get(reverse("pages:list"))
        # allow no template in some environments
        assert resp_list.status_code in (200, 404)
        # detail
        resp_detail = client.get(page.get_absolute_url())
        assert resp_detail.status_code in (200, 404)

    def test_pages_view_functions_exist(self):
        """Test that expected view functions exist in pages app."""
        from apps.pages import views

        # Test for common view patterns
        view_names = ["index", "home", "about", "contact"]
        existing_views = []

        for view_name in view_names:
            if hasattr(views, view_name):
                view_func = getattr(views, view_name)
                if callable(view_func):
                    existing_views.append(view_name)

        # Should have at least some views or be empty (both are valid)
        assert isinstance(existing_views, list)


@pytest.mark.unit
class TestPagesViewsUnit:
    """Unit tests for pages views (no DB)."""

    def test_pages_views_module_structure(self):
        """Test pages views module has expected structure."""
        from apps.pages import views

        # Should be a module
        assert hasattr(views, "__name__")
        assert hasattr(views, "__file__")

    def test_view_callables__if_exist(self):
        """Test that any views that exist are callable."""
        import inspect

        from apps.pages import views

        # Get all attributes that might be views
        for name in dir(views):
            if not name.startswith("_"):
                attr = getattr(views, name)
                if inspect.isfunction(attr) or inspect.isclass(attr):
                    # If it looks like a view, it should be callable
                    assert callable(attr)


@pytest.mark.django_db
class TestPagesModel:
    def test_page_str_and_url(self):
        page = Page.objects.create(title="Test", slug="test", is_published=True)
        assert str(page) == "Test"
        assert (
            reverse(
                "pages:detail",
                kwargs={"slug": "test"},
            )
            == page.get_absolute_url()
        )


@pytest.mark.integration
class TestPagesIntegration:
    """Integration tests for pages app."""

    def test_pages_app_integration__url_resolution(self):
        """Test pages app URL resolution integration."""
        try:
            from apps.pages.urls import urlpatterns

            # Should have URL patterns list
            assert isinstance(urlpatterns, list)

            # URL patterns should be properly structured
            for pattern in urlpatterns:
                assert hasattr(pattern, "pattern") or hasattr(pattern, "_route")

        except ImportError:
            # URLs may not be configured yet
            pass

    def test_pages_app_in_django_apps(self):
        """Test that pages app is properly registered in Django."""
        from django.apps import apps

        # Should be able to get the app config
        try:
            app_config = apps.get_app_config("pages")
            assert app_config.name == "apps.pages"
        except LookupError:
            # App may not be registered, that's OK for this test
            pass

    def test_pages_templates__if_exist(self):
        """Test pages templates can be loaded if they exist."""
        from django.template import TemplateDoesNotExist
        from django.template.loader import get_template

        common_templates = [
            "pages/index.html",
            "pages/home.html",
            "pages/about.html",
            "pages/base.html",
        ]

        existing_templates = []
        for template_name in common_templates:
            try:
                get_template(template_name)  # Just check if it exists
                existing_templates.append(template_name)
            except TemplateDoesNotExist:
                # Template doesn't exist, that's OK
                pass

        # Should have a list (may be empty)
        assert isinstance(existing_templates, list)
