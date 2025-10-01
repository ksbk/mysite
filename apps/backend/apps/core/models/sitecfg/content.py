"""Content configuration model."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..base import SingletonModel, TimeStampedModel


class ContentConfig(TimeStampedModel, SingletonModel):
    """
    Content and functionality configuration settings.
    """

    maintenance_mode = models.BooleanField(
        default=False,
        help_text=_("Enable maintenance mode"),
        verbose_name=_("Maintenance Mode"),
    )
    maintenance_message = models.TextField(
        blank=True,
        default="We're currently performing maintenance. Please check back soon.",
        help_text=_("Message to display during maintenance"),
        verbose_name=_("Maintenance Message"),
    )
    comments_enabled = models.BooleanField(
        default=True,
        help_text=_("Enable comments site-wide"),
        verbose_name=_("Comments Enabled"),
    )
    registration_enabled = models.BooleanField(
        default=True,
        help_text=_("Allow new user registrations"),
        verbose_name=_("Registration Enabled"),
    )
    max_upload_size_mb = models.PositiveIntegerField(
        default=10,
        help_text=_("Maximum file upload size in megabytes"),
        verbose_name=_("Max Upload Size (MB)"),
    )
    allowed_file_extensions = models.JSONField(
        default=list,
        help_text=_("List of allowed file extensions for uploads"),
        verbose_name=_("Allowed File Extensions"),
    )

    class Meta:
        verbose_name = _("Content Configuration")
        verbose_name_plural = _("Content Configuration")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return "Content Configuration"

    def clean(self):
        """Validate configuration values."""
        if self.max_upload_size_mb <= 0:
            raise ValidationError({
                "max_upload_size_mb": _("Upload size must be greater than 0")
            })

        if self.max_upload_size_mb > 100:  # Reasonable limit
            raise ValidationError({
                "max_upload_size_mb": _("Upload size cannot exceed 100 MB")
            })
