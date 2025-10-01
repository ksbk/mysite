"""
Django admin configuration for core app models.
"""

import json

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from .widgets import (
    ColorWidget,
    FeatureFlagsWidget,
    NavigationWidget,
    PrettyJSONWidget,
    SEOPreviewWidget,
)


# Removed old inline classes - using separate admin classes instead


class SiteConfigForm(forms.ModelForm):
    """Enhanced form for site configuration with better widgets."""

    class Meta:
        model = SiteConfig
        fields = "__all__"
        widgets = {
            "feature_flags": FeatureFlagsWidget(),
            "navigation": NavigationWidget(),
        }

    def clean_feature_flags(self):
        """Validate feature flags JSON."""
        data = self.cleaned_data["feature_flags"]
        if not data:
            return {}

        try:
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data

            # Ensure all values are boolean for feature flags
            if not isinstance(parsed, dict):
                raise forms.ValidationError("Feature flags must be a JSON object")

            for key, value in parsed.items():
                if not isinstance(value, bool):
                    raise forms.ValidationError(
                        f"Feature flag '{key}' must be true or false"
                    )

            return parsed
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {e}")

    def clean_navigation(self):
        """Validate navigation JSON structure."""
        data = self.cleaned_data["navigation"]
        if not data:
            return []

        try:
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data

            if not isinstance(parsed, list):
                raise forms.ValidationError("Navigation must be a JSON array")

            for item in parsed:
                if not isinstance(item, dict):
                    raise forms.ValidationError(
                        "Each navigation item must be an object"
                    )

                required_fields = ["label", "url"]
                for field in required_fields:
                    if field not in item:
                        raise forms.ValidationError(
                            f"Navigation item missing required field: {field}"
                        )

            return parsed
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {e}")


@admin.register(SEOConfig)
class SEOConfigAdmin(admin.ModelAdmin):
    """Admin for SEO configuration singleton."""

    list_display = ["meta_title", "meta_description", "noindex", "updated_at"]
    fields = [
        "meta_title",
        "meta_description",
        "meta_keywords",
        "canonical_url",
        "og_image",
        "noindex",
        "google_site_verification",
        "google_analytics_id",
    ]

    def has_add_permission(self, request):
        return not SEOConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ThemeConfig)
class ThemeConfigAdmin(admin.ModelAdmin):
    """Admin for theme configuration singleton."""

    list_display = [
        "primary_color",
        "secondary_color",
        "dark_mode_enabled",
        "updated_at",
    ]
    fields = [
        ("primary_color", "secondary_color"),
        ("favicon_url", "logo_url"),
        "dark_mode_enabled",
        "custom_css",
    ]

    def has_add_permission(self, request):
        return not ThemeConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContentConfig)
class ContentConfigAdmin(admin.ModelAdmin):
    """Admin for content configuration singleton."""

    list_display = [
        "maintenance_mode",
        "comments_enabled",
        "registration_enabled",
        "updated_at",
    ]
    fields = [
        ("maintenance_mode", "comments_enabled", "registration_enabled"),
        "maintenance_message",
        "max_upload_size_mb",
        "allowed_file_extensions",
    ]

    def has_add_permission(self, request):
        return not ContentConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """
    Unified admin for all site configuration.
    All config models are managed as inlines under SiteConfig.
    """

    form = SiteConfigForm
    list_display = ["site_name", "site_tagline", "contact_email", "created_at"]
    search_fields = ["site_name", "site_tagline"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "feature_flags_display",
        "navigation_display",
    ]

    fieldsets = [
        (
            "Site Information",
            {
                "fields": [
                    "site_name",
                    "site_tagline",
                    "domain",
                    "contact_email",
                ],
                "description": "Basic site information displayed across the website.",
            },
        ),
        (
            "Feature Flags",
            {
                "fields": [
                    "feature_flags",
                    "feature_flags_display",
                ],
                "description": "Enable/disable features across the site. Use JSON format with boolean values.",
                "classes": ["collapse"],
            },
        ),
        (
            "Navigation",
            {
                "fields": [
                    "navigation",
                    "navigation_display",
                ],
                "description": "Configure site navigation menu. Each item needs 'label' and 'url' fields.",
                "classes": ["collapse"],
            },
        ),
        (
            "System Information",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]

    def has_add_permission(self, request):
        # Only allow one site config
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of site config
        return False

    def changelist_view(self, request, extra_context=None):
        # If no config exists, redirect to add form
        if not SiteConfig.objects.exists():
            from django.shortcuts import redirect
            from django.urls import reverse

            return redirect(reverse("admin:core_siteconfig_add"))

        # Otherwise show normal changelist
        return super().changelist_view(request, extra_context)

    def save_related(self, request, form, formsets, change):
        """Ensure all related config objects are created."""
        super().save_related(request, form, formsets, change)

        # Ensure all singleton configs exist
        SEOConfig.load()
        ThemeConfig.load()
        ContentConfig.load()

    def feature_flags_display(self, obj):
        """Display feature flags as formatted JSON."""
        if not obj.feature_flags:
            return "No feature flags set"
        return mark_safe(
            f"<pre>{json.dumps(obj.feature_flags, indent=2, sort_keys=True)}</pre>"
        )

    feature_flags_display.short_description = "Feature Flags (JSON)"

    def navigation_display(self, obj):
        """Display navigation as formatted JSON."""
        if not obj.navigation:
            return "No navigation set"
        return mark_safe(
            f"<pre>{json.dumps(obj.navigation, indent=2, sort_keys=True)}</pre>"
        )

    navigation_display.short_description = "Navigation (JSON)"


# Admin classes defined above - no duplicates needed
