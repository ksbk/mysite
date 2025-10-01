"""
Enhanced error handling and structured logging for configuration system.
Provides comprehensive error types and logging with context.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ConfigErrorType(str, Enum):
    """Categorized error types for configuration issues."""

    VALIDATION_ERROR = "validation_error"
    CACHE_ERROR = "cache_error"
    DATABASE_ERROR = "database_error"
    SCHEMA_ERROR = "schema_error"
    MIGRATION_ERROR = "migration_error"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"


@dataclass(frozen=True)
class ConfigError:
    """Structured configuration error with context."""

    error_type: ConfigErrorType
    message: str
    context: dict[str, Any]
    source: str
    recoverable: bool = True

    def __str__(self) -> str:
        return f"[{self.error_type.value}] {self.message} (source: {self.source})"


class ConfigLogger:
    """
    Structured logger for configuration events with context.
    Provides consistent logging format and error tracking.
    """

    def __init__(self, name: str = "config"):
        self.logger = logging.getLogger(f"apps.core.config.{name}")
        self.errors: list[ConfigError] = []

    def info(self, message: str, **context) -> None:
        """Log info message with context."""
        self.logger.info(message, extra={"context": context})

    def warning(self, message: str, **context) -> None:
        """Log warning message with context."""
        self.logger.warning(message, extra={"context": context})

    def error(self, error: ConfigError | str, **context) -> None:
        """Log error with structured format."""
        if isinstance(error, str):
            error = ConfigError(
                error_type=ConfigErrorType.VALIDATION_ERROR,
                message=error,
                context=context,
                source="unknown",
            )

        self.errors.append(error)
        self.logger.error(
            str(error),
            extra={
                "error_type": error.error_type.value,
                "context": error.context,
                "source": error.source,
                "recoverable": error.recoverable,
            },
        )

    def critical(self, error: ConfigError | str, **context) -> None:
        """Log critical error that requires immediate attention."""
        if isinstance(error, str):
            error = ConfigError(
                error_type=ConfigErrorType.DATABASE_ERROR,
                message=error,
                context=context,
                source="unknown",
                recoverable=False,
            )

        self.errors.append(error)
        self.logger.critical(
            str(error),
            extra={
                "error_type": error.error_type.value,
                "context": error.context,
                "source": error.source,
                "recoverable": error.recoverable,
            },
        )

    def get_errors(
        self, error_type: ConfigErrorType | None = None
    ) -> list[ConfigError]:
        """Get logged errors, optionally filtered by type."""
        if error_type is None:
            return self.errors.copy()
        return [error for error in self.errors if error.error_type == error_type]

    def clear_errors(self) -> None:
        """Clear error history."""
        self.errors.clear()

    def has_critical_errors(self) -> bool:
        """Check if any non-recoverable errors have occurred."""
        return any(not error.recoverable for error in self.errors)


class ConfigErrorHandler:
    """
    Centralized error handling for configuration operations.
    Provides consistent error processing and recovery strategies.
    """

    def __init__(self, logger: ConfigLogger | None = None):
        self.logger = logger or ConfigLogger("error_handler")

    def handle_validation_error(
        self, error: Exception, source: str, context: dict[str, Any] | None = None
    ) -> ConfigError:
        """Handle validation errors with recovery options."""
        config_error = ConfigError(
            error_type=ConfigErrorType.VALIDATION_ERROR,
            message=f"Configuration validation failed: {error}",
            context=context or {},
            source=source,
            recoverable=True,
        )
        self.logger.error(config_error)
        return config_error

    def handle_cache_error(
        self, error: Exception, operation: str, context: dict[str, Any] | None = None
    ) -> ConfigError:
        """Handle cache-related errors."""
        config_error = ConfigError(
            error_type=ConfigErrorType.CACHE_ERROR,
            message=f"Cache operation '{operation}' failed: {error}",
            context=context or {},
            source="cache_manager",
            recoverable=True,
        )
        self.logger.warning(str(config_error))
        return config_error

    def handle_database_error(
        self,
        error: Exception,
        query: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ConfigError:
        """Handle database errors with fallback strategies."""
        config_error = ConfigError(
            error_type=ConfigErrorType.DATABASE_ERROR,
            message=f"Database operation failed: {error}",
            context={
                "query": query,
                **(context or {}),
            },
            source="database",
            recoverable=True,
        )
        self.logger.error(config_error)
        return config_error

    def handle_critical_error(
        self, error: Exception, source: str, context: dict[str, Any] | None = None
    ) -> ConfigError:
        """Handle critical errors that prevent system operation."""
        config_error = ConfigError(
            error_type=ConfigErrorType.SCHEMA_ERROR,
            message=f"Critical configuration error: {error}",
            context=context or {},
            source=source,
            recoverable=False,
        )
        self.logger.critical(config_error)
        return config_error

    def create_fallback_config(self, error: ConfigError) -> dict[str, Any]:
        """Create minimal fallback configuration for critical errors."""
        self.logger.info(
            "Creating fallback configuration due to error",
            error_type=error.error_type.value,
            source=error.source,
        )

        return {
            "site": {
                "site_name": "Site (Emergency Mode)",
                "site_tagline": "Configuration Error - Using Fallback",
                "domain": "",
                "contact_email": "",
                "feature_flags": {"maintenance_mode": True},
                "navigation": [],
            },
            "seo": {
                "title": "Site Error",
                "description": "Configuration system error",
                "keywords": [],
                "canonical_url": "",
                "og_image": "",
            },
            "theme": {
                "primary_color": "#dc3545",  # Bootstrap danger color
                "secondary_color": "#6c757d",
                "font_family": "system-ui",
            },
            "content": {
                "maintenance_message": (
                    "The site is experiencing configuration issues. "
                    "Please try again later."
                ),
                "allowed_file_extensions": [".txt"],
                "max_file_size": 1024,
            },
        }


# Global instances for consistent error handling
config_logger = ConfigLogger()
error_handler = ConfigErrorHandler(config_logger)

