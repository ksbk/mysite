"""
CSP (Content Security Policy) nonce middleware for Django.
"""

import secrets
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class CSPNonceMiddleware(MiddlewareMixin):
    """
    Middleware that generates a random nonce for Content Security Policy.

    The nonce is available in templates as {{ csp_nonce }} and can be used
    in CSP headers like: script-src 'self' 'nonce-{{ csp_nonce }}'
    """

    def process_request(self, request: HttpRequest) -> None:
        """Generate and attach a CSP nonce to the request."""
        # Generate a cryptographically secure random nonce
        nonce = secrets.token_urlsafe(32)

        # Attach to request for use in views and templates
        request.csp_nonce = nonce

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Add CSP nonce to the response context for template rendering.
        """
        # Make nonce available in template context
        if hasattr(request, "csp_nonce") and hasattr(response, "context_data"):
            if response.context_data is None:
                response.context_data = {}
            response.context_data["csp_nonce"] = request.csp_nonce

        return response


def get_csp_nonce(request: HttpRequest) -> str:
    """
    Get the CSP nonce from the request.

    Args:
        request: Django HTTP request object

    Returns:
        CSP nonce string or empty string if not available
    """
    return getattr(request, "csp_nonce", "")


def csp_nonce_context_processor(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor to make CSP nonce available in all templates.

    Add to TEMPLATES settings:
    'context_processors': [
        'apps.core.middleware.csp_nonce.csp_nonce_context_processor',
    ]
    """
    return {"csp_nonce": get_csp_nonce(request)}
