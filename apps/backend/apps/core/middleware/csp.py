"""
Content Security Policy middleware with nonce generation.
"""

import secrets

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class CSPNonceMiddleware(MiddlewareMixin):
    """
    Middleware to generate CSP nonces for secure inline scripts.

    Generates a unique nonce per request and adds it to both the
    request object and the CSP header.
    """

    def process_request(self, request: HttpRequest) -> None:
        """Generate and store CSP nonce on the request."""
        # Generate a cryptographically secure nonce
        nonce = secrets.token_urlsafe(16)

        # Store nonce on request for template access
        request.csp_nonce = nonce  # type: ignore

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Add CSP header with nonce to response."""
        # Only add CSP if enabled in settings
        if not getattr(settings, "CSP_ENABLED", False):
            return response

        # Get nonce from request
        nonce = getattr(request, "csp_nonce", "")

        if not nonce:
            return response

        # Build CSP policy
        csp_policy = self._build_csp_policy(nonce)

        # Determine header name based on settings
        report_only = getattr(settings, "CSP_REPORT_ONLY", True)
        header_name = (
            "Content-Security-Policy-Report-Only"
            if report_only
            else "Content-Security-Policy"
        )

        response[header_name] = csp_policy
        return response

    def _build_csp_policy(self, nonce: str) -> str:
        """Build CSP policy string with nonce."""
        # Base policy - strict by default
        policy_parts = []

        # Default source
        default_src = getattr(settings, "CSP_DEFAULT_SRC", "'self'")
        policy_parts.append(f"default-src {default_src}")

        # Script sources with nonce
        script_src = getattr(
            settings,
            "CSP_SCRIPT_SRC",
            "'self' 'unsafe-eval'",  # unsafe-eval needed for Vite in dev
        )
        policy_parts.append(f"script-src {script_src} 'nonce-{nonce}'")

        # Style sources with nonce
        style_src = getattr(settings, "CSP_STYLE_SRC", "'self' 'unsafe-inline'")
        policy_parts.append(f"style-src {style_src} 'nonce-{nonce}'")

        # Image sources
        img_src = getattr(settings, "CSP_IMG_SRC", "'self' data: https:")
        policy_parts.append(f"img-src {img_src}")

        # Font sources
        font_src = getattr(settings, "CSP_FONT_SRC", "'self'")
        policy_parts.append(f"font-src {font_src}")

        # Connect sources (for API calls)
        connect_src = getattr(settings, "CSP_CONNECT_SRC", "'self'")

        # Add Vite dev server if in debug mode
        if getattr(settings, "DEBUG", False):
            vite_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")
            connect_src += f" {vite_url}"

        policy_parts.append(f"connect-src {connect_src}")

        # Frame sources
        frame_src = getattr(settings, "CSP_FRAME_SRC", "'none'")
        policy_parts.append(f"frame-src {frame_src}")

        # Object sources
        object_src = getattr(settings, "CSP_OBJECT_SRC", "'none'")
        policy_parts.append(f"object-src {object_src}")

        # Base URI
        base_uri = getattr(settings, "CSP_BASE_URI", "'self'")
        policy_parts.append(f"base-uri {base_uri}")

        # Report URI if configured
        report_uri = getattr(settings, "CSP_REPORT_URI", None)
        if report_uri:
            policy_parts.append(f"report-uri {report_uri}")

        return "; ".join(policy_parts)
