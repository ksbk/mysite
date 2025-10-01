"""
Custom admin widgets for better configuration UX.
"""

import json

from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class PrettyJSONWidget(forms.Textarea):
    """
    Enhanced JSON textarea with syntax highlighting and validation.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "json-editor",
            "rows": 10,
            "cols": 80,
            "style": "font-family: monospace;",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        """Format JSON with proper indentation."""
        if value is None or value == "":
            return ""

        try:
            if isinstance(value, str):
                # Try to parse and reformat
                parsed = json.loads(value)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            elif isinstance(value, (dict, list)):
                return json.dumps(value, indent=2, ensure_ascii=False)
            else:
                return str(value)
        except (json.JSONDecodeError, TypeError):
            return str(value)

    class Media:
        css = {"all": ("admin/css/json-widget.css",)}
        js = ("admin/js/json-widget.js",)


class NavigationWidget(PrettyJSONWidget):
    """
    Specialized widget for navigation configuration with hints.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "placeholder": json.dumps(
                [
                    {"label": "Home", "url": "/", "name": "home", "order": 1},
                    {"label": "About", "url": "/about/", "name": "about", "order": 2},
                ],
                indent=2,
            ),
            "rows": 8,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class FeatureFlagsWidget(PrettyJSONWidget):
    """
    Specialized widget for feature flags with common examples.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "placeholder": json.dumps(
                {
                    "maintenance_mode": False,
                    "new_ui_enabled": False,
                    "comments_enabled": True,
                    "registration_enabled": True,
                    "analytics_enabled": True,
                },
                indent=2,
            ),
            "rows": 6,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ColorWidget(forms.TextInput):
    """
    Color picker widget for theme colors.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "type": "color",
            "class": "color-picker",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """Render color input with preview."""
        html = super().render(name, value, attrs, renderer)

        if value:
            preview_html = format_html(
                '<div class="color-preview" style="background-color: {}; width: 30px; height: 30px; border: 1px solid #ccc; display: inline-block; margin-left: 10px; border-radius: 3px;"></div>',
                value,
            )
            html = mark_safe(html + preview_html)

        return html


class SEOPreviewWidget(forms.Widget):
    """
    Widget that shows how SEO will appear in search results.
    """

    def __init__(self, attrs=None):
        self.title_field = None
        self.description_field = None
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """Render SEO preview."""
        return format_html(
            """
            <div class="seo-preview-container">
                <div class="seo-preview">
                    <div class="seo-title" id="seo-preview-title">Your Site Title</div>
                    <div class="seo-url" id="seo-preview-url">https://yoursite.com</div>
                    <div class="seo-description" id="seo-preview-description">Your meta description appears here...</div>
                </div>
                <script>
                    // Update preview when fields change
                    function updateSEOPreview() {{
                        const titleField = document.querySelector('input[name*="title"]');
                        const descField = document.querySelector('textarea[name*="description"]');

                        if (titleField) {{
                            document.getElementById('seo-preview-title').textContent =
                                titleField.value || 'Your Site Title';
                        }}

                        if (descField) {{
                            document.getElementById('seo-preview-description').textContent =
                                descField.value || 'Your meta description appears here...';
                        }}
                    }}

                    // Attach listeners
                    document.addEventListener('DOMContentLoaded', function() {{
                        const titleField = document.querySelector('input[name*="title"]');
                        const descField = document.querySelector('textarea[name*="description"]');

                        if (titleField) titleField.addEventListener('input', updateSEOPreview);
                        if (descField) descField.addEventListener('input', updateSEOPreview);

                        updateSEOPreview();
                    }});
                </script>
            </div>
            """
        )

    class Media:
        css = {"all": ("admin/css/seo-preview.css",)}
