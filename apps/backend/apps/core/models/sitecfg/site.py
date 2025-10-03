"""Site configuration model."""

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import SingletonModel, TimeStampedModel

DOMAIN_VALIDATION_REGEX = RegexValidator(
    regex=r"^(?=.{1,255}$)([a-zA-Z0-9-]{1,63}\.)+[A-Za-z]{2,63}$",
    message=_("Enter a valid domain like 'example.com' (no scheme or path)."),
)


class SiteConfig(TimeStampedModel, SingletonModel):
    """
    Singleton model to store site-wide configuration settings.
    Use SiteConfig.load() to ensure only one instance exists.
    """

    site_name = models.CharField(
        max_length=120,
        default="My Site",
        help_text=_("Display name used throughout the site"),
        verbose_name=_("Site Name"),
    )
    site_tagline = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Brief tagline or description shown in footers and meta tags"),
        verbose_name=_("Site Tagline"),
    )
    domain = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Primary domain for canonical URLs"),
        verbose_name=_("Domain"),
    )
    contact_email = models.EmailField(
        blank=True,
        help_text=_("Primary contact email address"),
        verbose_name=_("Contact Email"),
    )
    feature_flags = models.JSONField(
        default=dict,
        help_text=_("Feature flags for various site functionality"),
        verbose_name=_("Feature Flags"),
    )
    navigation = models.JSONField(
        default=list,
        help_text=_("Main navigation structure"),
        verbose_name=_("Navigation"),
    )

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.site_name
