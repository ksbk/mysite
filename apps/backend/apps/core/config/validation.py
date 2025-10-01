"""
Configuration validation and health checks for production deployment.
Provides comprehensive validation of configuration data and system health.
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any

try:
    from pydantic import ValidationError as PydanticValidationError
except ImportError:
    PydanticValidationError = ValueError

from .errors import ConfigErrorHandler, ConfigLogger, config_logger


class HealthStatus(str, Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ValidationResult:
    """Result of configuration validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    context: dict[str, Any]


@dataclass(frozen=True)
class HealthCheck:
    """Individual health check result."""

    name: str
    status: HealthStatus
    message: str
    details: dict[str, Any]
    duration_ms: float


class ConfigValidator:
    """
    Comprehensive configuration validator with Pydantic integration.
    Validates structure, content, and business rules.
    """

    def __init__(self, logger: ConfigLogger | None = None):
        self.logger = logger or config_logger
        self.error_handler = ConfigErrorHandler(self.logger)

    def validate_config(self, config_data: dict[str, Any]) -> ValidationResult:
        """Validate complete configuration structure and content."""
        errors = []
        warnings = []
        context = {"sections_validated": 0, "fields_checked": 0}

        try:
            # Basic structure validation (simplified without Pydantic)
            self._validate_structure(config_data)
            context["schema_valid"] = True

        except ValueError as e:
            context["schema_valid"] = False
            errors.append(f"Schema validation error: {e}")

        # Business rule validation
        try:
            self._validate_business_rules(config_data, errors, warnings)
            context["business_rules_checked"] = True
        except Exception as e:
            errors.append(f"Business rule validation failed: {e}")
            context["business_rules_checked"] = False

        # Cross-section validation
        try:
            self._validate_cross_sections(config_data, errors, warnings)
            context["cross_validation_done"] = True
        except Exception as e:
            errors.append(f"Cross-section validation failed: {e}")
            context["cross_validation_done"] = False

        is_valid = len(errors) == 0

        if not is_valid:
            self.logger.error(
                "Configuration validation failed",
                error_count=len(errors),
                warning_count=len(warnings),
            )
        elif warnings:
            self.logger.warning(
                "Configuration validation completed with warnings",
                warning_count=len(warnings),
            )
        else:
            self.logger.info("Configuration validation successful")

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            context=context,
        )

    def _validate_structure(self, config_data: dict[str, Any]) -> None:
        """Validate basic configuration structure."""
        required_sections = ["site", "seo", "theme", "content"]
        for section in required_sections:
            if section not in config_data:
                raise ValueError(f"Missing required section: {section}")
            if not isinstance(config_data[section], dict):
                raise ValueError(f"Section '{section}' must be a dictionary")

    def _validate_business_rules(
        self, config_data: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        """Validate business-specific rules and constraints."""
        site_config = config_data.get("site", {})

        # Required business fields
        if not site_config.get("site_name"):
            errors.append("Site name is required for SEO and branding")

        if not site_config.get("contact_email"):
            warnings.append("Contact email should be set for user support")

        # Theme validation
        theme_config = config_data.get("theme", {})
        primary_color = theme_config.get("primary_color", "")
        if primary_color and not primary_color.startswith("#"):
            warnings.append("Primary color should be a hex color code")

        # Content validation
        content_config = config_data.get("content", {})
        max_size = content_config.get("max_file_size", 0)
        if max_size > 10 * 1024 * 1024:  # 10MB
            warnings.append("Max file size is quite large, consider performance")

        # Feature flag validation
        feature_flags = site_config.get("feature_flags", {})
        maintenance_mode = feature_flags.get("maintenance_mode")
        maintenance_msg = content_config.get("maintenance_message")
        if maintenance_mode and not maintenance_msg:
            errors.append(
                "Maintenance message required when maintenance mode is enabled"
            )

    def _validate_cross_sections(
        self, config_data: dict[str, Any], errors: list[str], warnings: list[str]
    ) -> None:
        """Validate relationships between configuration sections."""
        site_config = config_data.get("site", {})
        seo_config = config_data.get("seo", {})

        # SEO and site consistency
        site_name = site_config.get("site_name", "")
        seo_title = seo_config.get("title", "")

        if site_name and seo_title and site_name not in seo_title:
            warnings.append("SEO title should include site name for branding")

        # Domain and canonical URL consistency
        domain = site_config.get("domain", "")
        canonical_url = seo_config.get("canonical_url", "")

        if domain and canonical_url and domain not in canonical_url:
            warnings.append("Canonical URL should match configured domain")


class HealthChecker:
    """
    System health checker for configuration and dependencies.
    Provides comprehensive health monitoring for production deployment.
    """

    def __init__(self, logger: ConfigLogger | None = None):
        self.logger = logger or config_logger

    async def run_health_checks(self) -> list[HealthCheck]:
        """Run all health checks and return results."""
        checks = []

        # Run checks in parallel for efficiency
        check_tasks = [
            self._check_database_connection(),
            self._check_cache_connectivity(),
            self._check_file_permissions(),
            self._check_memory_usage(),
            self._check_configuration_integrity(),
        ]

        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                checks.append(
                    HealthCheck(
                        name="system_check",
                        status=HealthStatus.CRITICAL,
                        message=f"Health check failed: {result}",
                        details={"exception": str(result)},
                        duration_ms=0.0,
                    )
                )
            else:
                checks.append(result)

        # Log overall health status
        critical_count = sum(
            1 for check in checks if check.status == HealthStatus.CRITICAL
        )
        warning_count = sum(
            1 for check in checks if check.status == HealthStatus.WARNING
        )

        if critical_count > 0:
            self.logger.critical(
                f"Health check failed with {critical_count} critical issues",
                critical_count=critical_count,
                warning_count=warning_count,
            )
        elif warning_count > 0:
            self.logger.warning(
                f"Health check completed with {warning_count} warnings",
                warning_count=warning_count,
            )
        else:
            self.logger.info("All health checks passed")

        return checks

    async def _check_database_connection(self) -> HealthCheck:
        """Check database connectivity and response time."""
        import time

        from django.db import connections
        from django.db.utils import OperationalError

        start_time = time.time()
        try:
            connection = connections["default"]
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            duration = (time.time() - start_time) * 1000
            status = HealthStatus.WARNING if duration > 100 else HealthStatus.HEALTHY

            return HealthCheck(
                name="database_connection",
                status=status,
                message=f"Database responsive in {duration:.1f}ms",
                details={"response_time_ms": duration},
                duration_ms=duration,
            )

        except OperationalError as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="database_connection",
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {e}",
                details={"error": str(e)},
                duration_ms=duration,
            )

    async def _check_cache_connectivity(self) -> HealthCheck:
        """Check cache system connectivity."""
        import time

        from django.core.cache import cache

        start_time = time.time()
        test_key = "health_check_test"
        test_value = "ok"

        try:
            # Test set and get operations
            cache.set(test_key, test_value, timeout=60)
            retrieved = cache.get(test_key)
            cache.delete(test_key)

            duration = (time.time() - start_time) * 1000

            if retrieved == test_value:
                return HealthCheck(
                    name="cache_connectivity",
                    status=HealthStatus.HEALTHY,
                    message=f"Cache operational in {duration:.1f}ms",
                    details={"response_time_ms": duration},
                    duration_ms=duration,
                )
            else:
                return HealthCheck(
                    name="cache_connectivity",
                    status=HealthStatus.CRITICAL,
                    message="Cache set/get operation failed",
                    details={"expected": test_value, "actual": retrieved},
                    duration_ms=duration,
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="cache_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Cache connectivity failed: {e}",
                details={"error": str(e)},
                duration_ms=duration,
            )

    async def _check_file_permissions(self) -> HealthCheck:
        """Check file system permissions for critical directories."""
        import os
        import time

        from django.conf import settings

        start_time = time.time()

        try:
            # Check media directory permissions
            media_root = getattr(settings, "MEDIA_ROOT", None)
            if media_root and os.path.exists(media_root):
                test_file = os.path.join(media_root, "health_check.tmp")
                try:
                    with open(test_file, "w") as f:
                        f.write("test")
                    os.remove(test_file)
                    media_writable = True
                except (PermissionError, OSError):
                    media_writable = False
            else:
                media_writable = None

            duration = (time.time() - start_time) * 1000

            if media_writable is False:
                return HealthCheck(
                    name="file_permissions",
                    status=HealthStatus.CRITICAL,
                    message="Media directory is not writable",
                    details={"media_root": media_root},
                    duration_ms=duration,
                )
            elif media_writable is None:
                return HealthCheck(
                    name="file_permissions",
                    status=HealthStatus.WARNING,
                    message="Media directory not configured",
                    details={"media_root": media_root},
                    duration_ms=duration,
                )
            else:
                return HealthCheck(
                    name="file_permissions",
                    status=HealthStatus.HEALTHY,
                    message="File permissions are correct",
                    details={"media_writable": True},
                    duration_ms=duration,
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="file_permissions",
                status=HealthStatus.CRITICAL,
                message=f"File permission check failed: {e}",
                details={"error": str(e)},
                duration_ms=duration,
            )

    async def _check_memory_usage(self) -> HealthCheck:
        """Check current memory usage."""
        import time

        try:
            import psutil
        except ImportError:
            psutil = None

        start_time = time.time()

        try:
            if psutil is None:
                duration = (time.time() - start_time) * 1000
                return HealthCheck(
                    name="memory_usage",
                    status=HealthStatus.UNKNOWN,
                    message="Memory monitoring unavailable (psutil not installed)",
                    details={"psutil_available": False},
                    duration_ms=duration,
                )

            memory = psutil.virtual_memory()
            duration = (time.time() - start_time) * 1000

            if memory.percent > 90:
                status = HealthStatus.CRITICAL
                message = f"Memory usage critically high: {memory.percent:.1f}%"
            elif memory.percent > 75:
                status = HealthStatus.WARNING
                message = f"Memory usage elevated: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"

            return HealthCheck(
                name="memory_usage",
                status=status,
                message=message,
                details={
                    "percent_used": memory.percent,
                    "available_mb": memory.available // (1024 * 1024),
                    "total_mb": memory.total // (1024 * 1024),
                },
                duration_ms=duration,
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="memory_usage",
                status=HealthStatus.UNKNOWN,
                message=f"Memory check failed: {e}",
                details={"error": str(e)},
                duration_ms=duration,
            )

    async def _check_configuration_integrity(self) -> HealthCheck:
        """Check configuration system integrity."""
        import time

        start_time = time.time()

        try:
            # Import and test the configuration service
            from .loader import ConfigService

            config_service = ConfigService()
            test_config = await config_service.get_config_async(use_cache=True)

            duration = (time.time() - start_time) * 1000

            if test_config:
                return HealthCheck(
                    name="configuration_integrity",
                    status=HealthStatus.HEALTHY,
                    message="Configuration system operational",
                    details={"config_loaded": True},
                    duration_ms=duration,
                )
            else:
                return HealthCheck(
                    name="configuration_integrity",
                    status=HealthStatus.WARNING,
                    message="Configuration system returned empty config",
                    details={"config_loaded": False},
                    duration_ms=duration,
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="configuration_integrity",
                status=HealthStatus.CRITICAL,
                message=f"Configuration system failed: {e}",
                details={"error": str(e)},
                duration_ms=duration,
            )
