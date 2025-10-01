"""
Modern cache management with dependency injection and structured keys.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from django.core.cache import cache


class CacheNamespace(str, Enum):
    """Structured cache namespaces for better organization."""

    CORE = "core"
    CONFIG = "config"
    FEATURE_FLAGS = "feature_flags"
    SITE_DATA = "site_data"


class CacheState(str, Enum):
    """Cache processing states for clear key semantics."""

    RAW = "raw"
    RESOLVED = "resolved"
    VALIDATED = "validated"
    PROCESSED = "processed"


@dataclass(frozen=True)
class CacheKey:
    """
    Structured cache key with semantic meaning.

    Pattern: {namespace}:{resource}:{state}:{version}
    Example: core:site_config:resolved:v1
    """

    namespace: CacheNamespace
    resource: str
    state: CacheState
    version: str

    def __str__(self) -> str:
        return f"{self.namespace}:{self.resource}:{self.state}:{self.version}"


class CacheProvider(Protocol):
    """Protocol for cache backends - enables dependency injection."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        ...

    def set(self, key: str, value: Any, timeout: int | None = None) -> bool:
        """Set value in cache with optional timeout."""
        ...

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...


class DjangoCacheProvider:
    """Django cache backend adapter."""

    def get(self, key: str, default: Any = None) -> Any:
        return cache.get(key, default)

    def set(self, key: str, value: Any, timeout: int | None = None) -> bool:
        cache.set(key, value, timeout)
        return True  # Django cache.set doesn't return boolean

    def delete(self, key: str) -> bool:
        return cache.delete(key)


@dataclass
class CacheConfig:
    """Configuration for cache operations."""

    default_timeout: int = 900  # 15 minutes
    version: str = "v1"  # Increment on schema changes to auto-invalidate
    provider: CacheProvider = DjangoCacheProvider()


class ModernCacheManager:
    """
    Modern cache manager with structured keys and dependency injection.
    """

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig()

    def get_site_config_key(self) -> CacheKey:
        """Get structured key for resolved site configuration."""
        return CacheKey(
            namespace=CacheNamespace.CORE,
            resource="site_config",
            state=CacheState.RESOLVED,
            version=self.config.version,
        )

    def get_feature_flags_key(self) -> CacheKey:
        """Get structured key for feature flags."""
        return CacheKey(
            namespace=CacheNamespace.CORE,
            resource="feature_flags",
            state=CacheState.PROCESSED,
            version=self.config.version,
        )

    def get(self, key: CacheKey, default: Any = None) -> Any:
        """Get value from cache using structured key."""
        return self.config.provider.get(str(key), default)

    def set(
        self,
        key: CacheKey,
        value: Any,
        timeout: int | None = None,
    ) -> bool:
        """Set value in cache using structured key."""
        cache_timeout = timeout or self.config.default_timeout
        return self.config.provider.set(str(key), value, cache_timeout)

    def delete(self, key: CacheKey) -> bool:
        """Delete value from cache using structured key."""
        return self.config.provider.delete(str(key))

    def invalidate_namespace(self, namespace: CacheNamespace) -> list[bool]:
        """
        Invalidate all keys in a namespace.
        Note: This is a simple implementation - production would use cache tags.
        """
        # In production, you'd use cache tags or redis patterns
        # For now, we'll track keys we've created
        results = []
        for resource in ["site_config", "feature_flags"]:
            for state in CacheState:
                key = CacheKey(namespace, resource, state, self.config.version)
                results.append(self.delete(key))
        return results


# Global cache manager instance
cache_manager = ModernCacheManager()
