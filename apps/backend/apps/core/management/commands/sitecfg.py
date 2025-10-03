"""Django management command for site configuration operations."""

import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from apps.core.sitecfg.audit_models import ConfigAudit, ConfigVersion
from apps.core.sitecfg.loader import ConfigLoader


class Command(BaseCommand):
    """Management command for site configuration operations."""

    help = "Manage site configuration: backup, restore, validate, cache, audit, and version operations"

    def add_arguments(self, parser):
        """Add command arguments."""
        subparsers = parser.add_subparsers(
            dest="operation", help="Configuration operation to perform"
        )

        # Backup command
        backup_parser = subparsers.add_parser(
            "backup", help="Backup configuration to JSON file"
        )
        backup_parser.add_argument(
            "--output",
            type=str,
            default=f'config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            help="Output file path (default: timestamped filename)",
        )
        backup_parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Backup specific configuration type only",
        )

        # Restore command
        restore_parser = subparsers.add_parser(
            "restore", help="Restore configuration from JSON file"
        )
        restore_parser.add_argument("input_file", type=str, help="Input JSON file path")
        restore_parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Restore specific configuration type only",
        )
        restore_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be restored without making changes",
        )

        # Validate command
        validate_parser = subparsers.add_parser(
            "validate", help="Validate current configuration"
        )
        validate_parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Validate specific configuration type only",
        )
        validate_parser.add_argument(
            "--fix", action="store_true", help="Attempt to fix validation issues"
        )

        # Cache command
        cache_parser = subparsers.add_parser("cache", help="Manage configuration cache")
        cache_parser.add_argument(
            "cache_action",
            choices=["clear", "warm", "status"],
            help="Cache action to perform",
        )
        cache_parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Target specific configuration type",
        )

        # Audit command
        audit_parser = subparsers.add_parser(
            "audit", help="View configuration audit history"
        )
        audit_parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Show audit history for specific type",
        )
        audit_parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Number of audit records to show (default: 20)",
        )

        # Version command
        version_parser = subparsers.add_parser(
            "version", help="Manage configuration versions"
        )
        version_parser.add_argument(
            "version_action",
            choices=["list", "create", "rollback"],
            help="Version action to perform",
        )
        version_parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Target specific configuration type",
        )
        version_parser.add_argument(
            "--version-number", type=int, help="Version number for rollback"
        )
        version_parser.add_argument(
            "--summary", type=str, help="Version summary/description"
        )

    def handle(self, *args, **options):
        """Handle the command."""
        operation = options.get("operation")

        if not operation:
            self.print_help("manage.py", "config")
            return

        try:
            if operation == "backup":
                self._handle_backup(options)
            elif operation == "restore":
                self._handle_restore(options)
            elif operation == "validate":
                self._handle_validate(options)
            elif operation == "cache":
                self._handle_cache(options)
            elif operation == "audit":
                self._handle_audit(options)
            elif operation == "version":
                self._handle_version(options)
            else:
                raise CommandError(f"Unknown operation: {operation}")

        except Exception as e:
            raise CommandError(f"Operation failed: {str(e)}") from e

    def _handle_backup(self, options):
        """Handle backup operation."""
        loader = ConfigLoader()
        config_type = options.get("config_type")
        output_file = options["output"]

        self.stdout.write("Starting configuration backup...")

        if config_type:
            config_data = {config_type: loader.get_config(config_type)}
        else:
            config_data = loader.get_config()

        # Add metadata
        backup_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "config_types": list(config_data.keys()),
                "version": "1.0",
            },
            "configuration": config_data,
        }

        # Write to file
        with open(output_file, "w") as f:
            json.dump(backup_data, f, indent=2, default=str)

        self.stdout.write(
            self.style.SUCCESS(f"Configuration backed up to: {output_file}")
        )

    def _handle_restore(self, options):
        """Handle restore operation."""
        input_file = options["input_file"]
        config_type = options.get("config_type")
        dry_run = options.get("dry_run", False)

        if not os.path.exists(input_file):
            raise CommandError(f"Input file not found: {input_file}")

        # Load backup data
        with open(input_file) as f:
            backup_data = json.load(f)

        config_data = backup_data.get("configuration", {})

        if config_type:
            if config_type not in config_data:
                raise CommandError(
                    f"Configuration type '{config_type}' not found in backup"
                )
            config_data = {config_type: config_data[config_type]}

        model_map = {
            "site": SiteConfig,
            "seo": SEOConfig,
            "theme": ThemeConfig,
            "content": ContentConfig,
        }

        if dry_run:
            self.stdout.write("DRY RUN - Would restore:")
            for conf_type, conf_data in config_data.items():
                self.stdout.write(f"  - {conf_type}: {len(conf_data)} fields")
            return

        self.stdout.write("Starting configuration restore...")

        with transaction.atomic():
            for conf_type, conf_data in config_data.items():
                if conf_type not in model_map:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping unknown config type: {conf_type}")
                    )
                    continue

                model_class = model_map[conf_type]
                instance, created = model_class.objects.get_or_create()

                # Update fields
                for field, value in conf_data.items():
                    if hasattr(instance, field):
                        setattr(instance, field, value)

                instance.save()

                action = "created" if created else "updated"
                self.stdout.write(f"  - {conf_type} configuration {action}")

        # Clear cache
        loader = ConfigLoader()
        loader.invalidate_cache()

        self.stdout.write(self.style.SUCCESS("Configuration restored successfully"))

    def _handle_validate(self, options):
        """Handle validate operation."""
        config_type = options.get("config_type")

        self.stdout.write("Validating configuration...")

        # Import validation schemas
        try:
            from apps.core.sitecfg.schemas import (
                ContentConfigSchema,
                SEOConfigSchema,
                SiteConfigSchema,
                ThemeConfigSchema,
            )

            schema_map = {
                "site": SiteConfigSchema,
                "seo": SEOConfigSchema,
                "theme": ThemeConfigSchema,
                "content": ContentConfigSchema,
            }
        except ImportError:
            self.stdout.write(
                self.style.WARNING(
                    "Validation schemas not available, skipping validation"
                )
            )
            return

        loader = ConfigLoader()
        types_to_validate = [config_type] if config_type else list(schema_map.keys())

        validation_results = {}

        for conf_type in types_to_validate:
            config_data = loader.get_config(conf_type)
            schema_class = schema_map[conf_type]

            try:
                # Validate with Pydantic
                schema_class(**config_data)
                validation_results[conf_type] = {"valid": True, "errors": []}
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {conf_type} configuration is valid")
                )
            except Exception as e:
                validation_results[conf_type] = {"valid": False, "errors": [str(e)]}
                self.stdout.write(
                    self.style.ERROR(f"✗ {conf_type} configuration is invalid:")
                )
                self.stdout.write(f"  Error: {str(e)}")

        # Summary
        valid_count = sum(1 for r in validation_results.values() if r["valid"])
        total_count = len(validation_results)

        if valid_count == total_count:
            self.stdout.write(
                self.style.SUCCESS(f"All {total_count} configuration(s) are valid")
            )
        else:
            invalid_count = total_count - valid_count
            self.stdout.write(
                self.style.WARNING(
                    f"{invalid_count} of {total_count} configuration(s) "
                    f"have validation issues"
                )
            )

    def _handle_cache(self, options):
        """Handle cache operations."""
        cache_action = options["cache_action"]
        config_type = options.get("config_type")

        loader = ConfigLoader()

        if cache_action == "clear":
            success = loader.invalidate_cache(config_type)
            if success:
                target = config_type or "all"
                self.stdout.write(
                    self.style.SUCCESS(f"Cache cleared for {target} configuration(s)")
                )
            else:
                self.stdout.write(self.style.ERROR("Failed to clear cache"))

        elif cache_action == "warm":
            success = loader.warm_cache(config_type)
            if success:
                target = config_type or "all"
                self.stdout.write(
                    self.style.SUCCESS(f"Cache warmed for {target} configuration(s)")
                )
            else:
                self.stdout.write(self.style.ERROR("Failed to warm cache"))

        elif cache_action == "status":
            # Check cache status
            from django.core.cache import cache

            types_to_check = (
                [config_type] if config_type else ["site", "seo", "theme", "content"]
            )

            self.stdout.write("Cache Status:")
            for conf_type in types_to_check:
                cache_key = f"config:{conf_type}"
                cached_data = cache.get(cache_key)
                status = "HIT" if cached_data else "MISS"
                self.stdout.write(f"  {conf_type}: {status}")

    def _handle_audit(self, options):
        """Handle audit history display."""
        config_type = options.get("config_type")
        limit = options.get("limit", 20)

        if config_type:
            # Get specific config model
            model_map = {
                "site": SiteConfig,
                "seo": SEOConfig,
                "theme": ThemeConfig,
                "content": ContentConfig,
            }

            if config_type not in model_map:
                raise CommandError(f"Unknown config type: {config_type}")

            model_class = model_map[config_type]
            instance = model_class.objects.first()

            if not instance:
                self.stdout.write(
                    self.style.WARNING(f"No {config_type} configuration found")
                )
                return

            audit_records = ConfigAudit.objects.get_history(instance)[:limit]
            self.stdout.write(f"Audit History for {config_type} configuration:")
        else:
            audit_records = ConfigAudit.objects.all()[:limit]
            self.stdout.write("Recent Configuration Changes:")

        if not audit_records:
            self.stdout.write("No audit records found")
            return

        for record in audit_records:
            user_info = f" by {record.user}" if record.user else ""
            self.stdout.write(
                f"  {record.timestamp.strftime("%Y-%m-%d %H:%M:%S")} - "
                f"{record.action.upper()}{user_info}"
            )
            if record.change_reason:
                self.stdout.write(f"    Reason: {record.change_reason}")

    def _handle_version(self, options):
        """Handle version operations."""
        version_action = options["version_action"]
        config_type = options.get("config_type")

        model_map = {
            "site": SiteConfig,
            "seo": SEOConfig,
            "theme": ThemeConfig,
            "content": ContentConfig,
        }

        if version_action == "list":
            if config_type:
                if config_type not in model_map:
                    raise CommandError(f"Unknown config type: {config_type}")

                model_class = model_map[config_type]
                instance = model_class.objects.first()

                if not instance:
                    self.stdout.write(
                        self.style.WARNING(f"No {config_type} configuration found")
                    )
                    return

                versions = ConfigVersion.objects.filter(
                    content_type__model=config_type.replace("_", "")
                )
                self.stdout.write(f"Versions for {config_type} configuration:")
            else:
                versions = ConfigVersion.objects.all()
                self.stdout.write("All Configuration Versions:")

            if not versions:
                self.stdout.write("No versions found")
                return

            for version in versions:
                current = " (current)" if version.is_current else ""
                created_by = f" by {version.created_by}" if version.created_by else ""
                self.stdout.write(
                    f"  v{version.version_number}{current} - "
                    f"{version.created_at.strftime("%Y-%m-%d %H:%M:%S")}"
                    f"{created_by}"
                )
                if version.change_summary:
                    self.stdout.write(f"    {version.change_summary}")

        elif version_action == "create":
            if not config_type:
                raise CommandError("--config-type is required for version creation")

            if config_type not in model_map:
                raise CommandError(f"Unknown config type: {config_type}")

            model_class = model_map[config_type]
            instance = model_class.objects.first()

            if not instance:
                raise CommandError(f"No {config_type} configuration found")

            loader = ConfigLoader()
            config_data = loader.get_config(config_type)

            version = ConfigVersion.create_version(
                config_object=instance,
                config_data=config_data,
                change_summary=options.get(
                    "summary", "Manual version creation via CLI"
                ),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created version {version.version_number} for "
                    f"{config_type} configuration"
                )
            )

        elif version_action == "rollback":
            if not config_type:
                raise CommandError("--config-type is required for rollback")

            version_number = options.get("version_number")
            if not version_number:
                raise CommandError("--version-number is required for rollback")

            if config_type not in model_map:
                raise CommandError(f"Unknown config type: {config_type}")

            model_class = model_map[config_type]
            instance = model_class.objects.first()

            if not instance:
                raise CommandError(f"No {config_type} configuration found")

            try:
                version = ConfigVersion.objects.get(
                    content_type__model=config_type.replace("_", ""),
                    object_id=instance.pk,
                    version_number=version_number,
                )
            except ConfigVersion.DoesNotExist as e:
                raise CommandError(
                    f"Version {version_number} not found for {config_type}"
                ) from e

            success = version.rollback_to()

            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully rolled back {config_type} configuration "
                        f"to version {version_number}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to rollback {config_type} configuration")
                )
