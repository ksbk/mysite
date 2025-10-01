"""
Management command to migrate configuration schemas.
"""

from django.core.management.base import BaseCommand

from ...config.versioning import migrate_all_configs


class Command(BaseCommand):
    """Migrate configuration schemas to current versions."""

    help = "Migrate configuration schemas to current versions"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without making changes",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write("DRY RUN - Would perform the following migrations:")
            # TODO: Implement dry-run logic
            self.stdout.write("  (Dry-run not yet implemented)")
            return

        self.stdout.write("Migrating configuration schemas...")

        try:
            results = migrate_all_configs()

            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            for config_name, success in results.items():
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {config_name} migrated successfully")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"✗ {config_name} migration failed")
                    )

            if success_count == total_count:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"All {total_count} configurations migrated successfully"
                    )
                )
            else:
                failed_count = total_count - success_count
                self.stdout.write(
                    self.style.WARNING(
                        f"{success_count}/{total_count} migrations successful, "
                        f"{failed_count} failed"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Migration failed: {e}"))
            raise
