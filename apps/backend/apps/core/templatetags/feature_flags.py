"""
Feature flag template tags for conditional rendering.
"""

from django import template
from django.template import Context, Template

from ..config.loader import ConfigLoader

register = template.Library()


@register.simple_tag
def feature_flag(flag_name: str, default: bool = False) -> bool:
    """
    Get a feature flag value.

    Usage:
        {% feature_flag 'dark_mode' as dark_mode_enabled %}
        {% if dark_mode_enabled %}
            <div class="dark-theme">...</div>
        {% endif %}
    """
    try:
        config = ConfigLoader.get_global_config()
        return config.get_feature_flag(flag_name, default)
    except Exception:
        return default


@register.inclusion_tag("core/feature_flag_block.html", takes_context=True)
def if_feature(context: Context, flag_name: str, default: bool = False) -> dict:
    """
    Conditional block based on feature flag.

    Usage:
        {% if_feature 'analytics' %}
            <script>// Analytics code</script>
        {% endif_feature %}
    """
    enabled = feature_flag(flag_name, default)
    return {
        "enabled": enabled,
        "flag_name": flag_name,
        "context": context,
    }


@register.simple_tag(takes_context=True)
def render_if_feature(
    context: Context, flag_name: str, template_string: str, default: bool = False
) -> str:
    """
    Render template string if feature is enabled.

    Usage:
        {% render_if_feature 'pwa' '<link rel="manifest" href="/manifest.json">' %}
    """
    enabled = feature_flag(flag_name, default)
    if not enabled:
        return ""

    try:
        template_obj = Template(template_string)
        return template_obj.render(context)
    except Exception:
        return ""


@register.filter
def has_feature(flag_name: str, default: bool = False) -> bool:
    """
    Filter to check if feature is enabled.

    Usage:
        {% if 'dark_mode'|has_feature %}
            <div class="dark-theme">...</div>
        {% endif %}
    """
    return feature_flag(flag_name, default)


@register.simple_tag
def feature_css_class(flag_name: str, css_class: str, default: bool = False) -> str:
    """
    Return CSS class if feature is enabled.

    Usage:
        <body class="{% feature_css_class 'dark_mode' 'theme-dark' %}">
    """
    enabled = feature_flag(flag_name, default)
    return css_class if enabled else ""


@register.simple_tag
def feature_config(flag_name: str, config_key: str, default: str = "") -> str:
    """
    Get configuration value if feature is enabled.

    Usage:
        {% feature_config 'analytics' 'seo.google_analytics_id' as ga_id %}
    """
    enabled = feature_flag(flag_name, False)
    if not enabled:
        return ""

    try:
        return ConfigLoader.get_config_value(config_key, default)
    except Exception:
        return default
