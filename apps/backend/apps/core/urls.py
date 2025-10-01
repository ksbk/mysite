"""
Core app URL patterns.
"""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # Health and status endpoints
    path("health/", views.health_check, name="health"),
    path("status/", views.status, name="status"),
]
