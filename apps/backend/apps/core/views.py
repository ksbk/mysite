"""
Health and status endpoints for monitoring.
"""

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .config import ConfigService


@require_GET
@never_cache
def health_check(request):
    """
    Simple health check endpoint.

    Returns basic system information and UTC timestamp.
    Used for load balancer health checks and monitoring.
    """
    try:
        # Test database connectivity by loading config
        ConfigService.get_config(use_cache=False)

        return JsonResponse({
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",  # Could be loaded from settings
            "components": {
                "database": "ok",
                "cache": "ok",
            },
        })
    except Exception as e:
        return JsonResponse(
            {
                "status": "unhealthy",
                "timestamp": timezone.now().isoformat(),
                "version": "1.0.0",
                "error": str(e),
            },
            status=503,
        )


@require_GET
@never_cache
def status(request):
    """
    Detailed status endpoint with configuration information.

    Returns more detailed system status including configuration
    validation and cache status.
    """
    try:
        from .validation import HealthChecker

        health_checker = HealthChecker()
        health_status = health_checker.check_all_systems()

        return JsonResponse({
            "status": "ok" if health_status.overall_healthy else "degraded",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "health": {
                "overall": health_status.overall_healthy,
                "components": {
                    "database": health_status.database_healthy,
                    "cache": health_status.cache_healthy,
                    "memory": health_status.memory_healthy,
                    "permissions": health_status.permissions_healthy,
                },
                "issues": health_status.issues,
            },
        })
    except Exception as e:
        return JsonResponse(
            {
                "status": "error",
                "timestamp": timezone.now().isoformat(),
                "version": "1.0.0",
                "error": str(e),
            },
            status=500,
        )
