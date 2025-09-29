from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "summary", "body")
    date_hierarchy = "published_at"
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at", "-created_at")
