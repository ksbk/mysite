"""Vite template tags: HMR for dev and manifest-based assets for prod.

Minimal and robust:
- vite_hmr(): includes HMR client + entry during development.
- vite_asset(entry): resolves hashed files via Vite manifest.json for production.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def vite_hmr(entry: str = "src/main.ts") -> str:
    """Return minimal Vite HMR script tags for development."""
    dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
    html = (
        f'<script type="module" src="{dev_url}/@vite/client"></script>'
        f'<script type="module" src="{dev_url}/{entry}"></script>'
    )
    return mark_safe(html)


_manifest_cache: dict[str, Any] = {"path": None, "mtime": None, "data": None}


def _load_manifest() -> dict[str, Any] | None:
    manifest_path = Path(getattr(settings, "VITE_MANIFEST_PATH", ""))
    if not manifest_path:
        return None
    try:
        stat = manifest_path.stat()
    except FileNotFoundError:
        return None

    cached_path = _manifest_cache.get("path")
    cached_mtime = _manifest_cache.get("mtime")
    if cached_path == str(manifest_path) and cached_mtime == stat.st_mtime:
        return _manifest_cache.get("data")

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        _manifest_cache.update({
            "path": str(manifest_path),
            "mtime": stat.st_mtime,
            "data": data,
        })
        return data
    except Exception:
        return None


@register.simple_tag
def vite_asset(entry: str = "src/main.ts") -> str:
    """Return script/link tags for the built entry file using Vite manifest.

    Falls back to a static path if manifest is unavailable (e.g., before first build).
    """
    manifest = _load_manifest()
    if not manifest:
        # Fallback to a predictable path (non-hashed) if no manifest yet
        # Keep aligned with Vite's default assetsDir structure
        src = static("dist/js/main.js")
        return mark_safe(f'<script type="module" src="{src}"></script>')

    entry_info = manifest.get(entry)
    if not entry_info:
        # Try common key from Rollup input alias
        entry_info = next((v for k, v in manifest.items() if v.get("isEntry")), None)
    if not entry_info:
        return ""  # nothing to include

    tags: list[str] = []
    # JS entry
    file_path = entry_info.get("file")
    if file_path:
        tags.append(
            f'<script type="module" src="{static("dist/" + file_path)}"></script>'
        )
    # CSS assets
    for css_path in entry_info.get("css", []):
        tags.append(f'<link rel="stylesheet" href="{static("dist/" + css_path)}" />')

    return mark_safe("\n".join(tags))
