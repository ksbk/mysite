from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

_manifest_cache: dict[str, dict[str, Any]] = {}


def _load_manifest() -> dict[str, Any]:
    path = getattr(settings, "VITE_MANIFEST_PATH", None)
    if not path:
        return {}
    try:
        mtime = str(Path(path).stat().st_mtime)
        cache_key = f"{path}:{mtime}"
    except FileNotFoundError:
        return {}

    if cache_key in _manifest_cache:
        return _manifest_cache[cache_key]

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        _manifest_cache.clear()
        _manifest_cache[cache_key] = data
        return data
    except Exception:
        return {}


@register.simple_tag
def vite_hmr() -> str:
    """Include Vite HMR client in development; noop in production."""
    if getattr(settings, "DEBUG", False):
        dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
        return mark_safe(
            f'<script type="module" src="{dev_url}/@vite/client"></script>'
        )
    return ""


@register.simple_tag
def vite_asset(entry: str = "src/main.ts") -> str:
    """
    Include the Vite entry script and any CSS.

    - In development, load directly from the dev server.
    - In production, resolve paths via the Vite manifest.
    """
    if getattr(settings, "DEBUG", False):
        dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
        return mark_safe(
            "\n".join([
                f'<script type="module" src="{dev_url}/{entry}"></script>',
            ])
        )

    manifest = _load_manifest()
    if not manifest:
        return ""

    item = manifest.get(entry)
    if not item:
        return ""

    tags: list[str] = []

    # CSS files
    for css_path in item.get("css", []):
        tags.append(f'<link rel="stylesheet" href="{static(css_path)}" />')

    # JS file
    file_path = item.get("file")
    if file_path:
        tags.append(f'<script type="module" src="{static(file_path)}"></script>')

    return mark_safe("\n".join(tags))
