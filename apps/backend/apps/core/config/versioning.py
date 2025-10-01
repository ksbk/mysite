"""
Configuration change detection and automatic cache invalidation.
Provides real-time monitoring and change notifications for configuration updates.
"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from ..models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from .cache import CacheNamespace, cache_manager
from .errors import config_logger


@dataclass(frozen=True)
class ConfigChange:
    """Represents a configuration change event."""

    model_name: str
    instance_id: int | None
    action: str  # 'created', 'updated', 'deleted'
    timestamp: datetime
    changed_fields: list[str]

    def __str__(self) -> str:
        return f"{self.model_name} {self.action} at {self.timestamp}"


class ConfigChangeTracker:
    """
    Tracks configuration changes and manages cache invalidation.
    Provides hooks for real-time updates and change notifications.
    """

    def __init__(self):
        self.change_handlers: list[Callable[[ConfigChange], None]] = []
        self.async_change_handlers: list[Callable[[ConfigChange], Awaitable[None]]] = []
        self.change_history: list[ConfigChange] = []
        self.max_history_size = 100

    def register_change_handler(self, handler: Callable[[ConfigChange], None]) -> None:
        """Register a synchronous change handler."""
        self.change_handlers.append(handler)
        config_logger.info(f"Registered change handler: {handler.__name__}")

    def register_async_change_handler(
        self, handler: Callable[[ConfigChange], Awaitable[None]]
    ) -> None:
        """Register an asynchronous change handler."""
        self.async_change_handlers.append(handler)
        config_logger.info(f"Registered async change handler: {handler.__name__}")

    def unregister_sync_handler(self, handler: Callable[[ConfigChange], None]) -> None:
        """Unregister a synchronous change handler."""
        if handler in self.change_handlers:
            self.change_handlers.remove(handler)
            config_logger.info(f"Unregistered sync handler: {handler.__name__}")

    def unregister_async_handler(
        self, handler: Callable[[ConfigChange], Awaitable[None]]
    ) -> None:
        """Unregister an asynchronous change handler."""
        if handler in self.async_change_handlers:
            self.async_change_handlers.remove(handler)
            config_logger.info(f"Unregistered async handler: {handler.__name__}")

    def record_change(
        self,
        model_name: str,
        instance_id: int | None,
        action: str,
        changed_fields: list[str] | None = None,
    ) -> ConfigChange:
        """Record a configuration change and notify handlers."""
        change = ConfigChange(
            model_name=model_name,
            instance_id=instance_id,
            action=action,
            timestamp=timezone.now(),
            changed_fields=changed_fields or [],
        )

        # Add to history with size limit
        self.change_history.append(change)
        if len(self.change_history) > self.max_history_size:
            self.change_history.pop(0)

        config_logger.info(f"Configuration change recorded: {change}")

        # Notify synchronous handlers
        for handler in self.change_handlers:
            try:
                handler(change)
            except Exception as e:
                config_logger.error(f"Error in change handler {handler.__name__}: {e}")

        # Notify asynchronous handlers
        if self.async_change_handlers:
            asyncio.create_task(self._notify_async_handlers(change))

        return change

    async def _notify_async_handlers(self, change: ConfigChange) -> None:
        """Notify asynchronous change handlers."""
        for handler in self.async_change_handlers:
            try:
                await handler(change)
            except Exception as e:
                config_logger.error(
                    f"Error in async change handler {handler.__name__}: {e}"
                )

    def get_recent_changes(self, limit: int = 10) -> list[ConfigChange]:
        """Get recent configuration changes."""
        return self.change_history[-limit:]

    def get_changes_since(self, since: datetime) -> list[ConfigChange]:
        """Get configuration changes since a specific time."""
        return [change for change in self.change_history if change.timestamp >= since]

    def clear_history(self) -> None:
        """Clear change history."""
        self.change_history.clear()
        config_logger.info("Change history cleared")


class CacheInvalidator:
    """
    Handles automatic cache invalidation based on configuration changes.
    Provides intelligent invalidation strategies.
    """

    def __init__(self, change_tracker: ConfigChangeTracker):
        self.change_tracker = change_tracker
        # Register cache invalidation handlers
        self.change_tracker.register_change_handler(self.invalidate_cache_sync)
        self.change_tracker.register_async_change_handler(self.invalidate_cache_async)

    def invalidate_cache_sync(self, change: ConfigChange) -> None:
        """Synchronous cache invalidation handler."""
        try:
            # Invalidate relevant cache namespace
            config_models = ["SiteConfig", "SEOConfig", "ThemeConfig", "ContentConfig"]
            if change.model_name in config_models:
                results = cache_manager.invalidate_namespace(CacheNamespace.CORE)
                config_logger.info(
                    f"Cache invalidated for {change.model_name} change",
                    invalidated_keys=len([r for r in results if r]),
                )

                # Also invalidate feature flags cache if site config changed
                if change.model_name == "SiteConfig":
                    cache_manager.invalidate_namespace(CacheNamespace.FEATURE_FLAGS)
                    config_logger.info("Feature flags cache invalidated")

        except Exception as e:
            config_logger.error(f"Failed to invalidate cache synchronously: {e}")

    async def invalidate_cache_async(self, change: ConfigChange) -> None:
        """Asynchronous cache invalidation handler."""
        try:
            # Run cache invalidation in thread to avoid blocking
            await asyncio.to_thread(self.invalidate_cache_sync, change)

            # Additional async-specific cache operations could go here
            config_logger.info(f"Async cache invalidation completed for {change}")

        except Exception as e:
            config_logger.error(f"Failed to invalidate cache asynchronously: {e}")

    def invalidate_all_config_caches(self) -> None:
        """Invalidate all configuration-related caches."""
        try:
            # Invalidate all configuration namespaces
            namespaces = [
                CacheNamespace.CORE,
                CacheNamespace.CONFIG,
                CacheNamespace.FEATURE_FLAGS,
                CacheNamespace.SITE_DATA,
            ]

            total_invalidated = 0
            for namespace in namespaces:
                results = cache_manager.invalidate_namespace(namespace)
                total_invalidated += len([r for r in results if r])

            config_logger.info(
                "All configuration caches invalidated",
                total_keys_invalidated=total_invalidated,
            )

        except Exception as e:
            config_logger.error(f"Failed to invalidate all caches: {e}")


# Global change tracker and cache invalidator
change_tracker = ConfigChangeTracker()
cache_invalidator = CacheInvalidator(change_tracker)


# Django signal handlers for automatic change detection
@receiver(post_save, sender=SiteConfig)
def handle_site_config_save(sender, instance, created, **kwargs):
    """Handle SiteConfig save events."""
    action = "created" if created else "updated"

    # Get changed fields if this is an update
    changed_fields = []
    if not created and hasattr(instance, "_dirty_fields"):
        changed_fields = list(instance._dirty_fields)

    change_tracker.record_change(
        model_name="SiteConfig",
        instance_id=instance.pk,
        action=action,
        changed_fields=changed_fields,
    )


@receiver(post_delete, sender=SiteConfig)
def handle_site_config_delete(sender, instance, **kwargs):
    """Handle SiteConfig delete events."""
    change_tracker.record_change(
        model_name="SiteConfig",
        instance_id=instance.pk,
        action="deleted",
    )


@receiver(post_save, sender=SEOConfig)
def handle_seo_config_save(sender, instance, created, **kwargs):
    """Handle SEOConfig save events."""
    action = "created" if created else "updated"

    changed_fields = []
    if not created and hasattr(instance, "_dirty_fields"):
        changed_fields = list(instance._dirty_fields)

    change_tracker.record_change(
        model_name="SEOConfig",
        instance_id=instance.pk,
        action=action,
        changed_fields=changed_fields,
    )


@receiver(post_delete, sender=SEOConfig)
def handle_seo_config_delete(sender, instance, **kwargs):
    """Handle SEOConfig delete events."""
    change_tracker.record_change(
        model_name="SEOConfig",
        instance_id=instance.pk,
        action="deleted",
    )


@receiver(post_save, sender=ThemeConfig)
def handle_theme_config_save(sender, instance, created, **kwargs):
    """Handle ThemeConfig save events."""
    action = "created" if created else "updated"

    changed_fields = []
    if not created and hasattr(instance, "_dirty_fields"):
        changed_fields = list(instance._dirty_fields)

    change_tracker.record_change(
        model_name="ThemeConfig",
        instance_id=instance.pk,
        action=action,
        changed_fields=changed_fields,
    )


@receiver(post_delete, sender=ThemeConfig)
def handle_theme_config_delete(sender, instance, **kwargs):
    """Handle ThemeConfig delete events."""
    change_tracker.record_change(
        model_name="ThemeConfig",
        instance_id=instance.pk,
        action="deleted",
    )


@receiver(post_save, sender=ContentConfig)
def handle_content_config_save(sender, instance, created, **kwargs):
    """Handle ContentConfig save events."""
    action = "created" if created else "updated"

    changed_fields = []
    if not created and hasattr(instance, "_dirty_fields"):
        changed_fields = list(instance._dirty_fields)

    change_tracker.record_change(
        model_name="ContentConfig",
        instance_id=instance.pk,
        action=action,
        changed_fields=changed_fields,
    )


@receiver(post_delete, sender=ContentConfig)
def handle_content_config_delete(sender, instance, **kwargs):
    """Handle ContentConfig delete events."""
    change_tracker.record_change(
        model_name="ContentConfig",
        instance_id=instance.pk,
        action="deleted",
    )


# Convenience functions for manual cache management
def invalidate_config_cache() -> None:
    """Manually invalidate configuration cache."""
    cache_invalidator.invalidate_all_config_caches()


def get_recent_config_changes(limit: int = 10) -> list[ConfigChange]:
    """Get recent configuration changes."""
    return change_tracker.get_recent_changes(limit)


def register_config_change_handler(handler: Callable[[ConfigChange], None]) -> None:
    """Register a configuration change handler."""
    change_tracker.register_change_handler(handler)
