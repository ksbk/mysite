"""Template tags for accessing configuration values in templates."""

from __future__ import annotations

from django import template

from ..sitecfg.loader import get_config

register = template.Library()


@register.simple_tag
def site_name(default: str = "My Site") -> str:
    """Get the site name quickly from cached config."""
    return get_config().get("site", {}).get("site_name", default)


@register.simple_tag
def maintenance_mode(default: bool = False) -> bool:
    """Whether maintenance mode is enabled."""
    return get_config().get("content", {}).get("maintenance_mode", default)


@register.simple_tag
def noindex_enabled(default: bool = False) -> bool:
    """Whether SEO noindex is enabled."""
    return get_config().get("seo", {}).get("noindex", default)


@register.filter
def get_feature_flag(feature_flags: dict | None, flag_name: str) -> bool:
    """Check if a feature flag is enabled."""
    return (feature_flags or {}).get(flag_name, False)


@register.simple_tag
def config(path: str, default: object | None = None) -> object | None:
    """
    Fetch nested configuration values using dot-notation path.

    Examples:
        {% config "site.site_name" %}
        {% config "seo.canonical_url" "/" %}
    """
    data = get_config()
    cur: object = data
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur
