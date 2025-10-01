"""
Management command to initialize site configuration with defaults.
"""

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class Command(BaseCommand):
    """Initialize site configuration with sensible defaults."""

    help = "Initialize site configuration with default values"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--site-name",
            type=str,
            default="My Site",
            help="Site name (default: My Site)",
        )
        parser.add_argument("--domain", type=str, help="Primary domain for the site")
        parser.add_argument("--contact-email", type=str, help="Contact email address")
        parser.add_argument(
            "--from-file", type=str, help="Load configuration from JSON file"
        )
        parser.add_argument(
            "--force", action="store_true", help="Overwrite existing configuration"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without making changes",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            if options["from_file"]:
                self._init_from_file(options)
            else:
                self._init_with_defaults(options)
        except Exception as e:
            raise CommandError(f"Failed to initialize configuration: {e}") from e

    def _init_from_file(self, options: dict[str, Any]) -> None:
        """Initialize configuration from JSON file."""
        file_path = options["from_file"]

        try:
            with open(file_path) as f:
                config_data = json.load(f)
        except FileNotFoundError as e:
            raise CommandError(f"Configuration file not found: {file_path}") from e
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON in configuration file: {e}") from e

        if options["dry_run"]:
            self.stdout.write("DRY RUN - Would load configuration from file:")
            self.stdout.write(json.dumps(config_data, indent=2))
            return

        self._create_configs_from_data(config_data, options["force"])
        self.stdout.write(self.style.SUCCESS(f"Configuration loaded from {file_path}"))

    def _init_with_defaults(self, options: dict[str, Any]) -> None:
        """Initialize configuration with default values."""
        site_name = options["site_name"]
        domain = options.get("domain", "")
        contact_email = options.get("contact_email", "")

        config_data = {
            "site": {
                "site_name": site_name,
                "domain": domain,
                "contact_email": contact_email,
                "feature_flags": {
                    "dark_mode": True,
                    "pwa": True,
                    "analytics": False,
                },
                "navigation": [
                    {"label": "Home", "url": "/", "active": True},
                    {"label": "About", "url": "/about/", "active": False},
                    {"label": "Contact", "url": "/contact/", "active": False},
                ],
            },
            "seo": {
                "meta_title": f"{site_name} - Welcome",
                "meta_description": f"Welcome to {site_name}",
                "canonical_url": f"https://{domain}" if domain else "",
                "noindex": False,
            },
            "theme": {
                "primary_color": "#007bff",
                "secondary_color": "#6c757d",
                "dark_mode_enabled": True,
            },
            "content": {
                "maintenance_mode": False,
                "comments_enabled": True,
                "registration_enabled": True,
                "max_upload_size_mb": 10,
                "allowed_file_extensions": [".jpg", ".jpeg", ".png", ".gif", ".pdf"],
            },
        }

        if options["dry_run"]:
            self.stdout.write("DRY RUN - Would create configuration:")
            self.stdout.write(json.dumps(config_data, indent=2))
            return

        self._create_configs_from_data(config_data, options["force"])
        self.stdout.write(
            self.style.SUCCESS(f"Configuration initialized for '{site_name}'")
        )

    def _create_configs_from_data(self, data: dict[str, Any], force: bool) -> None:
        """Create configuration objects from data."""
        # Check if configs already exist
        configs_exist = any([
            SiteConfig.objects.exists(),
            SEOConfig.objects.exists(),
            ThemeConfig.objects.exists(),
            ContentConfig.objects.exists(),
        ])

        if configs_exist and not force:
            raise CommandError(
                "Configuration already exists. Use --force to overwrite."
            )

        with transaction.atomic():
            if force:
                # Delete existing configs if force is True
                SiteConfig.objects.all().delete()
                SEOConfig.objects.all().delete()
                ThemeConfig.objects.all().delete()
                ContentConfig.objects.all().delete()

            # Create site config
            site_data = data.get("site", {})
            site_config = SiteConfig.objects.create(
                site_name=site_data.get("site_name", "My Site"),
                site_tagline=site_data.get("site_tagline", ""),
                domain=site_data.get("domain", ""),
                contact_email=site_data.get("contact_email", ""),
                feature_flags=site_data.get("feature_flags", {}),
                navigation=site_data.get("navigation", []),
            )

            # Create SEO config
            seo_data = data.get("seo", {})
            seo_config = SEOConfig.objects.create(
                meta_title=seo_data.get("meta_title", ""),
                meta_description=seo_data.get("meta_description", ""),
                meta_keywords=seo_data.get("meta_keywords", ""),
                noindex=seo_data.get("noindex", False),
                canonical_url=seo_data.get("canonical_url", ""),
                og_image=seo_data.get("og_image", ""),
                google_site_verification=seo_data.get("google_site_verification", ""),
                google_analytics_id=seo_data.get("google_analytics_id", ""),
                structured_data=seo_data.get("structured_data", {}),
            )

            # Create theme config
            theme_data = data.get("theme", {})
            theme_config = ThemeConfig.objects.create(
                primary_color=theme_data.get("primary_color", "#007bff"),
                secondary_color=theme_data.get("secondary_color", "#6c757d"),
                favicon_url=theme_data.get("favicon_url", ""),
                logo_url=theme_data.get("logo_url", ""),
                custom_css=theme_data.get("custom_css", ""),
                dark_mode_enabled=theme_data.get("dark_mode_enabled", True),
            )

            # Create content config
            content_data = data.get("content", {})
            content_config = ContentConfig.objects.create(
                maintenance_mode=content_data.get("maintenance_mode", False),
                maintenance_message=content_data.get(
                    "maintenance_message",
                    "We're currently performing maintenance. Please check back soon.",
                ),
                comments_enabled=content_data.get("comments_enabled", True),
                registration_enabled=content_data.get("registration_enabled", True),
                max_upload_size_mb=content_data.get("max_upload_size_mb", 10),
                allowed_file_extensions=content_data.get("allowed_file_extensions", []),
            )

        self.stdout.write("Created configuration objects:")
        self.stdout.write(f"  - SiteConfig: {site_config}")
        self.stdout.write(f"  - SEOConfig: {seo_config}")
        self.stdout.write(f"  - ThemeConfig: {theme_config}")
        self.stdout.write(f"  - ContentConfig: {content_config}")
