"""
Management command to validate site configuration.
"""

from typing import Any

from django.core.management.base import BaseCommand
from pydantic import ValidationError

from ...config.schemas import (
    ContentConfigSchema,
    SEOConfigSchema,
    SiteConfigSchema,
    ThemeConfigSchema,
)
from ...models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class Command(BaseCommand):
    """Validate site configuration using Pydantic schemas."""

    help = "Validate site configuration data and schemas"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--config-type",
            choices=["site", "seo", "theme", "content", "all"],
            default="all",
            help="Configuration type to validate (default: all)",
        )
        parser.add_argument(
            "--fix-errors",
            action="store_true",
            help="Attempt to fix validation errors automatically",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed validation information",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        config_type = options["config_type"]
        fix_errors = options["fix_errors"]
        verbose = options["verbose"]

        if config_type == "all":
            config_types = ["site", "seo", "theme", "content"]
        else:
            config_types = [config_type]

        total_errors = 0
        total_fixed = 0

        for cfg_type in config_types:
            self.stdout.write(
                f"\n{self.style.HTTP_INFO(f"Validating {cfg_type} configuration...")}"
            )

            try:
                errors, fixed = self._validate_config_type(
                    cfg_type, fix_errors, verbose
                )
                total_errors += errors
                total_fixed += fixed

                if errors == 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {cfg_type.title()} configuration is valid"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ {cfg_type.title()} configuration has {errors} errors"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to validate {cfg_type}: {e}")
                )
                total_errors += 1

        # Summary
        self.stdout.write(f"\n{self.style.HTTP_INFO("Validation Summary:")}")
        if total_errors == 0:
            self.stdout.write(self.style.SUCCESS("✓ All configurations are valid"))
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Found {total_errors} validation errors")
            )
            if total_fixed > 0:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Fixed {total_fixed} errors automatically")
                )

        if total_errors > 0:
            exit(1)

    def _validate_config_type(
        self, config_type: str, fix_errors: bool, verbose: bool
    ) -> tuple[int, int]:
        """Validate a specific configuration type."""
        errors = 0
        fixed = 0

        if config_type == "site":
            errors, fixed = self._validate_site_config(fix_errors, verbose)
        elif config_type == "seo":
            errors, fixed = self._validate_seo_config(fix_errors, verbose)
        elif config_type == "theme":
            errors, fixed = self._validate_theme_config(fix_errors, verbose)
        elif config_type == "content":
            errors, fixed = self._validate_content_config(fix_errors, verbose)

        return errors, fixed

    def _validate_site_config(self, fix_errors: bool, verbose: bool) -> tuple[int, int]:
        """Validate SiteConfig."""
        try:
            config = SiteConfig.objects.get()
        except SiteConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No SiteConfig found - creating default")
            )
            if fix_errors:
                config = SiteConfig.objects.create(site_name="Default Site")
                return 0, 1
            return 1, 0

        return self._validate_against_schema(
            config, SiteConfigSchema, "SiteConfig", fix_errors, verbose
        )

    def _validate_seo_config(self, fix_errors: bool, verbose: bool) -> tuple[int, int]:
        """Validate SEOConfig."""
        try:
            config = SEOConfig.objects.get()
        except SEOConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No SEOConfig found - creating default")
            )
            if fix_errors:
                config = SEOConfig.objects.create()
                return 0, 1
            return 1, 0

        return self._validate_against_schema(
            config, SEOConfigSchema, "SEOConfig", fix_errors, verbose
        )

    def _validate_theme_config(
        self, fix_errors: bool, verbose: bool
    ) -> tuple[int, int]:
        """Validate ThemeConfig."""
        try:
            config = ThemeConfig.objects.get()
        except ThemeConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No ThemeConfig found - creating default")
            )
            if fix_errors:
                config = ThemeConfig.objects.create()
                return 0, 1
            return 1, 0

        return self._validate_against_schema(
            config, ThemeConfigSchema, "ThemeConfig", fix_errors, verbose
        )

    def _validate_content_config(
        self, fix_errors: bool, verbose: bool
    ) -> tuple[int, int]:
        """Validate ContentConfig."""
        try:
            config = ContentConfig.objects.get()
        except ContentConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No ContentConfig found - creating default")
            )
            if fix_errors:
                config = ContentConfig.objects.create()
                return 0, 1
            return 1, 0

        return self._validate_against_schema(
            config, ContentConfigSchema, "ContentConfig", fix_errors, verbose
        )

    def _validate_against_schema(
        self,
        config: Any,
        schema_class: type,
        config_name: str,
        fix_errors: bool,
        verbose: bool,
    ) -> tuple[int, int]:
        """Validate a config instance against its Pydantic schema."""
        try:
            # Convert Django model to dict for validation
            config_data = {}
            for field in config._meta.fields:
                field_name = field.name
                if field_name not in ["id", "pk", "created_at", "updated_at"]:
                    config_data[field_name] = getattr(config, field_name)

            # Validate using Pydantic schema
            schema_class(**config_data)

            if verbose:
                self.stdout.write(f"  ✓ {config_name} validation successful")

            return 0, 0

        except ValidationError as e:
            errors = len(e.errors())

            if verbose:
                self.stdout.write(f"  ✗ {config_name} validation failed:")
                for error in e.errors():
                    field = ".".join(str(loc) for loc in error["loc"])
                    msg = error["msg"]
                    self.stdout.write(f"    - {field}: {msg}")

            if fix_errors:
                fixed = self._attempt_fixes(config, e.errors(), config_name, verbose)
                return max(0, errors - fixed), fixed

            return errors, 0

    def _attempt_fixes(
        self, config: Any, errors: list[dict[str, Any]], config_name: str, verbose: bool
    ) -> int:
        """Attempt to fix validation errors automatically."""
        fixed = 0

        for error in errors:
            field_path = error["loc"]
            error_type = error["type"]

            if len(field_path) == 1:
                field_name = field_path[0]

                if error_type == "missing":
                    # Set default value for missing fields
                    if hasattr(config._meta.get_field(field_name), "default"):
                        default_value = config._meta.get_field(field_name).default
                        if callable(default_value):
                            default_value = default_value()
                        setattr(config, field_name, default_value)
                        config.save()
                        fixed += 1
                        if verbose:
                            self.stdout.write(
                                f"    ✓ Fixed missing field '{field_name}' with default value"
                            )

                elif error_type in ["type_error.list", "type_error.dict"]:
                    # Fix type errors for JSON fields
                    if error_type == "type_error.list":
                        setattr(config, field_name, [])
                    elif error_type == "type_error.dict":
                        setattr(config, field_name, {})

                    config.save()
                    fixed += 1
                    if verbose:
                        self.stdout.write(
                            f"    ✓ Fixed type error for field '{field_name}'"
                        )

        return fixed
