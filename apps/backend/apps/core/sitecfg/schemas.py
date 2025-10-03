# pyright: reportMissingImports=false
"""
Pydantic schemas for configuration models with validation and type safety.
"""

import re
from typing import Any

try:  # Optional dependency
    from pydantic import BaseModel, Field, HttpUrl, field_validator  # type: ignore
    from pydantic.config import ConfigDict  # type: ignore

    PydanticAvailable = True
except Exception:  # pragma: no cover - fallback when pydantic isn't installed
    PydanticAvailable = False

    class BaseModel:  # type: ignore
        """Minimal stub to allow import without pydantic."""

        def __init__(self, *args, **kwargs):  # noqa: D401
            pass

    def Field(*args, **kwargs):  # type: ignore
        return kwargs.get("default", None)

    class HttpUrl(str):  # type: ignore
        pass

    def field_validator(*_args, **_kwargs):  # type: ignore
        def decorator(fn):
            return fn

        return decorator

    # Minimal ConfigDict fallback
    class ConfigDict(dict):  # type: ignore
        pass


class NavItem(BaseModel):
    """Navigation item with optional nesting."""

    label: str = Field(
        default="Menu item",
        min_length=1,
        max_length=100,
        description="Menu item label",
    )
    url: str = Field(
        default="/",
        max_length=2048,
        description="Target URL; relative (internal) or absolute (external)",
    )
    active: bool = Field(default=False, description="Mark item as active")
    external: bool = Field(
        default=False, description="Whether the URL is external (http/https)"
    )
    children: list["NavItem"] = Field(
        default_factory=list, description="Nested child navigation items"
    )

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Navigation label cannot be empty")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v:
            raise ValueError("Navigation URL cannot be empty")
        # Allow anchors and relative paths
        if v.startswith("#") or v.startswith("/"):
            return v
        # Allow absolute http/https URLs
        if v.startswith("http://") or v.startswith("https://"):
            return v
        # Allow mailto/tel links
        if v.startswith("mailto:") or v.startswith("tel:"):
            return v
        raise ValueError(
            "Navigation URL must be absolute (http/https), a relative path, "
            "an anchor (#), or mailto/tel"
        )


# Resolve forward references for recursive children field
if PydanticAvailable:
    try:
        NavItem.model_rebuild()
    except Exception:
        pass


