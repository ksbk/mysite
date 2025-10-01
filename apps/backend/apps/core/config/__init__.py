"""
Unified configuration system - simplified and clean.

This package provides:
- Unified ConfigService for both sync and async operations
- Type-safe configuration handling
- Efficient caching with structured keys
- Error handling and validation
- Change detection and cache invalidation
- Simple, maintainable architecture
"""

from .cache import cache_manager
from .versioning import (
    ConfigChange,
    cache_invalidator,
    change_tracker,
    get_recent_config_changes,
    invalidate_config_cache,
    register_config_change_handler,
)
from .errors import ConfigError, ConfigLogger, config_logger, error_handler
from .loader import ConfigService, get_config, get_config_async, get_site_config
from .unified_types import ConfigProvider, MaintenanceContext, RequestConfig
from .validation import ConfigValidator, HealthChecker

# Models re-export for convenience
from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig

# Backward compatibility
ConfigLoader = ConfigService
AsyncConfigLoader = ConfigService

__all__ = [
    # Core service
    "ConfigService",
    "ConfigProvider",
    "cache_manager",
    "get_config",
    "get_config_async",
    "get_site_config",
    # Error handling
    "ConfigError",
    "ConfigLogger",
    "config_logger",
    "error_handler",
    # Validation
    "ConfigValidator",
    "HealthChecker",
    # Change detection
    "ConfigChange",
    "change_tracker",
    "cache_invalidator",
    "invalidate_config_cache",
    "get_recent_config_changes",
    "register_config_change_handler",
    # Types
    "RequestConfig",
    "MaintenanceContext",
    # Configuration Models (re-exported for convenience)
    "SiteConfig",
    "SEOConfig",
    "ThemeConfig",
    "ContentConfig",
    # Backward compatibility
    "ConfigLoader",
    "AsyncConfigLoader",
]
