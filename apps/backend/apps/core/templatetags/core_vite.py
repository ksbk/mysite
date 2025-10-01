from django import template

register = template.Library()


@register.simple_tag
def vite_asset(asset_name):
    """Get Vite asset URL."""
    return f"http://localhost:5173/src/{asset_name}"


@register.simple_tag
def vite_hmr():
    """Include Vite HMR client."""
    return '<script type="module" src="http://localhost:5173/@vite/client"></script>'
