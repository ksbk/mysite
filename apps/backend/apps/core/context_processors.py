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
    """Add Vite configuration to template context.

    Provides both backward-compatible top-level variables used in templates and
    a nested `vite` object for structured access.
    """
    from django.conf import settings

    dev_server_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
    is_dev = bool(getattr(settings, "VITE_DEV", settings.DEBUG))
    # Only probe HMR when dev is intended
    hmr_available = _check_vite_available(dev_server_url) if is_dev else False

    ctx = {
        # Backward-compatible variables used in templates/includes
        "VITE_DEV": is_dev,
        "VITE_DEV_SERVER_URL": dev_server_url,
        "VITE_DEV_AVAILABLE": hmr_available,
        # Structured object for future templates
        "vite": {
            "is_dev": is_dev,
            "dev_server_url": dev_server_url,
            "assets": {},
            "hmr_available": hmr_available,
        },
    }
    return ctx


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
    """Check if Vite development server is available at the given URL.

    Security hardening:
    - Only allow http/https schemes
    - Only allow localhost/127.0.0.1 host (dev-only)
    - Use a HEAD request with short timeout
    """
    try:
        from urllib.parse import urlparse
        from urllib.request import Request, urlopen

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False  # nosec B310: restrict to safe schemes
        if parsed.hostname not in ("localhost", "127.0.0.1"):
            return False  # dev server should only be local

        req = Request(url, method="HEAD")
        with urlopen(req, timeout=1) as resp:  # nosec B310: scheme/host validated
            return 200 <= getattr(resp, "status", 200) < 500
    except Exception:
        return False
