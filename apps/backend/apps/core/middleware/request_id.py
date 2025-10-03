"""Request ID middleware for tracking requests across logs."""

import uuid

from django.utils.deprecation import MiddlewareMixin

from apps.core.logging import set_request_id


class RequestIDMiddleware(MiddlewareMixin):
    """Middleware to add a unique request ID to each request for log correlation."""

    def process_request(self, request):
        """Add a unique request ID to the request and thread-local storage."""
        request_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        request.request_id = request_id
        set_request_id(request_id)
        return None

    def process_response(self, request, response):
        """Add request ID to response headers for debugging."""
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        return response
