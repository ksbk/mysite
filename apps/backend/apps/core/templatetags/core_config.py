"""
Template tags for accessing configuration values in templates.
"""

from django import template

from ..config import ConfigLoader

register = template.Library()


@register.simple_tag(takes_context=True)
def config(context, path: str, default=None):
    """
    Get a configuration value by dot notation path.

    Usage in templates:
        {% config "site.site_name" %}
        {% config "seo.meta_title" "Default Title" %}
        {% config "theme.primary_color" "#007bff" %}
    """
    # Use cached config by default for performance
    return ConfigLoader.get_config_value(path, default, use_cache=True)


@register.inclusion_tag("core/config/site_config.html", takes_context=True)
def site_config(context):
    """
    Include tag that provides all site configuration in a template.

    Usage:
        {% site_config %}
    """
    return {
        "site_config": ConfigLoader.get_site_config(use_cache=True),
        "request": context.get("request"),
    }


@register.inclusion_tag("core/config/seo_meta.html", takes_context=True)
def seo_meta(context):
    """
    Include tag that renders SEO meta tags.

    Usage:
        {% seo_meta %}
    """
    seo_config = ConfigLoader.get_seo_config(use_cache=True)
    return {
        "seo": seo_config,
        "request": context.get("request"),
    }


@register.inclusion_tag("core/config/theme_vars.html", takes_context=True)
def theme_vars(context):
    """
    Include tag that renders CSS custom properties for theme.

    Usage:
        {% theme_vars %}
    """
    theme_config = ConfigLoader.get_theme_config(use_cache=True)
    return {
        "theme": theme_config,
        "request": context.get("request"),
    }


@register.filter
def get_feature_flag(feature_flags: dict, flag_name: str) -> bool:
    """
    Template filter to check if a feature flag is enabled.

    Usage:
        {% if site_config.feature_flags|get_feature_flag:"dark_mode" %}
    """
    return feature_flags.get(flag_name, False) if feature_flags else False


@register.simple_tag
def maintenance_mode():
    """
    Check if maintenance mode is enabled.

    Usage:
        {% maintenance_mode as is_maintenance %}
        {% if is_maintenance %}...{% endif %}
    """
    return ConfigLoader.get_config_value("content.maintenance_mode", False)


@register.simple_tag
def site_name():
    """
    Get the site name.

    Usage:
        <title>{% site_name %}</title>
    """
    return ConfigLoader.get_config_value("site.site_name", "My Site")


@register.simple_tag
def noindex_enabled():
    """
    Check if noindex is enabled.

    Usage:
        {% noindex_enabled as noindex %}
        {% if noindex %}<meta name="robots" content="noindex">{% endif %}
    """
    return ConfigLoader.get_config_value("seo.noindex", False)
