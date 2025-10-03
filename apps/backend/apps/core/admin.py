from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from .models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig


class SingletonModelAdmin(admin.ModelAdmin):
    """Admin for singleton models: no add/delete; always edit the single row."""

    # Convenience: show Save buttons at the top of the form
    save_on_top = True

    # Hide the Add button; we only allow editing the existing instance
    def has_add_permission(
        self, request: HttpRequest
    ) -> bool:  # pragma: no cover - trivial
        return False

    # Hide the Delete action on the change view
    def has_delete_permission(
        self, request: HttpRequest, obj=None
    ) -> bool:  # pragma: no cover - trivial
        return False

    # Redirect the changelist to the single instance change view
    def changelist_view(
        self, request: HttpRequest, extra_context=None
    ):  # pragma: no cover - trivial
        obj = self.model.load()
        url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[obj.pk],
        )
        return HttpResponseRedirect(url)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id=None,
        form_url: str = "",
        extra_context=None,
    ):  # pragma: no cover - trivial
        extra_context = extra_context or {}
        extra_context.setdefault(
            "subtitle",
            "This is a singleton. You can only edit the existing instance.",
        )
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    list_display = ("site_name", "domain", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SEOConfig)
class SEOConfigAdmin(SingletonModelAdmin):
    list_display = ("meta_title", "noindex", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ThemeConfig)
class ThemeConfigAdmin(SingletonModelAdmin):
    list_display = ("primary_color", "secondary_color", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ContentConfig)
class ContentConfigAdmin(SingletonModelAdmin):
    list_display = ("maintenance_mode", "max_upload_size_mb", "updated_at")
    readonly_fields = ("created_at", "updated_at")
