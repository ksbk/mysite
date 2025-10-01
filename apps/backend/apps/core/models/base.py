from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating 'created_at' and 'updated_at'
    fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Created at {self.created_at}, updated at {self.updated_at}"


class SingletonModel(models.Model):
    """
    Abstract base model that ensures only one instance exists.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure only one instance exists
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Get or create the singleton instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class VersionedSingletonModel(models.Model):
    """
    Abstract base model for versioned singleton configurations.
    """

    schema_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Schema version for backward compatibility",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure only one instance exists
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Get or create the singleton instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def get_current_schema_version(cls) -> str:
        """Get the current schema version for this model."""
        return getattr(cls, "_schema_version", "1.0")

    def needs_migration(self) -> bool:
        """Check if this instance needs schema migration."""
        current_version = self.get_current_schema_version()
        return self.schema_version != current_version

    def migrate_schema(self, save: bool = True) -> bool:
        """Migrate schema to current version."""
        if not self.needs_migration():
            return False

        old_version = self.schema_version
        new_version = self.get_current_schema_version()

        # Perform version-specific migrations
        migrated = self._perform_migration(old_version, new_version)

        if migrated:
            self.schema_version = new_version
            if save:
                self.save()

        return migrated

    def _perform_migration(self, from_version: str, to_version: str) -> bool:
        """
        Override this method in subclasses to perform actual migrations.
        Return True if migration was successful, False otherwise.
        """
        return True


class OrderedModel(models.Model):
    """
    Abstract base model that provides ordering functionality.
    """

    order = models.PositiveIntegerField(
        default=0, help_text="Order for display purposes"
    )

    class Meta:
        abstract = True
        ordering = ["order", "id"]
