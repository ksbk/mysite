"""
Enhanced configuration loader with audit logging and versioning.
"""
# isort: skip_file

import logging
from typing import Any
from urllib.parse import urljoin

from django.core.cache import cache
from django.db import transaction

from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig

logger = logging.getLogger(__name__)

__all__ = [
    "ConfigLoader",
    "get_config",
    "resolve_config",
    "invalidate_cache",
]

CACHE_KEY = "core:site_config:resolved:v1"
CACHE_TTL = 300  # seconds
CACHE_PREFIX = "config:"


class ConfigLoader:
    """Enhanced configuration loader with audit logging and versioning."""

    def __init__(self):
        self.schema_map = {
            "site": SiteConfig,
            "seo": SEOConfig,
            "theme": ThemeConfig,
            "content": ContentConfig,
        }

    def get_config(self, config_type: str = None) -> dict[str, Any]:
        """Get configuration from database with caching."""
        if config_type:
            return self._get_single_config(config_type)

        # Get all configurations
        all_configs = {}
        for conf_type in self.schema_map.keys():
            all_configs[conf_type] = self._get_single_config(conf_type)

        return all_configs

    def _get_single_config(self, config_type: str) -> dict[str, Any]:
        """Get a single configuration type."""
        cache_key = f"{CACHE_PREFIX}{config_type}"

        # Try cache first
        cached_config = self._get_cache(cache_key)
        if cached_config:
            return cached_config

        # Load from database
        try:
            model_class = self.schema_map.get(config_type)
            if not model_class:
                logger.warning(f"Unknown config type: {config_type}")
                return {}

            with transaction.atomic():
                config_instance = model_class.objects.first()
                config_data = self._model_to_dict(config_instance)

                # Validate/normalize when possible
                config_data = self._normalize_config(config_type, config_data)

                # Cache the configuration
                self._set_cache(cache_key, config_data, CACHE_TTL)

                return config_data

        except Exception as e:
            logger.exception(f"Failed to load {config_type} config: {e}")
            return self._get_default_config().get(config_type, {})

    def _normalize_config(self, config_type: str, config_data: dict) -> dict:
        """Normalize configuration data."""
        try:
            from .normalize import normalize_config_dict

            normalized = normalize_config_dict({config_type: config_data})
            return normalized.get(config_type, config_data)
        except Exception as e:
            logger.debug(f"Normalization failed for {config_type}: {e}")
            return config_data

    def _get_cache(self, key: str) -> Any:
        """Get value from cache with error handling."""
        try:
            return cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
            return None

    def _set_cache(self, key: str, value: Any, timeout: int) -> bool:
        """Set value in cache with error handling."""
        try:
            cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")
            return False

    def _delete_cache(self, key: str) -> bool:
        """Delete value from cache with error handling."""
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for {key}: {e}")
            return False

    def invalidate_cache(self, config_type: str = None) -> bool:
        """Invalidate configuration cache."""
        if config_type:
            cache_key = f"{CACHE_PREFIX}{config_type}"
            return self._delete_cache(cache_key)

        # Invalidate all config caches
        success = True
        for conf_type in self.schema_map.keys():
            cache_key = f"{CACHE_PREFIX}{conf_type}"
            success = self._delete_cache(cache_key) and success

        # Also invalidate legacy cache key
        success = self._delete_cache(CACHE_KEY) and success

        return success

    def warm_cache(self, config_type: str = None) -> bool:
        """Warm configuration cache."""
        try:
            if config_type:
                self._get_single_config(config_type)
            else:
                for conf_type in self.schema_map.keys():
                    self._get_single_config(conf_type)
            return True
        except Exception as e:
            logger.exception(f"Cache warming failed: {e}")
            return False

    def _model_to_dict(self, model_instance):
        """Convert model instance to dictionary."""
        if not model_instance:
            return {}

        data = {}
        for field in model_instance._meta.fields:
            value = getattr(model_instance, field.name, None)
            data[field.name] = value
        return data


# Legacy function for backward compatibility
def get_config() -> dict[str, Any]:
    """Get configuration from database with simple caching."""
    loader = ConfigLoader()
    return loader.get_config()


def resolve_config(request=None) -> dict[str, Any]:
    """Resolve config for templates and context processors."""
    cfg = get_config()

    # Post-process canonical_url based on request if missing
    if request is not None:
        site = cfg.setdefault("site", {})
        seo = cfg.setdefault("seo", {})
        base = getattr(request, "build_absolute_uri", lambda p: p)("/")
        canonical = seo.get("canonical_url") or site.get("domain")
        if canonical:
            # If canonical is a path or bare domain, join with base
            if canonical.startswith("http://") or canonical.startswith("https://"):
                seo["canonical_url"] = canonical
            else:
                seo["canonical_url"] = urljoin(base, canonical.lstrip("/"))
        else:
            seo["canonical_url"] = base

    # Ensure seo.og_image has a default
    seo = cfg.setdefault("seo", {})
    if not seo.get("og_image"):
        seo["og_image"] = "/static/images/og-default.png"
    # Normalize og_image to absolute when request is available and path is relative
    if request is not None and isinstance(seo.get("og_image"), str):
        og = seo["og_image"]
        if og.startswith("/"):
            base = getattr(request, "build_absolute_uri", lambda p: p)("/")
            seo["og_image"] = urljoin(base, og.lstrip("/"))

    return cfg


def invalidate_cache():
    """Invalidate the configuration cache."""
    loader = ConfigLoader()
    return loader.invalidate_cache()


def _model_to_dict(model_instance):
    """Convert model instance to dictionary."""
    loader = ConfigLoader()
    return loader._model_to_dict(model_instance)


def _get_default_config() -> dict[str, Any]:
    """Get safe default configuration."""
    return {
        "site": {
            "site_name": "My Site",
            "site_tagline": "",
            "domain": "",
            "contact_email": "",
            "feature_flags": {},
            "navigation": [],
        },
        "seo": {
            "title": "My Site",
            "description": "",
            "keywords": [],
            "canonical_url": "",
            "og_title": "",
            "og_description": "",
            "og_image": "",
        },
        "theme": {
            "primary_color": "#007bff",
            "secondary_color": "#6c757d",
            "font_family": "system-ui",
            "font_size_base": "16px",
        },
        "content": {
            "maintenance_message": "",
            "allowed_file_extensions": [".jpg", ".jpeg", ".png", ".pdf"],
            "max_file_size": 5242880,
        },
    }
