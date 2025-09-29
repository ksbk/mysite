from django.db import models


class SiteSettings(models.Model):
    """Singleton site-wide settings for meta/SEO/customization."""

    site_name = models.CharField(max_length=200, default="MySite")
    meta_description = models.CharField(max_length=300, blank=True, default="")
    meta_keywords = models.CharField(max_length=300, blank=True, default="")
    og_image = models.URLField(blank=True, default="")

    class Meta:
        verbose_name = "Site settings"

    def __str__(self) -> str:  # pragma: no cover
        return "Site Settings"

    @classmethod
    def get_solo(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
