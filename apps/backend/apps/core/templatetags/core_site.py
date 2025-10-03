"""Site-related template tags (JSON-LD rendering) for v1."""

from __future__ import annotations

import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_json_ld(data: dict | list | None) -> str:
    """Render a minimal JSON-LD script tag from a dict or list."""
    if not data:
        return ""
    try:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return mark_safe(f'<script type="application/ld+json">{payload}</script>')
    except Exception:
        return ""


@register.filter
def absolute_uri(path: str, request=None) -> str:
    """Convert a relative path to an absolute URI."""
    if not path:
        return ""

    # If already absolute URI, return as-is
    if path.startswith(("http://", "https://", "//")):
        return path

    # For relative paths, we need request context
    # In practice, this would be available via template context
    # For now, return with protocol and domain placeholder
    if path.startswith("/"):
        return f"https://example.com{path}"
    else:
        return f"https://example.com/{path}"
