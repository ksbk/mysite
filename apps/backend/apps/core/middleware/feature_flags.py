"""
Feature flag middleware for adding context and handling global flags.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from ..config.loader import ConfigService
from ..config.unified_types import RequestConfig


class FeatureFlagMiddleware(MiddlewareMixin):
    """
    Middleware to add feature flags to request context and handle global flags.
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Add feature flags to request for easy access in views."""
        try:
            # Use typed configuration instead of dynamic attributes
            if not hasattr(request, "_config"):
                global_config = ConfigService.get_config()
                request._config = RequestConfig.from_config_data(global_config)  # type: ignore

            # Backward compatibility - still set legacy attributes
            config = request._config  # type: ignore
            feature_flags = config.get_feature_flags()
            request.feature_flags = feature_flags  # type: ignore

            # Create has_feature method for backward compatibility
            def has_feature(flag: str, default: bool = False) -> bool:
                return feature_flags.get(flag, default)

            request.has_feature = has_feature  # type: ignore
        except Exception:
            request._config = RequestConfig.create_empty()  # type: ignore
            request.feature_flags = {}  # type: ignore
            request.has_feature = lambda flag, default=False: default  # type: ignore

        # Check for maintenance mode using typed config
        feature_flags = getattr(request, "feature_flags", {})
        if feature_flags.get("maintenance_mode", False):
            # Skip maintenance for admin and certain paths
            if self._should_skip_maintenance(request):
                return None

            # Show maintenance page with typed context
            return self._render_maintenance_page(request)

        return None

    def _should_skip_maintenance(self, request: HttpRequest) -> bool:
        """Check if maintenance mode should be skipped for this request."""
        # Skip for admin
        if request.path.startswith("/admin/"):
            return True

        # Skip for staff users (check carefully for user attribute)
        if hasattr(request, "user") and hasattr(request.user, "is_authenticated"):
            if request.user.is_authenticated and hasattr(request.user, "is_staff"):
                if getattr(request.user, "is_staff", False):
                    return True

        # Skip for certain paths (health checks, etc.)
        skip_paths = ["/health/", "/status/", "/ping/"]
        if any(request.path.startswith(path) for path in skip_paths):
            return True

        return False

    def _render_maintenance_page(self, request: HttpRequest) -> HttpResponse:
        """Render maintenance mode page."""
        try:
            # Use cached config if available, otherwise load fresh
            config = getattr(request, "_config", None)
            if config is not None:
                content_config = config.get_content_config()
                message = content_config.get(
                    "maintenance_message",
                    "We're currently performing maintenance. Please check back soon.",
                )
            else:
                # Fallback to fresh config load
                global_config = ConfigService.get_config()
                content_config = global_config.get("content", {})
                message = content_config.get(
                    "maintenance_message",
                    "We're currently performing maintenance. Please check back soon.",
                )
        except Exception:
            message = "We're currently performing maintenance. Please check back soon."

        context = {
            "maintenance_message": message,
            "site_name": getattr(request, "site_name", "Site"),
        }
        return render(request, "core/maintenance.html", context, status=503)


class FeatureFlagContextMiddleware(MiddlewareMixin):
    """
    Lightweight middleware to add feature flags to template context.
    """

    def process_template_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Add feature flags to template context using typed config."""
        # Check if response has context_data (TemplateResponse)
        # Check if response has context_data (TemplateResponse)
        if (
            hasattr(response, "context_data")
            and hasattr(response, "context_data")
            and getattr(response, "context_data", None) is not None
        ):
            try:
                # Use typed config from request if available
                config = getattr(request, "_config", None)
                if config is not None:
                    feature_flags = config.get_feature_flags()

                    def has_feature(flag: str, default: bool = False) -> bool:
                        return feature_flags.get(flag, default)

                    response.context_data["feature_flags"] = feature_flags  # type: ignore
                    response.context_data["has_feature"] = has_feature  # type: ignore
                else:
                    # Fallback - create fresh typed config
                    global_config = ConfigService.get_config()
                    typed_config = RequestConfig.from_config_data(global_config)
                    feature_flags = typed_config.get_feature_flags()

                    def has_feature(flag: str, default: bool = False) -> bool:
                        return feature_flags.get(flag, default)

                    response.context_data["feature_flags"] = feature_flags  # type: ignore
                    response.context_data["has_feature"] = has_feature  # type: ignore
            except Exception:
                response.context_data["feature_flags"] = {}  # type: ignore
                response.context_data["has_feature"] = (  # type: ignore
                    lambda flag, default=False: default
                )

        return response
