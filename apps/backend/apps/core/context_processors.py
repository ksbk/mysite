""""""

Context processors for core app functionality.Context processors for core app functionality.

Provides stable SITE, NAV, and FEATURES data for templates.Provides stable SITE, NAV, and FEATURES data for templates.

""""""



import secretsimport secrets

import timeimport time

from typing import Anyfrom typing import Any

from urllib.request import urlopen

from django.conf import settings

from django.http import HttpRequestfrom django.conf import settings

from django.http import HttpRequest



def site_context(request):from .config import ConfigService

    """

    Context processor that provides stable SITE, NAV, and FEATURES shape.# Vite dev server availability check cache

    Uses the unified loader for consistency._last_check = 0.0

    """_last_result = False

    try:

        from apps.core.config.loader import resolve_config

        site = resolve_config(request)def _check_vite_available(url: str, ttl: float = 10.0) -> bool:

        return {    """Check if Vite dev server is available with caching."""

            "SITE": site,    global _last_check, _last_result

            "NAV": site["content"]["navigation"],    now = time.monotonic()

            "FEATURES": site.get("feature_flags", {})

        }    if now - _last_check < ttl:

    except Exception:        return _last_result

        # Fallback configuration in case of errors

        return {    try:

            "SITE": {        # Cheap probe for HMR client (URL controlled via settings)

                "site": {        with urlopen(f"{url}/@vite/client", timeout=0.5):  # nosec B310

                    "site_name": "My Site",            _last_result = True

                    "site_tagline": "",    except OSError:

                    "domain": "",        _last_result = False

                    "contact_email": "",

                    "feature_flags": {},    _last_check = now

                    "navigation": [],    return _last_result

                },

                "seo": {

                    "title": "My Site",def site_context(request):

                    "description": "",    """

                    "keywords": [],    Context processor that provides stable SITE, NAV, and FEATURES shape.

                    "canonical_url": "",    Uses the unified loader for consistency.

                    "og_image": "",    """

                },    try:

                "theme": {        from apps.core.config.loader import resolve_config

                    "primary_color": "#007bff",        site = resolve_config(request)

                    "secondary_color": "#6c757d",        return {

                    "font_family": "system-ui",            "SITE": site,

                },            "NAV": site["content"]["navigation"],

                "content": {            "FEATURES": site.get("feature_flags", {})

                    "maintenance_message": "",        }

                    "allowed_file_extensions": [".jpg", ".jpeg", ".png", ".pdf"],    except Exception:

                    "max_file_size": 5242880,        # Fallback configuration in case of errors

                    "navigation": [],        return {

                },            "SITE": {

            },                "site": {

            "NAV": [],                    "site_name": "My Site",

            "FEATURES": {},                    "site_tagline": "",

        }                    "domain": "",

                    "contact_email": "",

                    "feature_flags": {},

def vite(request):                    "navigation": [],

    """                },

    Vite integration context processor.                "seo": {

    Provides Vite development server info and asset helpers.                    "title": "My Site",

    """                    "description": "",

    dev = getattr(settings, "DEBUG", False)                    "keywords": [],

    dev_url = "http://localhost:5173"                    "canonical_url": "",

                        "og_image": "",

    return {                },

        "VITE": {                "theme": {

            "debug": dev,                    "primary_color": "#007bff",

            "dev_server": dev_url if dev else None,                    "secondary_color": "#6c757d",

            "available": dev,  # Simplified for v1                    "font_family": "system-ui",

        }                },

    }                "content": {

                    "maintenance_message": "",

                    "allowed_file_extensions": [".jpg", ".jpeg", ".png", ".pdf"],

def security(request):                    "max_file_size": 5242880,

    """                },

    Security context processor.            },

    Provides CSP nonce and security headers.            "NAV": [],

    """            "FEATURES": {},

    # Generate nonce for CSP if not already set        }

    nonce = getattr(request, 'csp_nonce', None)

    if not nonce:

        nonce = secrets.token_urlsafe(16)def vite(request: HttpRequest) -> dict[str, Any]:

        request.csp_nonce = nonce    """Provide Vite development server information."""

        dev = bool(getattr(settings, "DEBUG", False))

    return {    dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")

        "CSP_NONCE": nonce,    available = _check_vite_available(dev_url) if dev else False

        "SECURITY": {

            "csp_nonce": nonce,    return {

            "secure_headers": True,        "DEBUG": dev,

        }        "VITE_DEV": dev,

    }        "VITE_DEV_SERVER_URL": dev_url,
        "VITE_DEV_AVAILABLE": available,
    }


def security(request: HttpRequest) -> dict[str, Any]:
    """Provide security-related context including CSP nonce."""
    nonce = ""
    if getattr(settings, "CSP_NONCE_enabled", False):
        # Generate a new nonce for each request
        nonce = secrets.token_urlsafe(16)
        # Store in request for CSP middleware to use
        setattr(request, "csp_nonce", nonce)

    return {
        "CSP_NONCE": nonce,
    }

                _last_result = False

        # Extract feature flags    _last_check = now

        feature_flags = config_dict.get("site", {}).get("feature_flags", {})    return _last_result



        return {

            "SITE": config_dict,  # Complete nested configurationdef vite(request):

            "NAV": navigation,    # Direct access to navigation    dev = bool(getattr(settings, "DEBUG", False))

            "FEATURES": feature_flags,  # Direct access to feature flags    dev_url = getattr(settings, "VITE_DEV_SERVER_URL", "http://localhost:5173")

        }    available = _check_vite_available(dev_url) if dev else False

    except Exception:    return {

        # Fallback configuration in case of errors        "DEBUG": dev,

        return {        "debug": dev,

            "SITE": {        "VITE_DEV": dev,

                "site": {        "VITE_DEV_SERVER_URL": dev_url,

                    "site_name": "My Site",        "VITE_DEV_AVAILABLE": available,

                    "site_tagline": "",    }

                    "domain": "",

                    "contact_email": "",

                    "feature_flags": {},def _load_site_json() -> dict:

                    "navigation": [],    path = getattr(settings, "SITE_SETTINGS_JSON", None)

                },    if not path:

                "seo": {        return {}

                    "meta_title": "",    try:

                    "meta_description": "",        with open(path, encoding="utf-8") as f:

                    "noindex": False,            return json.load(f)

                    "canonical_url": "",    except Exception:

                    "og_image": "",        return {}

                },

                "theme": {

                    "primary_color": "#007bff",def site(request):

                    "secondary_color": "#6c757d",    """Provide site customization settings with JSON fallback and DB override."""

                    "dark_mode_enabled": True,    defaults = {

                },        "site_name": getattr(settings, "SITE_NAME", "MySite"),

                "content": {        "site_author": "MySite Team",

                    "maintenance_mode": False,        "meta_description": "MySite - A modern Django + Vite application",

                    "comments_enabled": True,        "meta_keywords": "django,vite,web development",

                    "registration_enabled": True,        "og_description": "MySite - A modern Django + Vite application",

                },        "og_image": "",

            },        "twitter_site": "",

            "NAV": [],        "canonical_url": "",

            "FEATURES": {},        "noindex": False,

        }        "hero_title": "Welcome to MySite",
        "hero_subtitle": "A modern Django + Vite application.",
        "theme_color_light": "#ffffff",
        "theme_color_dark": "#0b0f19",
        "mask_icon_color": "",
        "analytics_domain": "",
        "cdn_domain": "",
        "json_ld": "",
    }

    data = {**defaults, **_load_site_json()}
    try:
        s = SiteSettings.get_solo()
        if s.site_name:
            data["site_name"] = s.site_name
        if s.meta_description:
            data["meta_description"] = s.meta_description
        if s.meta_keywords:
            data["meta_keywords"] = s.meta_keywords
        if s.og_image:
            data["og_image"] = s.og_image
    except Exception:  # nosec B110 - acceptable during initial migrations
        # On initial deploy before migrations, silently ignore DB lookup.
        # Narrowing exception types would require importing ORM errors; we
        # document the behavior and suppress Bandit as this is a benign path.
        data = data

    return {"SITE": data}


def security(request):
    """Provide security-related context including CSP nonce."""
    nonce = ""
    if getattr(settings, "CSP_NONCE_ENABLED", False):
        # Generate a new nonce for each request
        nonce = secrets.token_urlsafe(16)
        # Store in request for CSP middleware to use
        request.csp_nonce = nonce

    return {
        "csp_nonce": nonce,
    }
