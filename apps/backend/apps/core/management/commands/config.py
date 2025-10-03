"""Django management command for configuration operations (alias for sitecfg)."""

from django.core.management.base import BaseCommand

from .sitecfg import Command as SitecfgCommand


class Command(BaseCommand):
    """Configuration management command (alias for sitecfg)."""

    help = "Manage configuration (alias for sitecfg command)"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Delegate to sitecfg command
        sitecfg_command = SitecfgCommand()
        sitecfg_command.add_arguments(parser)

    def handle(self, *args, **options):
        """Handle command execution."""
        # Delegate to sitecfg command
        sitecfg_command = SitecfgCommand()
        return sitecfg_command.handle(*args, **options)
