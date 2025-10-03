import unittest

from django.test import SimpleTestCase

from apps.core.sitecfg.normalize import (
    PydanticAvailable as SchemasPydanticAvailable,
)
from apps.core.sitecfg.normalize import (
    normalize_config_dict,
    to_global_config,
)
from apps.core.sitecfg.schemas import (
    ContentConfigSchema,
    GlobalConfigSchema,
    SEOConfigSchema,
    SiteConfigSchema,
    ThemeConfigSchema,
)


@unittest.skipUnless(SchemasPydanticAvailable, "pydantic not installed")
class SchemasNormalizationTests(SimpleTestCase):
    def test_site_email_domain_normalization(self):
        raw = {
            "site": {
                "site_name": "  My Site  ",
                "contact_email": "INFO@EXAMPLE.COM",
                "domain": "example.com",
                "feature_flags": {"beta": True},
                "navigation": [{"label": "Home", "url": "/"}],
            }
        }
        norm = normalize_config_dict(raw)
        self.assertEqual(norm["site"]["site_name"], "My Site")
        self.assertEqual(norm["site"]["contact_email"], "info@example.com")
        self.assertEqual(norm["site"]["domain"], "example.com")
        self.assertTrue(norm["site"]["feature_flags"]["beta"])

    def test_theme_colors_uppercased(self):
        raw = {"theme": {"primary_color": "#00ff00", "secondary_color": "#abcdef"}}
        norm = normalize_config_dict(raw)
        self.assertEqual(norm["theme"]["primary_color"], "#00ff00")
        self.assertEqual(norm["theme"]["secondary_color"], "#abcdef")

    def test_invalid_canonical_url_raises(self):
        with self.assertRaises(ValueError):
            normalize_config_dict({"seo": {"canonical_url": "example.com"}})

    def test_to_global_config_defaults(self):
        cfg = to_global_config({"site": {"site_name": "Demo"}})
        self.assertIsInstance(cfg, GlobalConfigSchema)
        self.assertEqual(cfg.site.site_name, "Demo")
        self.assertIsInstance(cfg.site, SiteConfigSchema)
        # Ensure defaults from other sections
        self.assertIsInstance(cfg.seo, SEOConfigSchema)
        self.assertIsInstance(cfg.theme, ThemeConfigSchema)
        self.assertIsInstance(cfg.content, ContentConfigSchema)
