"""Configuration audit and versioning models."""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

User = get_user_model()


class ConfigAuditManager(models.Manager):
    """Manager for ConfigAudit with convenience methods."""

    def log_change(
        self,
        config_object: models.Model,
        action: str,
        user: User | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        change_reason: str | None = None,
    ) -> "ConfigAudit":
        """Log a configuration change."""
        return self.create(
            content_type=ContentType.objects.get_for_model(config_object),
            object_id=config_object.pk,
            config_object=config_object,
            action=action,
            user=user,
            old_value=old_value,
            new_value=new_value,
            change_reason=change_reason,
            timestamp=timezone.now(),
        )

    def get_history(self, config_object: models.Model) -> models.QuerySet:
        """Get audit history for a configuration object."""
        return self.filter(
            content_type=ContentType.objects.get_for_model(config_object),
            object_id=config_object.pk,
        ).order_by("-timestamp")

    def get_changes_by_user(self, user: User) -> models.QuerySet:
        """Get all configuration changes by a user."""
        return self.filter(user=user).order_by("-timestamp")


class ConfigAudit(models.Model):
    """Audit log for configuration changes."""

    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        ROLLBACK = "rollback", "Rollback"
        VALIDATE = "validate", "Validate"

    # Generic foreign key to any configuration model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    config_object = GenericForeignKey("content_type", "object_id")

    # Audit details
    action = models.CharField(max_length=20, choices=Action.choices)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made the change",
    )
    timestamp = models.DateTimeField(default=timezone.now)
    change_reason = models.TextField(blank=True, help_text="Reason for the change")

    # Data snapshots
    old_value = models.JSONField(
        null=True, blank=True, help_text="Configuration state before the change"
    )
    new_value = models.JSONField(
        null=True, blank=True, help_text="Configuration state after the change"
    )

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(
        max_length=50, blank=True, help_text="Request ID for correlation with logs"
    )

    objects = ConfigAuditManager()

    class Meta:
        db_table = "core_config_audit"
        verbose_name = "Configuration Audit"
        verbose_name_plural = "Configuration Audits"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        user_info = f" by {self.user}" if self.user else ""
        return f"{self.action} {self.config_object}{user_info} at {self.timestamp}"

    def get_changes(self) -> dict:
        """Get a summary of what changed."""
        if not self.old_value or not self.new_value:
            return {}

        changes = {}
        old_dict = self.old_value if isinstance(self.old_value, dict) else {}
        new_dict = self.new_value if isinstance(self.new_value, dict) else {}

        # Find all keys that changed
        all_keys = set(old_dict.keys()) | set(new_dict.keys())

        for key in all_keys:
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)

            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val, "changed": True}

        return changes

    def can_rollback(self) -> bool:
        """Check if this change can be rolled back."""
        return (
            self.action in [self.Action.UPDATE, self.Action.CREATE]
            and self.old_value is not None
        )


class ConfigVersion(models.Model):
    """Configuration version tracking for rollback capabilities."""

    # Generic foreign key to any configuration model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    config_object = GenericForeignKey("content_type", "object_id")

    # Version information
    version_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Configuration snapshot
    config_data = models.JSONField(help_text="Complete configuration state")
    schema_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Schema version for compatibility checking",
    )

    # Metadata
    is_current = models.BooleanField(default=False)
    change_summary = models.TextField(blank=True)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing versions (e.g., 'stable', 'experimental')",
    )

    class Meta:
        db_table = "core_config_version"
        verbose_name = "Configuration Version"
        verbose_name_plural = "Configuration Versions"
        ordering = ["-version_number"]
        unique_together = ["content_type", "object_id", "version_number"]
        indexes = [
            models.Index(fields=["content_type", "object_id", "version_number"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_current"]),
        ]

    def __str__(self) -> str:
        current = " (current)" if self.is_current else ""
        return f"{self.config_object} v{self.version_number}{current}"

    def save(self, *args, **kwargs):
        """Ensure only one version is marked as current per object."""
        if self.is_current:
            # Mark other versions of the same object as not current
            ConfigVersion.objects.filter(
                content_type=self.content_type, object_id=self.object_id
            ).update(is_current=False)

        super().save(*args, **kwargs)

    @classmethod
    def create_version(
        cls,
        config_object: models.Model,
        config_data: dict,
        user: User | None = None,
        change_summary: str = "",
        tags: list | None = None,
    ) -> "ConfigVersion":
        """Create a new version for a configuration object."""
        # Get the next version number
        last_version = cls.objects.filter(
            content_type=ContentType.objects.get_for_model(config_object),
            object_id=config_object.pk,
        ).first()

        next_version = (last_version.version_number + 1) if last_version else 1

        return cls.objects.create(
            content_type=ContentType.objects.get_for_model(config_object),
            object_id=config_object.pk,
            config_object=config_object,
            version_number=next_version,
            config_data=config_data,
            created_by=user,
            change_summary=change_summary,
            tags=tags or [],
            is_current=True,
        )

    def rollback_to(self, user: User | None = None) -> bool:
        """Rollback the configuration to this version."""
        try:
            # Update the configuration object with this version's data
            config_object = self.config_object
            if not config_object:
                return False

            # Store current state for audit
            from .loader import ConfigLoader

            loader = ConfigLoader()
            current_data = loader._model_to_dict(config_object)

            # Apply the rollback data
            for field, value in self.config_data.items():
                if hasattr(config_object, field):
                    setattr(config_object, field, value)

            config_object.save()

            # Log the rollback
            ConfigAudit.objects.log_change(
                config_object=config_object,
                action=ConfigAudit.Action.ROLLBACK,
                user=user,
                old_value=current_data,
                new_value=self.config_data,
                change_reason=f"Rolled back to version {self.version_number}",
            )

            # Mark this version as current
            self.is_current = True
            self.save()

            # Clear cache
            cache_key = f"config:{config_object._meta.model_name}"
            loader._delete_cache(cache_key)

            return True

        except Exception:
            return False
