"""Theme configuration model."""

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import SingletonModel, TimeStampedModel


class ThemeConfig(TimeStampedModel, SingletonModel):
    """
    Theme and visual configuration settings.
    """

    primary_color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text=_("Primary brand color (hex format)"),
        verbose_name=_("Primary Color"),
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#6c757d",
        help_text=_("Secondary brand color (hex format)"),
        verbose_name=_("Secondary Color"),
    )
    favicon_url = models.URLField(
        blank=True,
        help_text=_("URL to favicon file"),
        verbose_name=_("Favicon URL"),
    )
    logo_url = models.URLField(
        blank=True,
        help_text=_("URL to site logo"),
        verbose_name=_("Logo URL"),
    )
    custom_css = models.TextField(
        blank=True,
        help_text=_("Custom CSS to inject into pages"),
        verbose_name=_("Custom CSS"),
    )
    dark_mode_enabled = models.BooleanField(
        default=True,
        help_text=_("Enable dark mode support"),
        verbose_name=_("Dark Mode Enabled"),
    )

    class Meta:
        verbose_name = _("Theme Configuration")
        verbose_name_plural = _("Theme Configuration")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return "Theme Configuration"

    def clean(self):
        """Validate color formats."""
        hex_pattern = r"^#[0-9A-Fa-f]{6}$"

        if self.primary_color and not re.match(hex_pattern, self.primary_color):
            raise ValidationError({
                "primary_color": _("Color must be in hex format (#000000)")
            })

        if self.secondary_color and not re.match(hex_pattern, self.secondary_color):
            raise ValidationError({
                "secondary_color": _("Color must be in hex format (#000000)")
            })
