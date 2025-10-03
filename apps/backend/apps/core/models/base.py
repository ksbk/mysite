from __future__ import annotations

from datetime import timedelta
from typing import NoReturn

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

__all__ = [
    "TimeStampedModel",
    "SingletonModel",
    "VersionedSingletonModel",
    "OrderedModel",
]


class TimeStampedModel(models.Model):
    """Abstract base with self-updating created/updated timestamps."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Created At"),
        help_text=_("The date and time when this object was created."),
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when this object was last updated."),
        db_index=False,
    )

    class Meta:
        abstract = True
        get_latest_by = "created_at"

    # Use default save/delete from Django; no custom signature needed

    def __str__(self) -> str:  # pragma: no cover
        name = self._meta.verbose_name
        return f"{name} #{self.pk}" if self.pk else f"Unsaved {name}"

    @property
    def is_recently_created(self) -> bool:
        """True if created within the last 24 hours."""
        now = timezone.now()
        return bool(self.created_at and (now - self.created_at) <= timedelta(hours=24))

    @property
    def is_recently_updated(self) -> bool:
        """True if updated within the last hour."""
        now = timezone.now()
        return bool(self.updated_at and (now - self.updated_at) <= timedelta(hours=1))


class SingletonModel(models.Model):
    """
    Abstract base that ensures exactly one row exists.
    Uses a unique boolean enforcer (works with any PK type) and an atomic loader.
    """

    _singleton_enforcer = models.BooleanField(
        default=True,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name=_("Singleton enforcer"),
        help_text=_("Ensures only one instance of this model can exist."),
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        """Ensure the singleton enforcer remains True on every save."""
        self._singleton_enforcer = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> NoReturn:
        raise ValidationError(
            _(
                "Singleton instances cannot be deleted. "
                "Edit the existing instance instead."
            )
        )

    @classmethod
    def load(cls, using: str | None = None):
        """
        Get (or atomically create) the singleton instance.
        Safe under concurrency and across multiple DB aliases.
        """
        db = using or cls._default_manager.db
        qs = cls._default_manager.using(db)

        obj = qs.first()
        if obj:
            # django-stubs may not infer Self here; the model class controls qs
            return obj  # type: ignore[return-value]

        with transaction.atomic(using=db):
            try:
                obj, _ = qs.get_or_create(_singleton_enforcer=True)
            except IntegrityError:
                obj = qs.get(_singleton_enforcer=True)
        return obj  # type: ignore[return-value]


class VersionedSingletonModel(SingletonModel):
    """
    Abstract base for versioned singleton configurations.

    - Persisted `schema_version` tracks instance format.
    - `_SCHEMA_VERSION` (class constant) represents current code schema.
    - `migrate_schema()` calls `_perform_migration()` that subclasses can override.
    """

    _SCHEMA_VERSION = "1.0"

    schema_version = models.CharField(
        max_length=20,
        default=_SCHEMA_VERSION,
        help_text=_("Schema version for backward compatibility."),
    )

    class Meta:
        abstract = True

    @classmethod
    def get_current_schema_version(cls) -> str:
        return getattr(cls, "_SCHEMA_VERSION", "1.0")

    def needs_migration(self) -> bool:
        return (self.schema_version or "") != self.get_current_schema_version()

    def migrate_schema(self, save: bool = True) -> bool:
        """
        Perform version-specific migrations and bump schema_version.
        Override `_perform_migration()` in subclasses for real changes.
        """
        if not self.needs_migration():
            return False

        old_version = self.schema_version or ""
        new_version = self.get_current_schema_version()

        migrated = self._perform_migration(old_version, new_version)
        if migrated:
            self.schema_version = new_version
            # Persist the new schema version
            super().save(update_fields=["schema_version"])
        return migrated

    def _perform_migration(self, from_version: str, to_version: str) -> bool:
        """Override in subclasses. Return True if migration succeeded."""
        return True


class OrderedModel(models.Model):
    """
    Abstract base providing a simple 'order' field.

    NOTE: This sets a *global* default ordering for inheritors.
    If you prefer per-model control, remove `Meta.ordering` here
    and set ordering on concrete models instead.
    """

    order = models.PositiveIntegerField(
        default=0,
        help_text=_("Order for display purposes."),
    )

    class Meta:
        abstract = True
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["order"])]
