from django.utils.deprecation import MiddlewareMixin

__all__ = ["ConfigAuditMiddleware"]


class ConfigAuditMiddleware(MiddlewareMixin):
    """Middleware to track configuration changes and manage audit context."""

    def process_request(self, request):
        """Process incoming request and set up audit context."""
        # Set up any audit context needed for tracking configuration changes
        # For now, just return None to allow request processing to continue
        return None

    def process_response(self, request, response):
        """Process outgoing response and clean up audit context."""
        # Clean up any audit context or finalize audit logging
        # Return the response unchanged
        return response
