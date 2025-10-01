"""
Tests for core config template tags.
"""

from django.template import Context, Template
from django.test import RequestFactory, TestCase

from ...models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class CoreConfigTemplateTagsTest(TestCase):
    """Test core config template tags."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()

        # Create test configurations
        self.site_config = SiteConfig.objects.create(
            site_name="Test Site",
            site_tagline="A test site for testing",
            feature_flags={"pwa": True, "dark_mode": False},
        )

        self.seo_config = SEOConfig.objects.create(
            meta_title="Test Title", meta_description="Test description", noindex=False
        )

        self.theme_config = ThemeConfig.objects.create(
            primary_color="#ff0000", secondary_color="#00ff00"
        )

        self.content_config = ContentConfig.objects.create(
            maintenance_mode=False, comments_enabled=True
        )

    def test_config_tag_basic(self):
        """Test basic config tag functionality."""
        template = Template("{% load core_config %}{% config 'site.site_name' %}")
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "Test Site")

    def test_config_tag_with_default(self):
        """Test config tag with default value."""
        template = Template(
            "{% load core_config %}{% config 'nonexistent.path' 'Default Value' %}"
        )
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "Default Value")

    def test_config_tag_nested_path(self):
        """Test config tag with nested dot notation."""
        template = Template("{% load core_config %}{% config 'seo.meta_title' %}")
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "Test Title")

    def test_site_name_tag(self):
        """Test site_name convenience tag."""
        template = Template("{% load core_config %}{% site_name %}")
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "Test Site")

    def test_maintenance_mode_tag(self):
        """Test maintenance_mode tag."""
        template = Template(
            "{% load core_config %}"
            "{% maintenance_mode as is_maintenance %}"
            "{% if is_maintenance %}MAINTENANCE{% else %}NORMAL{% endif %}"
        )
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "NORMAL")

    def test_noindex_enabled_tag(self):
        """Test noindex_enabled tag."""
        template = Template(
            "{% load core_config %}"
            "{% noindex_enabled as noindex %}"
            "{% if noindex %}NOINDEX{% else %}INDEX{% endif %}"
        )
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "INDEX")

    def test_get_feature_flag_filter(self):
        """Test get_feature_flag template filter."""
        template = Template(
            "{% load core_config %}"
            "{% config 'site.feature_flags' as flags %}"
            "{% if flags|get_feature_flag:'pwa' %}PWA_ON{% else %}PWA_OFF{% endif %}"
        )
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "PWA_ON")

    def test_get_feature_flag_filter_false(self):
        """Test get_feature_flag filter with false value."""
        template = Template(
            "{% load core_config %}"
            "{% config 'site.feature_flags' as flags %}"
            "{% if flags|get_feature_flag:'dark_mode' %}DARK{% else %}LIGHT{% endif %}"
        )
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "LIGHT")

    def test_get_feature_flag_filter_missing(self):
        """Test get_feature_flag filter with missing flag."""
        template = Template(
            "{% load core_config %}"
            "{% config 'site.feature_flags' as flags %}"
            "{% if flags|get_feature_flag:'missing' %}EXISTS{% else %}MISSING{% endif %}"
        )
        request = self.factory.get("/")

        rendered = template.render(Context({"request": request}))
        self.assertEqual(rendered, "MISSING")
