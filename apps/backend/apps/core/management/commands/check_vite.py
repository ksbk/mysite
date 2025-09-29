from urllib.request import urlopen

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check Vite dev server availability"

    def handle(self, *args, **options):
        url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
        try:
            with urlopen(f"{url}/@vite/client", timeout=1):
                self.stdout.write(self.style.SUCCESS(f"Vite dev server is up at {url}"))
                return 0
        except Exception as exc:  # pragma: no cover - simple CLI
            self.stderr.write(
                self.style.ERROR(f"Vite dev server is NOT reachable at {url}: {exc}")
            )
            return 1
