"""
Feature flag decorators for views and functions.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator

from ..config.loader import ConfigLoader


def feature_required(
    flag_name: str,
    default: bool = False,
    redirect_url: str | None = None,
    template: str = "core/feature_disabled.html",
    raise_404: bool = False,
):
    """
    Decorator to require a feature flag to be enabled.

    Args:
        flag_name: Name of the feature flag to check
        default: Default value if flag not found
        redirect_url: URL to redirect to if feature is disabled
        template: Template to render if feature is disabled
        raise_404: Whether to raise Http404 if feature is disabled

    Usage:
        @feature_required('registration')
        def signup_view(request):
            # Only accessible if 'registration' feature is enabled
            pass

        @feature_required('api_v2', raise_404=True)
        def api_v2_view(request):
            # Returns 404 if 'api_v2' feature is disabled
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                config = ConfigLoader.get_global_config()
                enabled = config.get_feature_flag(flag_name, default)
            except Exception:
                enabled = default

            if enabled:
                return func(*args, **kwargs)

            # Feature is disabled, handle accordingly
            if raise_404:
                raise Http404(f"Feature '{flag_name}' is not available")

            if redirect_url:
                from django.shortcuts import redirect

                return redirect(redirect_url)

            # Render disabled template
            request = args[0] if args else None
            context = {
                "feature_name": flag_name,
                "message": f"The '{flag_name}' feature is currently disabled.",
            }
            return render(request, template, context, status=503)

        return wrapper

    return decorator


def feature_gate(flag_name: str, default: bool = False):
    """
    Simple decorator that returns None if feature is disabled.

    Usage:
        @feature_gate('analytics')
        def track_event(event_name):
            # Only executes if 'analytics' feature is enabled
            # Returns None if disabled
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                config = ConfigLoader.get_global_config()
                enabled = config.get_feature_flag(flag_name, default)
            except Exception:
                enabled = default

            if enabled:
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator


def method_feature_required(
    flag_name: str,
    default: bool = False,
    redirect_url: str | None = None,
    template: str = "core/feature_disabled.html",
    raise_404: bool = False,
):
    """
    Method decorator version of feature_required for class-based views.

    Usage:
        @method_decorator(method_feature_required('comments'), name='post')
        class BlogPostView(DetailView):
            # POST method only available if 'comments' feature is enabled
            pass
    """
    return method_decorator(
        feature_required(flag_name, default, redirect_url, template, raise_404)
    )


class FeatureMixin:
    """
    Mixin for class-based views to check feature flags.
    """

    feature_flag: str | None = None
    feature_default: bool = False
    feature_redirect_url: str | None = None
    feature_template: str = "core/feature_disabled.html"
    feature_raise_404: bool = False

    def dispatch(self, request, *args, **kwargs):
        """Check feature flag before dispatching to view method."""
        if self.feature_flag:
            try:
                config = ConfigLoader.get_global_config()
                enabled = config.get_feature_flag(
                    self.feature_flag, self.feature_default
                )
            except Exception:
                enabled = self.feature_default

            if not enabled:
                return self._handle_feature_disabled(request)

        return super().dispatch(request, *args, **kwargs)

    def _handle_feature_disabled(self, request) -> HttpResponse:
        """Handle case when feature is disabled."""
        if self.feature_raise_404:
            raise Http404(f"Feature '{self.feature_flag}' is not available")

        if self.feature_redirect_url:
            from django.shortcuts import redirect

            return redirect(self.feature_redirect_url)

        context = {
            "feature_name": self.feature_flag,
            "message": f"The '{self.feature_flag}' feature is currently disabled.",
        }
        return render(request, self.feature_template, context, status=503)


def conditional_feature(
    flag_name: str, enabled_func: Callable, disabled_func: Callable = None
):
    """
    Decorator that calls different functions based on feature flag state.

    Usage:
        @conditional_feature('new_algorithm', new_process, old_process)
        def process_data(data):
            pass  # This will be ignored
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                config = ConfigLoader.get_global_config()
                enabled = config.get_feature_flag(flag_name, False)
            except Exception:
                enabled = False

            if enabled:
                return enabled_func(*args, **kwargs)
            elif disabled_func:
                return disabled_func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
