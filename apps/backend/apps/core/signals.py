"""
Django signals for core app functionality.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .config.cache import cache_manager
from .models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=SiteConfig)
@receiver([post_save, post_delete], sender=SEOConfig)
@receiver([post_save, post_delete], sender=ThemeConfig)
@receiver([post_save, post_delete], sender=ContentConfig)
def _config_changed(**kwargs):
    """
    Idempotent cache invalidation when any config model changes.

    Handles both save and delete operations with unified logic.
    """
    from .config.cache import CacheNamespace

    cache_manager.invalidate_namespace(CacheNamespace.CORE)

    # Log for debugging (optional, can be removed for production)
    sender = kwargs.get("sender")
    instance = kwargs.get("instance")
    signal_name = "save" if kwargs.get("created") is not None else "delete"

    if sender and instance:
        logger.debug(
            f"Config cache invalidated: {sender.__name__} {signal_name} "
            f"(ID: {instance.pk})"
        )
    else:
        logger.debug("Config cache invalidated")
