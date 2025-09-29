from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "email", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("subject", "email", "message")
    ordering = ("-created_at",)
