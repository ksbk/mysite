"""
Management command to test and display configuration sources.
"""

from django.core.management.base import BaseCommand

from ...config.sources import multi_source_loader


class Command(BaseCommand):
    """Test and display configuration source information."""

    help = "Display configuration source information and test loading"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--test-key", type=str, help="Test loading a specific configuration key"
        )
        parser.add_argument(
            "--show-sources", action="store_true", help="Show all configured sources"
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        show_sources = options.get("show_sources", True)
        test_key = options.get("test_key")

        if show_sources:
            self._show_sources()

        if test_key:
            self._test_config_key(test_key)

    def _show_sources(self):
        """Display information about all configuration sources."""
        self.stdout.write(self.style.HTTP_INFO("Configuration Sources:"))

        source_info = multi_source_loader.get_source_info()

        for i, info in enumerate(source_info, 1):
            status = "✓" if info["available"] else "✗"
            status_style = self.style.SUCCESS if info["available"] else self.style.ERROR

            self.stdout.write(
                f"{i}. {status_style(status)} {info['source_type']} "
                f"(priority: {info['priority']})"
            )

            if not info["available"]:
                self.stdout.write(f"   {self.style.WARNING('Not available')}")

    def _test_config_key(self, config_key: str):
        """Test loading a specific configuration key."""
        self.stdout.write(
            f"\n{self.style.HTTP_INFO(f'Testing config key: {config_key}')}"
        )

        try:
            value = multi_source_loader.get_config_value(config_key)

            if value is not None:
                self.stdout.write(self.style.SUCCESS(f"✓ Found value: {repr(value)}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Key '{config_key}' not found in any source")
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error loading key: {e}"))
