"""Django management command to validate site configuration."""

from django.core.management.base import BaseCommand

from apps.core.models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from apps.core.sitecfg.loader import ConfigLoader
from apps.core.sitecfg.normalize import PydanticAvailable, normalize_config_dict


class Command(BaseCommand):
    """Validate site configuration using Pydantic schemas."""

    help = "Validate site configuration using Pydantic schemas"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Validate specific configuration type only",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to fix validation errors by normalizing data",
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Show detailed validation results"
        )

    def handle(self, *args, **options):
        """Handle the command."""
        if not PydanticAvailable:
            self.stdout.write(
                self.style.WARNING(
                    "Pydantic is not available. Install it for full validation support."
                )
            )
            return

        config_type = options.get("config_type")
        fix_errors = options["fix"]
        verbose = options["verbose"]

        loader = ConfigLoader()

        try:
            # Get configuration data
            if config_type:
                config_data = {config_type: loader.get_config(config_type)}
                self.stdout.write(f"Validating {config_type} configuration...")
            else:
                config_data = loader.get_config()
                self.stdout.write("Validating all configuration...")

            # Validate configuration
            validation_results = self._validate_config(config_data, verbose)

            # Report results
            total_errors = sum(len(errors) for errors in validation_results.values())

            if total_errors == 0:
                self.stdout.write(self.style.SUCCESS("✓ All configuration is valid!"))
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Found {total_errors} validation errors")
                )

                for config_name, errors in validation_results.items():
                    if errors:
                        self.stdout.write(f"\n{config_name.upper()} Configuration:")
                        for error in errors:
                            self.stdout.write(f"  • {error}")

                if fix_errors:
                    self.stdout.write("\nAttempting to fix errors...")
                    self._fix_validation_errors(config_data)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Validation failed: {str(e)}"))
            if verbose:
                raise

    def _validate_config(self, config_data, verbose=False):
        """Validate configuration data and return error details."""
        validation_results = {}

        for config_name, data in config_data.items():
            validation_results[config_name] = []

            try:
                # Attempt normalization which includes validation
                normalize_config_dict({config_name: data})

                if verbose:
                    self.stdout.write(f"  ✓ {config_name} configuration is valid")

            except Exception as e:
                error_msg = str(e)
                validation_results[config_name].append(error_msg)

                if verbose:
                    self.stdout.write(f"  ✗ {config_name}: {error_msg}")

        return validation_results

    def _fix_validation_errors(self, config_data):
        """Attempt to fix validation errors by normalizing and saving data."""
        model_map = {
            "site": SiteConfig,
            "seo": SEOConfig,
            "theme": ThemeConfig,
            "content": ContentConfig,
        }

        fixed_count = 0

        for config_name, data in config_data.items():
            if config_name not in model_map:
                continue

            try:
                # Normalize the data
                normalized = normalize_config_dict({config_name: data})
                normalized_data = normalized[config_name]

                # Update the model instance
                model_class = model_map[config_name]
                instance = model_class.objects.first()

                if instance:
                    for field, value in normalized_data.items():
                        if hasattr(instance, field):
                            setattr(instance, field, value)

                    instance.save()
                    fixed_count += 1
                    self.stdout.write(f"  ✓ Fixed {config_name} configuration")

            except Exception as e:
                self.stdout.write(f"  ✗ Could not fix {config_name}: {str(e)}")

        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully fixed {fixed_count} configurations")
            )
        else:
            self.stdout.write(
                self.style.WARNING("No configurations could be automatically fixed")
            )
