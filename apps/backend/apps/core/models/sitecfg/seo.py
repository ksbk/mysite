"""SEO configuration model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import SingletonModel, TimeStampedModel


class SEOConfig(TimeStampedModel, SingletonModel):
    """
    SEO-related configuration settings.
    """

    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text=_("Default meta title (max 60 characters)"),
        verbose_name=_("Meta Title"),
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text=_("Default meta description (max 160 characters)"),
        verbose_name=_("Meta Description"),
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Comma-separated meta keywords"),
        verbose_name=_("Meta Keywords"),
    )
    noindex = models.BooleanField(
        default=False,
        help_text=_("Prevent search engines from indexing the site"),
        verbose_name=_("No Index"),
    )
    canonical_url = models.URLField(
        blank=True,
        help_text=_("Canonical URL for the site"),
        verbose_name=_("Canonical URL"),
    )
    og_image = models.URLField(
        blank=True,
        help_text=_("Default Open Graph image URL"),
        verbose_name=_("OG Image"),
    )
    google_site_verification = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Google Search Console verification code"),
        verbose_name=_("Google Site Verification"),
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Google Analytics tracking ID"),
        verbose_name=_("Google Analytics ID"),
    )
    structured_data = models.JSONField(
        default=dict,
        help_text=_("Default structured data (JSON-LD)"),
        verbose_name=_("Structured Data"),
    )

    class Meta:
        verbose_name = _("SEO Configuration")
        verbose_name_plural = _("SEO Configuration")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return "SEO Configuration"