class SiteConfigSchema(BaseModel):
    """Site configuration schema with validation."""

    site_name: str = Field(
        default="My Site",
        min_length=1,
        max_length=120,
        description="Site name displayed in header and title tags",
    )
    site_tagline: str = Field(
        default="",
        max_length=200,
        description="Brief description or slogan for the site",
    )
    domain: str = Field(
        default="",
        max_length=255,
        description="Primary domain for the site (without protocol)",
    )
    contact_email: str = Field(
        default="",
        max_length=320,  # RFC 5321 maximum email length
        description="Main contact email address",
    )
    feature_flags: dict[str, bool] = Field(
        default_factory=dict,
        description="Feature flags for enabling/disabling functionality",
    )
    navigation: list[NavItem] = Field(
        default_factory=list, description="Main navigation menu items"
    )

    @field_validator("site_name")
    @classmethod
    def validate_site_name(cls, v: str) -> str:
        """Validate site name is not empty and contains valid characters."""
        if not v.strip():
            raise ValueError("Site name cannot be empty")
        if len(v.strip()) < 2:
            raise ValueError("Site name must be at least 2 characters long")
        return v.strip()

    @field_validator("contact_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format using regex."""
        if not v:
            return v

        # RFC 5322 compliant email regex (simplified)
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate domain format."""
        if not v:
            return v

        # Remove protocol if present
        if v.startswith(("http://", "https://")):
            raise ValueError("Domain should not include protocol (http/https)")

        # Basic domain validation
        domain_pattern = re.compile(
            r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.?[a-zA-Z0-9]+$"
        )
        if not domain_pattern.match(v):
            raise ValueError("Invalid domain format")
        return v.lower()

    @field_validator("feature_flags")
    @classmethod
    def validate_feature_flags(cls, v: dict[str, Any]) -> dict[str, bool]:
        """Validate feature flags are boolean values."""
        validated = {}
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError(f"Feature flag key must be string, got {type(key)}")
            if not isinstance(value, bool):
                raise ValueError(
                    f"Feature flag '{key}' must be boolean, got {type(value)}"
                )
            validated[key] = value
        return validated

    # Pydantic will validate NavItem instances recursively


class SEOConfigSchema(BaseModel):
    """SEO configuration schema with validation."""

    meta_title: str = Field(
        default="",
        max_length=60,
        description="Page title for search engines and browser tabs",
    )
    meta_description: str = Field(
        default="",
        max_length=160,
        description="Meta description for search engine results",
    )
    meta_keywords: str = Field(
        default="",
        max_length=255,
        description="Comma-separated keywords (legacy, not widely used)",
    )
    noindex: bool = Field(
        default=False, description="Prevent search engines from indexing this site"
    )
    canonical_url: HttpUrl | str = Field(
        default="", description="Canonical URL for this page/site"
    )
    og_image: HttpUrl | str = Field(
        default="", description="Open Graph image URL for social sharing"
    )
    google_site_verification: str = Field(
        default="",
        max_length=100,
        description="Google Search Console verification code",
    )
    google_analytics_id: str = Field(
        default="",
        max_length=50,
        description="Google Analytics tracking ID (GA4 or Universal)",
    )
    structured_data: dict[str, Any] = Field(
        default_factory=dict, description="JSON-LD structured data for rich snippets"
    )

    @field_validator("meta_title")
    @classmethod
    def validate_meta_title(cls, v: str) -> str:
        """Validate meta title length and content."""
        if len(v) > 60:
            raise ValueError(
                "Meta title should be 60 characters or less for optimal SEO"
            )
        return v.strip()

    @field_validator("meta_description")
    @classmethod
    def validate_meta_description(cls, v: str) -> str:
        """Validate meta description length and content."""
        if len(v) > 160:
            raise ValueError("Meta description should be 160 characters or less")
        return v.strip()

    @field_validator("meta_keywords")
    @classmethod
    def validate_meta_keywords(cls, v: str) -> str:
        """Validate and clean meta keywords."""
        if not v:
            return v

        # Clean up keywords: remove extra spaces, ensure proper comma separation
        keywords = [kw.strip() for kw in v.split(",") if kw.strip()]
        return ", ".join(keywords)

    @field_validator("canonical_url")
    @classmethod
    def validate_canonical_url(cls, v: str | HttpUrl) -> str:
        """Allow relative or absolute; loader will normalize to absolute."""
        if not v:
            return ""
        url_str = str(v).strip()
        # Accept absolute http(s) or site-relative
        if url_str.startswith(("http://", "https://", "/")):
            return url_str
        raise ValueError(
            "Canonical URL must be absolute http(s) or a site-relative path"
        )

    @field_validator("og_image")
    @classmethod
    def validate_og_image(cls, v: str | HttpUrl) -> str:
        """Allow relative or absolute; basic image extension sanity."""
        if not v:
            return ""
        url_str = str(v).strip()
        if not url_str.startswith(("http://", "https://", "/")):
            raise ValueError(
                "OG image URL must be absolute http(s) or a site-relative path"
            )
        valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")
        if not any(url_str.lower().endswith(ext) for ext in valid_extensions):
            # Soft warning (no raise) – some CDNs omit extensions
            pass
        return url_str

    @field_validator("google_analytics_id")
    @classmethod
    def validate_ga_id(cls, v: str) -> str:
        """Validate Google Analytics ID format."""
        if not v:
            return v

        # GA4 format: G-XXXXXXXXXX
        # Universal Analytics: UA-XXXXXXXX-X
        ga4_pattern = re.compile(r"^G-[A-Z0-9]{10}$")
        ua_pattern = re.compile(r"^UA-\d+-\d+$")

        if not (ga4_pattern.match(v) or ua_pattern.match(v)):
            raise ValueError(
                "Invalid Google Analytics ID. Expected formats: 'G-XXXXXXXXXX' (GA4) "
                "or 'UA-XXXXXXXX-X' (Universal Analytics)"
            )
        return v

    @field_validator("google_site_verification")
    @classmethod
    def validate_google_verification(cls, v: str) -> str:
        """Validate Google site verification code."""
        if not v:
            return v

        # Google verification codes are typically 43-44 characters,
        # alphanumeric plus hyphen (-) and underscore (_)
        if len(v) < 40 or len(v) > 50:
            raise ValueError("Google site verification code should be 40-50 characters")

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Google site verification code should only contain "
                "letters, numbers, hyphens, and underscores"
            )
        return v

    @field_validator("structured_data")
    @classmethod
    def validate_structured_data(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate structured data format."""
        if not v:
            return v

        # Basic validation for JSON-LD structured data
        if "@context" in v and not isinstance(v["@context"], str):
            raise ValueError("@context in structured data must be a string")

        if "@type" in v and not isinstance(v["@type"], str):
            raise ValueError("@type in structured data must be a string")

        return v


class ThemeConfigSchema(BaseModel):
    """Theme configuration schema with validation."""

    primary_color: str = Field(
        default="#007bff",
        description="Primary brand color in hex format (#rgb or #rrggbb)",
    )
    secondary_color: str = Field(
        default="#6c757d",
        description="Secondary brand color in hex format (#rgb or #rrggbb)",
    )
    favicon_url: str = Field(default="", description="URL to favicon image")
    logo_url: str = Field(default="", description="URL to site logo image")
    custom_css: str = Field(default="", description="Additional CSS styles to include")
    dark_mode_enabled: bool = Field(
        default=True, description="Enable dark mode theme toggle"
    )

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color as #rgb or #rrggbb and normalize to lowercase."""
        if not isinstance(v, str) or not v.startswith("#"):
            raise ValueError("Color must start with #")
        if len(v) not in (4, 7):
            raise ValueError("Color must be #rgb or #rrggbb")
        hex_part = v[1:]
        try:
            int(hex_part, 16)
        except ValueError as e:
            raise ValueError("Invalid hex color format") from e
        return v.lower()

    @field_validator("favicon_url", "logo_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        """Validate image URL format."""
        if not v:
            return v

        # Allow relative URLs or full URLs
        if v.startswith("/"):
            return v  # Relative URL

        if not v.startswith(("http://", "https://")):
            raise ValueError(
                "Image URL must be relative (start with /) or absolute (with protocol)"
            )

        # Check for common image extensions
        valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico")
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            allowed = ", ".join(valid_extensions)
            raise ValueError(f"Image URL should end with one of: {allowed}")

        return v

    @field_validator("custom_css")
    @classmethod
    def validate_custom_css(cls, v: str) -> str:
        """Basic validation for custom CSS."""
        if not v:
            return v

        # Basic sanity checks
        if "<script" in v.lower():
            raise ValueError("Custom CSS cannot contain script tags")

        if "javascript:" in v.lower():
            raise ValueError("Custom CSS cannot contain javascript: URLs")

        # Check for balanced braces
        open_braces = v.count("{")
        close_braces = v.count("}")
        if open_braces != close_braces:
            raise ValueError("Custom CSS has unbalanced braces")

        return v.strip()


class ContentConfigSchema(BaseModel):
    """Content configuration schema with validation."""

    maintenance_mode: bool = Field(
        default=False, description="Enable maintenance mode to show maintenance page"
    )
    maintenance_message: str = Field(
        default="We're currently performing maintenance. Please check back soon.",
        max_length=500,
        description="Message to display during maintenance mode",
    )
    comments_enabled: bool = Field(
        default=True, description="Allow comments on blog posts and pages"
    )
    registration_enabled: bool = Field(
        default=True, description="Allow new user registrations"
    )
    max_upload_size_mb: int = Field(
        default=10, gt=0, le=100, description="Maximum file upload size in megabytes"
    )
    allowed_file_extensions: list[str] = Field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".gif", ".pdf"],
        description="List of allowed file extensions for uploads",
    )

    @field_validator("maintenance_message")
    @classmethod
    def validate_maintenance_message(cls, v: str) -> str:
        """Validate maintenance message."""
        if not v.strip():
            raise ValueError("Maintenance message cannot be empty")

        # Basic HTML safety check
        dangerous_tags = ["<script", "<iframe", "<object", "<embed"]
        for tag in dangerous_tags:
            if tag in v.lower():
                raise ValueError(f"Maintenance message cannot contain {tag} tags")

        return v.strip()

    @field_validator("max_upload_size_mb")
    @classmethod
    def validate_upload_size(cls, v: int) -> int:
        """Validate upload size is within reasonable bounds."""
        if v <= 0:
            raise ValueError("Upload size must be greater than 0")

        if v > 100:
            raise ValueError("Upload size cannot exceed 100MB")

        # Warn about large sizes
        if v > 50:
            # This is just a validation note, not an error
            pass

        return v

    @field_validator("allowed_file_extensions")
    @classmethod
    def validate_extensions(cls, v: list[str]) -> list[str]:
        """Validate and normalize file extensions."""
        if not v:
            return v

        normalized = []
        for ext in v:
            if not isinstance(ext, str):
                raise ValueError("All file extensions must be strings")

            # Normalize extension
            ext = ext.strip().lower()
            if not ext.startswith("."):
                ext = f".{ext}"

            # Basic security check
            if len(ext) > 10:
                raise ValueError(f"File extension '{ext}' is too long")

            if not re.match(r"^\.[a-zA-Z0-9]+$", ext):
                raise ValueError(f"Invalid file extension format: {ext}")

            # Check for dangerous extensions
            dangerous_extensions = [
                ".exe",
                ".bat",
                ".cmd",
                ".com",
                ".pif",
                ".scr",
                ".vbs",
                ".js",
                ".jar",
                ".php",
                ".asp",
                ".aspx",
                ".jsp",
            ]
            if ext in dangerous_extensions:
                raise ValueError(
                    f"File extension '{ext}' is not allowed for security reasons"
                )

            normalized.append(ext)

        return list(set(normalized))  # Remove duplicates


class GlobalConfigSchema(BaseModel):
    """Composite configuration schema combining all config types."""

    site: SiteConfigSchema = Field(
        default_factory=SiteConfigSchema,
        description="Site-wide configuration and settings",
    )
    seo: SEOConfigSchema = Field(
        default_factory=SEOConfigSchema,
        description="Search engine optimization settings",
    )
    theme: ThemeConfigSchema = Field(
        default_factory=ThemeConfigSchema,
        description="Visual theme and branding configuration",
    )
    content: ContentConfigSchema = Field(
        default_factory=ContentConfigSchema,
        description="Content management and upload settings",
    )

    # Pydantic v2 configuration
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get a feature flag value with fallback."""
        return self.site.feature_flags.get(flag_name, default)

    def is_maintenance_mode(self) -> bool:
        """Check if site is in maintenance mode."""
        return self.content.maintenance_mode

    def get_upload_limit_bytes(self) -> int:
        """Get upload limit in bytes."""
        return self.content.max_upload_size_mb * 1024 * 1024


__all__ = [
    "PydanticAvailable",
    "SiteConfigSchema",
    "SEOConfigSchema",
    "ThemeConfigSchema",
    "ContentConfigSchema",
    "GlobalConfigSchema",
]
