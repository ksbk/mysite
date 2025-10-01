"""
Management command to export site configuration to JSON.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from ...models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class Command(BaseCommand):
    """Export site configuration to JSON format."""

    help = "Export site configuration to JSON file"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "output_file",
            nargs="?",
            type=str,
            help="Output JSON file path (default: config_YYYYMMDD_HHMMSS.json)",
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Format JSON with indentation for readability",
        )
        parser.add_argument(
            "--include-metadata",
            action="store_true",
            help="Include timestamps and Django model metadata",
        )
        parser.add_argument(
            "--stdout", action="store_true", help="Write to stdout instead of file"
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            config_data = self._collect_config_data(
                include_metadata=options["include_metadata"]
            )

            # Format JSON
            indent = 2 if options["pretty"] else None
            json_output = json.dumps(config_data, indent=indent, ensure_ascii=False)

            if options["stdout"]:
                self.stdout.write(json_output)
            else:
                output_file = self._get_output_file(options["output_file"])
                self._write_to_file(output_file, json_output)
                self.stdout.write(
                    self.style.SUCCESS(f"Configuration exported to {output_file}")
                )

        except Exception as e:
            raise CommandError(f"Failed to export configuration: {e}") from e

    def _collect_config_data(self, include_metadata: bool = False) -> dict[str, Any]:
        """Collect configuration data from all config models."""
        config_data = {}

        # Get site config
        try:
            site_config = SiteConfig.objects.get()
            config_data["site"] = {
                "site_name": site_config.site_name,
                "site_tagline": site_config.site_tagline,
                "domain": site_config.domain,
                "contact_email": site_config.contact_email,
                "feature_flags": site_config.feature_flags,
                "navigation": site_config.navigation,
            }
            if include_metadata:
                config_data["site"]["_metadata"] = {
                    "pk": site_config.pk,
                    "created_at": site_config.created_at.isoformat(),
                    "updated_at": site_config.updated_at.isoformat(),
                }
        except SiteConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No SiteConfig found - using empty data")
            )
            config_data["site"] = {}

        # Get SEO config
        try:
            seo_config = SEOConfig.objects.get()
            config_data["seo"] = {
                "meta_title": seo_config.meta_title,
                "meta_description": seo_config.meta_description,
                "meta_keywords": seo_config.meta_keywords,
                "noindex": seo_config.noindex,
                "canonical_url": seo_config.canonical_url,
                "og_image": seo_config.og_image,
                "google_site_verification": seo_config.google_site_verification,
                "google_analytics_id": seo_config.google_analytics_id,
                "structured_data": seo_config.structured_data,
            }
            if include_metadata:
                config_data["seo"]["_metadata"] = {
                    "pk": seo_config.pk,
                    "created_at": seo_config.created_at.isoformat(),
                    "updated_at": seo_config.updated_at.isoformat(),
                }
        except SEOConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No SEOConfig found - using empty data")
            )
            config_data["seo"] = {}

        # Get theme config
        try:
            theme_config = ThemeConfig.objects.get()
            config_data["theme"] = {
                "primary_color": theme_config.primary_color,
                "secondary_color": theme_config.secondary_color,
                "favicon_url": theme_config.favicon_url,
                "logo_url": theme_config.logo_url,
                "custom_css": theme_config.custom_css,
                "dark_mode_enabled": theme_config.dark_mode_enabled,
            }
            if include_metadata:
                config_data["theme"]["_metadata"] = {
                    "pk": theme_config.pk,
                    "created_at": theme_config.created_at.isoformat(),
                    "updated_at": theme_config.updated_at.isoformat(),
                }
        except ThemeConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No ThemeConfig found - using empty data")
            )
            config_data["theme"] = {}

        # Get content config
        try:
            content_config = ContentConfig.objects.get()
            config_data["content"] = {
                "maintenance_mode": content_config.maintenance_mode,
                "maintenance_message": content_config.maintenance_message,
                "comments_enabled": content_config.comments_enabled,
                "registration_enabled": content_config.registration_enabled,
                "max_upload_size_mb": content_config.max_upload_size_mb,
                "allowed_file_extensions": content_config.allowed_file_extensions,
            }
            if include_metadata:
                config_data["content"]["_metadata"] = {
                    "pk": content_config.pk,
                    "created_at": content_config.created_at.isoformat(),
                    "updated_at": content_config.updated_at.isoformat(),
                }
        except ContentConfig.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("No ContentConfig found - using empty data")
            )
            config_data["content"] = {}

        if include_metadata:
            config_data["_export"] = {
                "timestamp": datetime.now().isoformat(),
                "django_version": "5.2+",
                "format_version": "1.0",
            }

        return config_data

    def _get_output_file(self, provided_path: str | None) -> str:
        """Get the output file path."""
        if provided_path:
            return provided_path

        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"config_{timestamp}.json"

    def _write_to_file(self, file_path: str, content: str) -> None:
        """Write content to file."""
        try:
            # Ensure parent directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise CommandError(f"Failed to write to file {file_path}: {e}") from e
