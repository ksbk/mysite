from django.test import RequestFactory, TestCase

from apps.core.models import SiteConfig
from apps.core.sitecfg.loader import invalidate_cache, resolve_config


class ConfigLoaderCacheTest(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.req = self.rf.get("/")
        # Ensure a SiteConfig exists
        if not SiteConfig.objects.exists():
            SiteConfig.objects.create(site_name="A")

    def test_siteconfig_cache_refresh_on_save(self):
        sc = SiteConfig.objects.first()

        # Warm cache
        data1 = resolve_config(self.req)
        self.assertIn(
            data1["site"].get("site_name"),
            ("A", sc.site_name),
        )

        # Change value and save (signals should invalidate cache)
        sc.site_name = "B"
        sc.save()

        data2 = resolve_config(self.req)
        self.assertEqual(data2["site"].get("site_name"), "B")

    def test_manual_invalidate_cache(self):
        sc = SiteConfig.objects.first()
        sc.site_name = "C"
        sc.save()

        invalidate_cache()
        data3 = resolve_config(self.req)
        self.assertIn(data3["site"].get("site_name"), ("B", "C"))
