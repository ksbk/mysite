from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name",)
    fieldsets = (
        (None, {"fields": ("site_name",)}),
        ("SEO", {"fields": ("meta_description", "meta_keywords", "og_image")}),
    )
