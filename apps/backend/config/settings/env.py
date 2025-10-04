# apps/backend/config/settings/env.py
"""
Environment settings for the project.

- Uses Pydantic v2 BaseSettings to read and validate configuration.
- Loads variables from **.env.local** (highest priority) then **.env**, then OS env.
- Keeps defaults sensible for local development while remaining production-ready.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, validated environment settings."""

    # ── Pydantic config ────────────────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),  # .env.local overrides .env
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="ignore",
        env_parse_none_str="",  # Don't parse empty strings as None
        env_nested_delimiter=None,  # Disable nested parsing to avoid JSON parsing
    )

    # ── Core ──────────────────────────────────────────────────────────────────
    DEBUG: bool = Field(default=False, description="Enable Django debug mode")
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("django-insecure-change-me-in-production"),
        description="Django secret key",
    )
    ALLOWED_HOSTS: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"],
        description="Allowed hosts list (comma-separated in env)",
    )

    # ── Frontend / Vite ───────────────────────────────────────────────────────
    VITE_DEV_SERVER_URL: str = Field(
        default="http://localhost:5173",
        description="Vite dev server base URL (no trailing slash after normalization)",
    )
    VITE_DEV: bool | None = Field(
        default=None,
        description="Force HMR assets (None=derive from DEBUG)",
    )
    VITE_MANIFEST_PATH: Path | None = Field(
        default=None,
        description="Absolute path to Vite manifest.json (derive in base.py when None)",
    )

    # ── Security ──────────────────────────────────────────────────────────────
    CSP_NONCE_ENABLED: bool = Field(
        default=False, description="Enable CSP nonce middleware"
    )
    SESSION_COOKIE_SECURE: bool = Field(default=False)
    CSRF_COOKIE_SECURE: bool = Field(default=False)
    SECURE_SSL_REDIRECT: bool = Field(
        default=False, description="Redirect HTTP to HTTPS"
    )
    SECURE_HSTS_SECONDS: int = Field(
        0, description="HSTS max-age in seconds (requires HTTPS + SSL redirect)"
    )
    CSRF_TRUSTED_ORIGINS_DEV: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Trusted origins appended only in DEBUG (set in base.py)",
    )

    # ── Performance ───────────────────────────────────────────────────────────
    ENABLE_COMPRESSION: bool = Field(
        default=True, description="Enable static compression"
    )
    ENABLE_WHITENOISE: bool = Field(
        default=False, description="Serve static via WhiteNoise"
    )

    # ── Feature flags ─────────────────────────────────────────────────────────
    ENABLE_DEBUG_TOOLBAR: bool = Field(
        default=False, description="Enable Django Debug Toolbar"
    )
    ENABLE_ADMIN: bool = Field(
        default=True, description="Enable Django admin interface"
    )
    ENABLE_API_DOCS: bool = Field(
        default=False, description="Enable API docs (DRF/OpenAPI)"
    )
    MAINTENANCE_MODE: bool = Field(default=False, description="Enable maintenance mode")

    # ── Environment/runtime ───────────────────────────────────────────────────
    APP_ENV: Literal["local", "dev", "staging", "prod"] = "local"

    # ── Email ─────────────────────────────────────────────────────────────────
    EMAIL_BACKEND: str = Field(
        "django.core.mail.backends.console.EmailBackend",
        description="Django email backend class",
    )
    EMAIL_HOST: str = Field(default="localhost", description="SMTP server hostname")
    EMAIL_PORT: int = Field(default=587, description="SMTP server port")
    EMAIL_HOST_USER: str = Field(default="", description="SMTP username")
    EMAIL_HOST_PASSWORD: SecretStr = Field(
        default=SecretStr(""), description="SMTP password"
    )
    EMAIL_USE_TLS: bool = Field(default=True, description="Use STARTTLS for SMTP")
    EMAIL_USE_SSL: bool = Field(default=False, description="Use SSL/TLS for SMTP")
    DEFAULT_FROM_EMAIL: str = Field(
        "noreply@mysite.local", description="Default sender email"
    )

    # ── Static/Media (URLs; filesystem paths derived in base.py) ──────────────
    STATIC_URL: str = "/static/"
    MEDIA_URL: str = "/media/"

    # ── Database ──────────────────────────────────────────────────────────────
    SQLITE_PATH: Path = Path("db.sqlite3")  # resolved relative to BASE_DIR in base.py
    DATABASE_URL: str | None = Field(
        default=None, description="Optional DB URL (e.g., postgres://...)"
    )

    # ── Cache ─────────────────────────────────────────────────────────────────
    CACHE_URL: str | None = Field(
        default=None, description="Cache URL (e.g., redis://, memcached://)"
    )
    CACHE_TIMEOUT: int = Field(
        default=300, description="Default cache timeout (seconds)"
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "plain"] = Field(
        default="plain", description="Log format: 'json' for prod, 'plain' for dev"
    )
    LOG_FILE_PATH: Path | None = Field(
        default=None, description="Optional log file path (created in base.py if set)"
    )

    # ── Validators ────────────────────────────────────────────────────────────
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def _split_hosts(cls, v) -> list[str]:
        if v is None:
            return ["localhost", "127.0.0.1"]
        if isinstance(v, list | tuple):
            return [str(h).strip() for h in v if str(h).strip()]
        return [h.strip() for h in str(v).split(",") if h.strip()]

    @field_validator("SECURE_HSTS_SECONDS")
    @classmethod
    def _hsts_bounds(cls, v: int) -> int:
        # Keep within 0..2 years; common values: 15552000 (180d), 31536000 (1y)
        max_seconds = 60 * 60 * 24 * 730
        return max(0, min(v, max_seconds))

    @field_validator("VITE_DEV_SERVER_URL")
    @classmethod
    def _normalize_vite_url(cls, v: str) -> str:
        # Normalize to no trailing slash to avoid double '//' when composing URLs
        return v.rstrip("/")

    @field_validator("STATIC_URL", "MEDIA_URL")
    @classmethod
    def _normalize_url_slashes(cls, v: str) -> str:
        # Ensure leading and trailing slash (e.g., '/static/', '/media/')
        v = "/" + v.strip("/")
        if not v.endswith("/"):
            v += "/"
        return v

    @field_validator("EMAIL_PORT")
    @classmethod
    def _email_port_bounds(cls, v: int) -> int:
        # Keep within valid TCP port range
        return max(1, min(v, 65535))

    @model_validator(mode="after")
    def _check_email_tls_ssl(self) -> Settings:
        # TLS and SSL are mutually exclusive in most setups
        if self.EMAIL_USE_TLS and self.EMAIL_USE_SSL:
            raise ValueError("EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be True")
        return self

    @model_validator(mode="after")
    def _check_hsts_consistency(self) -> Settings:
        # Warn if HSTS is enabled without SSL redirect (common prod pitfall)
        if self.SECURE_HSTS_SECONDS > 0 and not self.SECURE_SSL_REDIRECT:
            import warnings

            warnings.warn(
                "SECURE_HSTS_SECONDS > 0 but SECURE_SSL_REDIRECT is False. "
                "HSTS requires HTTPS; consider setting SECURE_SSL_REDIRECT=True.",
                UserWarning,
                stacklevel=3,
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance loaded from .env/.env.local and OS env.

    Example:
        from .env import get_settings
        env = get_settings()
        SECRET_KEY = env.SECRET_KEY.get_secret_value()
        DEBUG = env.DEBUG
    """
    return Settings()


__all__ = ["Settings", "get_settings"]
