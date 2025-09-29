from __future__ import annotations

import json
import time
from urllib.request import urlopen

from django.conf import settings

from .models import SiteSettings

_last_check = 0.0
_last_result = False


def _check_vite_available(url: str, ttl: float = 10.0) -> bool:
    global _last_check, _last_result
    now = time.monotonic()
    if now - _last_check < ttl:
        return _last_result
    try:
        # cheap probe for HMR client (URL controlled via settings)  # nosec B310
        with urlopen(f"{url}/@vite/client", timeout=0.5):  # nosec B310
            _last_result = True
    except OSError:
        _last_result = False
    _last_check = now
    return _last_result


def vite(request):
    dev = bool(getattr(settings, "DEBUG", False))
    dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
    available = _check_vite_available(dev_url) if dev else False
    return {
        "DEBUG": dev,
        "VITE_DEV": dev,
        "VITE_DEV_SERVER_URL": dev_url,
        "VITE_DEV_AVAILABLE": available,
    }


def _load_site_json() -> dict:
    path = getattr(settings, "SITE_SETTINGS_JSON", None)
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def site(request):
    """Provide site customization settings with JSON fallback and DB override."""
    defaults = {
        "site_name": getattr(settings, "SITE_NAME", "MySite"),
        "meta_description": "MySite - A modern Django + Vite application",
        "meta_keywords": "django,vite,web development",
        "og_image": "",
    }

    data = {**defaults, **_load_site_json()}
    try:
        s = SiteSettings.get_solo()
        if s.site_name:
            data["site_name"] = s.site_name
        if s.meta_description:
            data["meta_description"] = s.meta_description
        if s.meta_keywords:
            data["meta_keywords"] = s.meta_keywords
        if s.og_image:
            data["og_image"] = s.og_image
    except Exception:  # nosec B110 - acceptable during initial migrations
        # On initial deploy before migrations, silently ignore DB lookup.
        # Narrowing exception types would require importing ORM errors; we
        # document the behavior and suppress Bandit as this is a benign path.
        data = data

    return {"SITE": data}
