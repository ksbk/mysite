"""Django management command to initialize site configuration."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class Command(BaseCommand):
    """Initialize site configuration with default values."""

    help = "Initialize site configuration with default values"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force initialization even if configuration already exists",
        )
        parser.add_argument(
            "--site-name",
            type=str,
            default="My Site",
            help="Set the site name (default: My Site)",
        )
        parser.add_argument("--domain", type=str, help="Set the primary domain")
        parser.add_argument("--email", type=str, help="Set the contact email")

    def handle(self, *args, **options):
        """Handle the command."""
        force = options["force"]

        # Check if configuration already exists
        configs_exist = any([
            SiteConfig.objects.exists(),
            SEOConfig.objects.exists(),
            ThemeConfig.objects.exists(),
            ContentConfig.objects.exists(),
        ])

        if configs_exist and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Configuration already exists. Use --force to overwrite."
                )
            )
            return

        with transaction.atomic():
            # Initialize SiteConfig
            site_config, created = SiteConfig.objects.get_or_create(
                defaults={
                    "site_name": options["site_name"],
                    "site_description": "Welcome to our website",
                    "contact_email": options.get("email", ""),
                    "domain": options.get("domain", ""),
                    "maintenance_mode": False,
                    "timezone": "UTC",
                    "language_code": "en-US",
                }
            )

            # Initialize SEOConfig
            seo_config, created = SEOConfig.objects.get_or_create(
                defaults={
                    "default_title": options["site_name"],
                    "default_description": f"Welcome to {options["site_name"]}",
                    "default_keywords": "website, blog, content",
                    "noindex": False,
                    "canonical_url": "",
                    "og_image": "",
                }
            )

            # Initialize ThemeConfig
            theme_config, created = ThemeConfig.objects.get_or_create(
                defaults={
                    "primary_color": "#007bff",
                    "secondary_color": "#6c757d",
                    "accent_color": "#28a745",
                    "success_color": "#28a745",
                    "warning_color": "#ffc107",
                    "danger_color": "#dc3545",
                    "info_color": "#17a2b8",
                    "font_family": (
                        "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
                    ),
                    "font_size_base": 16,
                    "dark_mode_enabled": False,
                }
            )

            # Initialize ContentConfig
            content_config, created = ContentConfig.objects.get_or_create(
                defaults={
                    "posts_per_page": 10,
                    "allow_comments": True,
                    "comment_moderation": False,
                    "show_author_info": True,
                    "enable_related_posts": True,
                    "excerpt_length": 150,
                    "date_format": "%B %d, %Y",
                    "enable_search": True,
                    "enable_tags": True,
                    "enable_categories": True,
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully initialized site configuration for "
                f'"{options["site_name"]}"'
            )
        )

        if options.get("domain"):
            self.stdout.write(f"Domain: {options["domain"]}")
        if options.get("email"):
            self.stdout.write(f"Contact email: {options["email"]}")
