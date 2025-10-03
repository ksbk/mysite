"""URL patterns for configuration management."""

from django.urls import path

from .views import ConfigCacheView, ConfigHealthView, ConfigValidationView

app_name = "config"

urlpatterns = [
    # Validation endpoints
    path(
        "validate/<str:config_type>/", ConfigValidationView.as_view(), name="validate"
    ),
    # Health check
    path("health/", ConfigHealthView.as_view(), name="health"),
    # Cache management
    path("cache/", ConfigCacheView.as_view(), name="cache-all"),
    path("cache/<str:config_type>/", ConfigCacheView.as_view(), name="cache-specific"),
]
