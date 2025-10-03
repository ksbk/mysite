"""Configuration validation and management views."""

import json
import logging
from typing import Any

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError as PydanticValidationError

from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from .loader import ConfigLoader
from .schemas import (
    ContentConfigSchema,
    SEOConfigSchema,
    SiteConfigSchema,
    ThemeConfigSchema,
)

logger = logging.getLogger(__name__)

SCHEMA_MAP = {
    "site": SiteConfigSchema,
    "seo": SEOConfigSchema,
    "theme": ThemeConfigSchema,
    "content": ContentConfigSchema,
}

MODEL_MAP = {
    "site": SiteConfig,
    "seo": SEOConfig,
    "theme": ThemeConfig,
    "content": ContentConfig,
}


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class ConfigValidationView(View):
    """Validate configuration data before saving."""

    def post(self, request, config_type: str):
        """Validate configuration data."""
        if config_type not in SCHEMA_MAP:
            return JsonResponse(
                {
                    "valid": False,
                    "errors": [f"Unknown configuration type: {config_type}"],
                },
                status=400,
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse(
                {"valid": False, "errors": [f"Invalid JSON: {str(e)}"]}, status=400
            )

        schema_class = SCHEMA_MAP[config_type]

        try:
            # Validate with Pydantic schema
            validated_data = schema_class(**data)

            # Additional business logic validation
            validation_errors = self._validate_business_rules(
                config_type, validated_data
            )

            if validation_errors:
                return JsonResponse({"valid": False, "errors": validation_errors})

            return JsonResponse({
                "valid": True,
                "validated_data": validated_data.model_dump(),
                "message": f"{config_type.title()} configuration is valid",
            })

        except PydanticValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                errors.append(f"{field}: {error["msg"]}")

            return JsonResponse({"valid": False, "errors": errors}, status=400)

        except Exception as e:
            logger.exception(f"Validation error for {config_type} config")
            return JsonResponse(
                {"valid": False, "errors": [f"Validation failed: {str(e)}"]}, status=500
            )

    def _validate_business_rules(self, config_type: str, data: Any) -> list[str]:
        """Validate business-specific rules."""
        errors = []

        if config_type == "site":
            # Validate site-specific rules
            if hasattr(data, "maintenance_mode") and data.maintenance_mode:
                if (
                    not hasattr(data, "maintenance_message")
                    or not data.maintenance_message
                ):
                    errors.append(
                        "maintenance_message is required when "
                        "maintenance_mode is enabled"
                    )

        elif config_type == "seo":
            # Validate SEO-specific rules
            if hasattr(data, "meta_title") and len(data.meta_title) > 60:
                errors.append(
                    "meta_title should be under 60 characters for optimal SEO"
                )

            if hasattr(data, "meta_description") and len(data.meta_description) > 160:
                errors.append(
                    "meta_description should be under 160 characters " "for optimal SEO"
                )

        elif config_type == "theme":
            # Validate theme-specific rules
            if hasattr(data, "custom_css") and data.custom_css:
                # Basic CSS validation (check for common issues)
                if "javascript:" in data.custom_css.lower():
                    errors.append("custom_css cannot contain JavaScript code")

        return errors


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class ConfigHealthView(View):
    """Configuration system health check."""

    def get(self, request):
        """Check configuration system health."""
        health_status = {"healthy": True, "checks": {}, "timestamp": None}

        try:
            # Check cache connectivity
            loader = ConfigLoader()
            cache_healthy = self._check_cache_health(loader)
            health_status["checks"]["cache"] = {
                "healthy": cache_healthy,
                "message": (
                    "Cache is accessible"
                    if cache_healthy
                    else "Cache is not accessible"
                ),
            }

            # Check database connectivity
            db_healthy = self._check_database_health()
            health_status["checks"]["database"] = {
                "healthy": db_healthy,
                "message": (
                    "Database is accessible"
                    if db_healthy
                    else "Database is not accessible"
                ),
            }

            # Check schema validation
            schema_healthy = self._check_schema_health()
            health_status["checks"]["schemas"] = {
                "healthy": schema_healthy,
                "message": (
                    "All schemas are valid"
                    if schema_healthy
                    else "Schema validation issues found"
                ),
            }

            # Overall health
            health_status["healthy"] = all(
                check["healthy"] for check in health_status["checks"].values()
            )

            from datetime import datetime

            health_status["timestamp"] = datetime.now().isoformat()

            status_code = 200 if health_status["healthy"] else 503
            return JsonResponse(health_status, status=status_code)

        except Exception as e:
            logger.exception("Health check failed")
            return JsonResponse(
                {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
                status=503,
            )

    def _check_cache_health(self, loader: ConfigLoader) -> bool:
        """Check if cache is accessible."""
        try:
            # Try to set and get a test value
            test_key = "health_check_test"
            test_value = {"test": True}
            loader._set_cache(test_key, test_value, 60)
            cached_value = loader._get_cache(test_key)
            return cached_value is not None
        except Exception:
            return False

    def _check_database_health(self) -> bool:
        """Check if database is accessible."""
        try:
            # Try to query each model
            for model_class in MODEL_MAP.values():
                model_class.objects.exists()
            return True
        except Exception:
            return False

    def _check_schema_health(self) -> bool:
        """Check if all schemas are valid."""
        try:
            # Try to instantiate each schema with minimal data
            for schema_class in SCHEMA_MAP.values():
                schema_class()  # This will use default values
            return True
        except Exception:
            return False


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class ConfigCacheView(View):
    """Configuration cache management."""

    def delete(self, request, config_type: str = None):
        """Clear configuration cache."""
        try:
            loader = ConfigLoader()

            if config_type:
                if config_type not in SCHEMA_MAP:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": f"Unknown configuration type: {config_type}",
                        },
                        status=400,
                    )

                # Clear specific config cache
                cache_key = f"config:{config_type}"
                loader._delete_cache(cache_key)
                message = f"{config_type.title()} configuration cache cleared"
            else:
                # Clear all config caches
                for conf_type in SCHEMA_MAP.keys():
                    cache_key = f"config:{conf_type}"
                    loader._delete_cache(cache_key)
                message = "All configuration caches cleared"

            return JsonResponse({"success": True, "message": message})

        except Exception as e:
            logger.exception("Cache clear failed")
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def post(self, request, config_type: str = None):
        """Warm configuration cache."""
        try:
            loader = ConfigLoader()

            if config_type:
                if config_type not in SCHEMA_MAP:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": f"Unknown configuration type: {config_type}",
                        },
                        status=400,
                    )

                # Warm specific config cache
                loader.get_config(config_type)
                message = f"{config_type.title()} configuration cache warmed"
            else:
                # Warm all config caches
                for conf_type in SCHEMA_MAP.keys():
                    loader.get_config(conf_type)
                message = "All configuration caches warmed"

            return JsonResponse({"success": True, "message": message})

        except Exception as e:
            logger.exception("Cache warm failed")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
