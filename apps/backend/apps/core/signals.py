"""
Django signals for core app functionality.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ContentConfig, SEOConfig, SiteConfig, ThemeConfig
from .sitecfg.loader import invalidate_cache

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=SiteConfig)
@receiver([post_save, post_delete], sender=SEOConfig)
@receiver([post_save, post_delete], sender=ThemeConfig)
@receiver([post_save, post_delete], sender=ContentConfig)
def config_changed(**kwargs):
    """
    Invalidate cache when any config model changes.
    """
    invalidate_cache()

    # Log for debugging
    sender = kwargs.get("sender")
    instance = kwargs.get("instance")
    signal_name = "save" if kwargs.get("created") is not None else "delete"

    if sender and instance:
        logger.debug(
            f"Config cache invalidated: {sender.__name__} {signal_name} (ID: {instance.pk})"
        )
    else:
        logger.debug("Config cache invalidated")
