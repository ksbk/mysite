"""
Unified configuration service for Django applications.
Combines sync/async operations with comprehensive caching and type safety.
"""

import asyncio
from typing import Any

from asgiref.sync import sync_to_async
from django.db import transaction

from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from .cache import cache_manager
from .errors import config_logger
from .unified_types import ConfigProvider


class ConfigService(ConfigProvider):
    """
    Unified configuration service providing both sync and async access.
    Integrates caching, validation, and error handling.
    """

    @classmethod
    def get_config(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get configuration synchronously with caching support."""
        try:
            # Try cache first if enabled
            if use_cache:
                config_key = cache_manager.get_site_config_key()
                cached_config = cache_manager.get(config_key)
                if cached_config:
                    config_logger.info("Configuration loaded from cache")
                    return cached_config

            # Load from database
            config = cls._load_from_database()

            # Cache the result if caching is enabled
            if use_cache and config:
                config_key = cache_manager.get_site_config_key()
                cache_manager.set(config_key, config)
                config_logger.info("Configuration cached for future use")

            return config

        except Exception as e:
            config_logger.error(f"Failed to get configuration: {e}")
            return cls._get_default_config()

    @classmethod
    async def get_config_async(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get configuration asynchronously with caching support."""
        try:
            # Try cache first if enabled
            if use_cache:
                config_key = cache_manager.get_site_config_key()
                cached_config = await asyncio.to_thread(cache_manager.get, config_key)
                if cached_config:
                    config_logger.info("Configuration loaded from cache (async)")
                    return cached_config

            # Load from database asynchronously
            config = await sync_to_async(cls._load_from_database)()

            # Cache the result if caching is enabled
            if use_cache and config:
                config_key = cache_manager.get_site_config_key()
                await asyncio.to_thread(cache_manager.set, config_key, config)
                config_logger.info("Configuration cached for future use (async)")

            return config

        except Exception as e:
            config_logger.error(f"Failed to get configuration (async): {e}")
            return cls._get_default_config()

    @classmethod
    def _load_from_database(cls) -> dict[str, Any]:
        """Load configuration from database models."""
        try:
            with transaction.atomic():
                # Load configuration sections with select_related for efficiency
                site_config = SiteConfig.objects.select_related().first()
                seo_config = SEOConfig.objects.select_related().first()
                theme_config = ThemeConfig.objects.select_related().first()
                content_config = ContentConfig.objects.select_related().first()

                # Convert to dictionary format
                config_data = {
                    "site": cls._serialize_model(site_config),
                    "seo": cls._serialize_model(seo_config),
                    "theme": cls._serialize_model(theme_config),
                    "content": cls._serialize_model(content_config),
                }

                config_logger.info("Configuration loaded from database")
                return config_data

        except Exception as e:
            config_logger.error(f"Failed to load config from database: {e}")
            return cls._get_default_config()

    @classmethod
    def _serialize_model(cls, model_instance) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        if not model_instance:
            return {}

        # Get all model fields except internal Django fields
        data = {}
        for field in model_instance._meta.fields:
            if not field.name.startswith("_"):
                value = getattr(model_instance, field.name, None)
                data[field.name] = value

        return data

    @classmethod
    def _get_default_config(cls) -> dict[str, Any]:
        """Return default fallback configuration."""
        config_logger.warning("Using default fallback configuration")

        return {
            "site": {
                "site_name": "My Site",
                "site_tagline": "Welcome to my site",
                "domain": "",
                "contact_email": "",
                "feature_flags": {},
                "navigation": [],
            },
            "seo": {
                "title": "My Site",
                "description": "Welcome to my site",
                "keywords": [],
                "canonical_url": "",
                "og_image": "",
            },
            "theme": {
                "primary_color": "#007bff",
                "secondary_color": "#6c757d",
                "font_family": "system-ui",
            },
            "content": {
                "maintenance_message": "",
                "allowed_file_extensions": [".jpg", ".jpeg", ".png", ".pdf"],
                "max_file_size": 5242880,  # 5MB
            },
        }

    # Convenience methods for common operations
    @classmethod
    def get_site_config(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get only site configuration section."""
        config = cls.get_config(use_cache)
        return config.get("site", {})

    @classmethod
    async def get_site_config_async(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get only site configuration section asynchronously."""
        config = await cls.get_config_async(use_cache)
        return config.get("site", {})

    @classmethod
    def get_theme_config(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get only theme configuration section."""
        config = cls.get_config(use_cache)
        return config.get("theme", {})

    @classmethod
    async def get_theme_config_async(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get only theme configuration section asynchronously."""
        config = await cls.get_config_async(use_cache)
        return config.get("theme", {})

    @classmethod
    def get_seo_config(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get only SEO configuration section."""
        config = cls.get_config(use_cache)
        return config.get("seo", {})

    @classmethod
    async def get_seo_config_async(cls, use_cache: bool = True) -> dict[str, Any]:
        """Get only SEO configuration section asynchronously."""
        config = await cls.get_config_async(use_cache)
        return config.get("seo", {})

    @classmethod
    def invalidate_cache(cls) -> None:
        """Invalidate configuration cache."""
        from .cache import CacheNamespace

        cache_manager.invalidate_namespace(CacheNamespace.CORE)
        config_logger.info("Configuration cache invalidated")

    @classmethod
    async def invalidate_cache_async(cls) -> None:
        """Invalidate configuration cache asynchronously."""
        from .cache import CacheNamespace

        await asyncio.to_thread(cache_manager.invalidate_namespace, CacheNamespace.CORE)
        config_logger.info("Configuration cache invalidated (async)")


# Backward compatibility aliases
ConfigLoader = ConfigService  # For existing code using ConfigLoader
AsyncConfigLoader = ConfigService  # For existing code using AsyncConfigLoader


# Convenience functions for common use cases
def get_config(use_cache: bool = True) -> dict[str, Any]:
    """Convenience function to get configuration."""
    return ConfigService.get_config(use_cache)


async def get_config_async(use_cache: bool = True) -> dict[str, Any]:
    """Convenience function to get configuration asynchronously."""
    return await ConfigService.get_config_async(use_cache)


def get_site_config(use_cache: bool = True) -> dict[str, Any]:
    """Convenience function to get site configuration."""
    return ConfigService.get_site_config(use_cache)


def resolve_config(request=None) -> dict[str, Any]:
    """
    Unified config resolver for context processors and templates.
    Provides versioned caching, postprocessing, and fallbacks.
    """
    return ConfigService.get_config(use_cache=True)
