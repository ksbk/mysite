from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import connection, models
from django.test import TransactionTestCase

from apps.core.models.base import (
    OrderedModel,
    SingletonModel,
    TimeStampedModel,
    VersionedSingletonModel,
)

# === Test Model Definitions (Django models for testing, not test classes) ===


class TimeStampedTestModel(TimeStampedModel):
    """Test model for TimeStampedModel functionality."""

    name = models.CharField(max_length=32)

    class Meta:
        app_label = "core"
        db_table = "test_core_timestamped"


class SingletonTestModel(TimeStampedModel, SingletonModel):
    """Test model for SingletonModel functionality."""

    name = models.CharField(max_length=32, default="singleton")

    class Meta:
        app_label = "core"
        db_table = "test_core_singleton"


class VersionedTestModel(TimeStampedModel, VersionedSingletonModel):
    """Test model for VersionedSingletonModel functionality."""

    _SCHEMA_VERSION = "2.0"
    note = models.CharField(max_length=32, blank=True)

    class Meta:
        app_label = "core"
        db_table = "test_core_versioned"


class OrderedTestModel(OrderedModel):
    """Test model for OrderedModel functionality."""

    name = models.CharField(max_length=32)

    class Meta:
        app_label = "core"
        db_table = "test_core_ordered"
        ordering = ["order", "id"]


# --- Tests -------------------------------------------------------------------


class ModelTestCaseMixin:
    """Mixin to create tables for test models that have no migrations."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create tables for test models if they don't exist
        with connection.schema_editor() as schema_editor:
            try:
                schema_editor.create_model(TimeStampedTestModel)
            except Exception:
                pass  # Table already exists
            try:
                schema_editor.create_model(SingletonTestModel)
            except Exception:
                pass  # Table already exists
            try:
                schema_editor.create_model(VersionedTestModel)
            except Exception:
                pass  # Table already exists
            try:
                schema_editor.create_model(OrderedTestModel)
            except Exception:
                pass  # Table already exists


class TimeStampedModelTests(ModelTestCaseMixin, TransactionTestCase):
    def test_created_and_updated_flags(self):
        obj = TimeStampedTestModel.objects.create(name="alpha")
        self.assertIsNotNone(obj.pk)
        self.assertTrue(obj.is_recently_created)
        self.assertTrue(obj.is_recently_updated)
        # updated_at should be >= created_at
        self.assertGreaterEqual(obj.updated_at, obj.created_at)

        # On save, updated_at should advance or remain >= created_at
        obj.name = "beta"
        obj.save(update_fields=["name"])  # fast update
        obj.refresh_from_db()
        self.assertGreaterEqual(obj.updated_at, obj.created_at)


class SingletonModelTests(ModelTestCaseMixin, TransactionTestCase):
    def test_load_returns_single_instance_and_prevents_delete(self):
        a = SingletonTestModel.load()
        b = SingletonTestModel.load()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(SingletonTestModel.objects.count(), 1)

        with self.assertRaises(ValidationError):
            a.delete()
        self.assertEqual(SingletonTestModel.objects.count(), 1)

    def test_enforcer_remains_true_on_save(self):
        obj = SingletonTestModel.load()
        # Try to flip it; save() should force True
        obj._singleton_enforcer = False
        obj.save()
        obj.refresh_from_db()
        self.assertTrue(obj._singleton_enforcer)


class VersionedSingletonModelTests(ModelTestCaseMixin, TransactionTestCase):
    def test_migration_flow(self):
        # First load creates with base default ("1.0")
        obj = VersionedTestModel.load()
        self.assertEqual(obj.schema_version, "1.0")
        self.assertTrue(obj.needs_migration())

        migrated = obj.migrate_schema()
        self.assertTrue(migrated)
        obj.refresh_from_db()
        self.assertEqual(obj.schema_version, "2.0")
        self.assertFalse(obj.needs_migration())

        # Idempotent on second call
        self.assertFalse(obj.migrate_schema())


class OrderedModelTests(ModelTestCaseMixin, TransactionTestCase):
    def test_global_ordering(self):
        OrderedTestModel.objects.create(name="a", order=2)
        OrderedTestModel.objects.create(name="b", order=1)
        OrderedTestModel.objects.create(name="c", order=1)

        rows = list(OrderedTestModel.objects.all().values_list("order", "id"))
        # Should be ordered by (order asc, id asc)
        self.assertEqual(rows, sorted(rows))
