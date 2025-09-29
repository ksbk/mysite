from __future__ import annotations

import time
from urllib.request import urlopen

from django.conf import settings

_last_check = 0.0
_last_result = False


def _check_vite_available(url: str, ttl: float = 10.0) -> bool:
    global _last_check, _last_result
    now = time.monotonic()
    if now - _last_check < ttl:
        return _last_result
    try:
        # cheap probe for HMR client
        with urlopen(f"{url}/@vite/client", timeout=0.5):
            _last_result = True
    except Exception:
        _last_result = False
    _last_check = now
    return _last_result


def vite(request):
    dev = getattr(settings, "DEBUG", False)
    dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
    available = _check_vite_available(dev_url) if dev else False
    return {
        "VITE_DEV": dev,
        "VITE_DEV_SERVER_URL": dev_url,
        "VITE_DEV_AVAILABLE": available,
    }
