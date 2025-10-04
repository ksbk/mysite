"""Site-related template tags (JSON-LD rendering) for v1."""

from __future__ import annotations

import json

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def render_json_ld(data: dict | list | None) -> str:
    """Render a minimal JSON-LD script tag from a dict or list."""
    if not data:
        return ""
    try:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        # Avoid mark_safe; let Django handle HTML-escaping context.
        # JSON is safe to embed verbatim inside a script tag.
        return format_html('<script type="application/ld+json">{}</script>', payload)
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
