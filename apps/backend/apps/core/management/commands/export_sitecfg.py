"""Django management command to export site configuration."""

import json
from datetime import datetime

from django.core.management.base import BaseCommand

from apps.core.sitecfg.loader import ConfigLoader


class Command(BaseCommand):
    """Export site configuration to JSON file."""

    help = "Export site configuration to JSON file"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--output",
            type=str,
            default=f"config_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json",
            help="Output file path (default: timestamped filename)",
        )
        parser.add_argument(
            "--config-type",
            type=str,
            choices=["site", "seo", "theme", "content"],
            help="Export specific configuration type only",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Format JSON with indentation for readability",
        )

    def handle(self, *args, **options):
        """Handle the command."""
        loader = ConfigLoader()
        output_file = options["output"]
        config_type = options.get("config_type")
        pretty = options["pretty"]

        try:
            # Get configuration data
            if config_type:
                config_data = {config_type: loader.get_config(config_type)}
                self.stdout.write(f"Exporting {config_type} configuration...")
            else:
                config_data = loader.get_config()
                self.stdout.write("Exporting all configuration...")

            # Add metadata
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "config_type": config_type or "all",
                "data": config_data,
            }

            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
                else:
                    json.dump(export_data, f, default=str, ensure_ascii=False)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully exported configuration to {output_file}"
                )
            )

            # Show summary
            if config_type:
                self.stdout.write(f"Configuration type: {config_type}")
            else:
                types = list(config_data.keys())
                self.stdout.write(f"Configuration types: {", ".join(types)}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Export failed: {str(e)}"))
            raise
