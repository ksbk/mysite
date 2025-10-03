"""Context processors for core app."""

from typing import Any

from django.http import HttpRequest

from apps.core.sitecfg import get_config


def site_context(request: HttpRequest) -> dict[str, Any]:
    """Add configuration to template context."""
    try:
        config = get_config()
        return {"config": config}
    except Exception:
        return {"config": {}}


def vite(request: HttpRequest) -> dict[str, Any]:
    """Add Vite configuration to template context."""
    from django.conf import settings

    return {
        "vite": {
            "is_dev": settings.DEBUG,
            "dev_server_url": getattr(
                settings, "VITE_DEV_SERVER_URL", "http://localhost:5173"
            ),
            "assets": {},
            "hmr_available": False,
        }
    }


def security(request: HttpRequest) -> dict[str, Any]:
    """Add security context for templates."""
    return {
        "security": {
            "csrf_token": request.META.get("CSRF_COOKIE"),
        }
    }


# Aliases for tests that expect these specific function names
def config_context(request: HttpRequest) -> dict[str, Any]:
    """Alias for site_context - used by integration tests."""
    return site_context(request)


def vite_context(request: HttpRequest) -> dict[str, Any]:
    """Alias for vite - used by integration tests."""
    return vite(request)


def _check_vite_available(url: str) -> bool:
    """Check if Vite development server is available at the given URL."""
    try:
        import urllib.request

        urllib.request.urlopen(url, timeout=1)
        return True
    except Exception:
        return False
