"""
Template tags for configuration system.
Provides {% config %} and {% feature_enabled %} tags.
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def config(context, section: str, key: str | None = None, default=None):
    """
    Get configuration value from context.

    Usage:
        {% config "site.site_name" %}
        {% config "site" "site_name" %}
        {% config "theme.primary_color" "blue" %}
    """
    site_config = context.get("SITE", {})

    if key is None:
        # Handle dot notation like "site.site_name"
        if "." in section:
            parts = section.split(".", 1)
            section, key = parts
        else:
            # Return entire section
            return site_config.get(section, default)

    # Get nested value
    section_data = site_config.get(section, {})
    return section_data.get(key, default)


@register.simple_tag(takes_context=True)
def feature_enabled(context, flag_name: str, default: bool = False) -> bool:
    """
    Check if a feature flag is enabled.

    Usage:
        {% feature_enabled "maintenance_mode" %}
        {% feature_enabled "new_ui" False %}
    """
    features = context.get("FEATURES", {})
    return features.get(flag_name, default)


@register.inclusion_tag("core/partials/meta_seo.html", takes_context=True)
def render_seo_meta(context):
    """Render SEO meta tags from configuration."""
    site_config = context.get("SITE", {})
    seo_config = site_config.get("seo", {})
    site_info = site_config.get("site", {})

    return {
        "title": seo_config.get("title", site_info.get("site_name", "")),
        "description": seo_config.get("description", ""),
        "keywords": seo_config.get("keywords", []),
        "canonical_url": seo_config.get("canonical_url", ""),
        "og_image": seo_config.get("og_image", ""),
        "site_name": site_info.get("site_name", ""),
    }


@register.inclusion_tag("core/partials/navigation.html", takes_context=True)
def render_navigation(context):
    """Render navigation from configuration."""
    nav_items = context.get("NAV", [])
    return {"nav_items": nav_items}
