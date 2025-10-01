"""
Unified type definitions for configuration system.
Clean, simple types without over-engineering.
"""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class RequestConfig:
    """Configuration data for a specific request context."""

    config_data: dict[str, Any]
    user_id: str | None = None
    session_data: dict[str, Any] | None = None

    @classmethod
    def from_config_data(cls, config_data: dict[str, Any]) -> "RequestConfig":
        """Create RequestConfig from configuration dictionary."""
        return cls(config_data=config_data)

    def get_site_config(self) -> dict[str, Any]:
        """Get site configuration section."""
        return self.config_data.get("site", {})

    def get_seo_config(self) -> dict[str, Any]:
        """Get SEO configuration section."""
        return self.config_data.get("seo", {})

    def get_theme_config(self) -> dict[str, Any]:
        """Get theme configuration section."""
        return self.config_data.get("theme", {})

    def get_content_config(self) -> dict[str, Any]:
        """Get content configuration section."""
        return self.config_data.get("content", {})

    def get_feature_flags(self) -> dict[str, bool]:
        """Get feature flags from site configuration."""
        site_config = self.get_site_config()
        return site_config.get("feature_flags", {})

    @classmethod
    def create_empty(cls) -> "RequestConfig":
        """Create empty configuration for testing or fallback."""
        empty_config: dict[str, dict[str, Any]] = {
            "site": {},
            "seo": {},
            "theme": {},
            "content": {},
        }
        return cls(config_data=empty_config)


@dataclass(frozen=True)
class MaintenanceContext:
    """Context information for maintenance mode."""

    enabled: bool
    message: str
    estimated_duration: str | None = None
    contact_info: str | None = None

    @classmethod
    def from_config(cls, config_data: dict[str, Any]) -> "MaintenanceContext":
        """Create maintenance context from configuration data."""
        site_config = config_data.get("site", {})
        feature_flags = site_config.get("feature_flags", {})
        content_config = config_data.get("content", {})

        return cls(
            enabled=feature_flags.get("maintenance_mode", False),
            message=content_config.get("maintenance_message", "Site under maintenance"),
            estimated_duration=content_config.get("estimated_downtime"),
            contact_info=site_config.get("contact_email"),
        )


class ConfigProvider(Protocol):
    """Protocol for configuration providers - enables dependency injection."""

    def get_config(self, use_cache: bool = True) -> dict[str, Any]:
        """Get configuration synchronously."""
        ...

    async def get_config_async(self, use_cache: bool = True) -> dict[str, Any]:
        """Get configuration asynchronously."""
        ...


# Configuration validation helpers
def validate_config_structure(config_data: dict[str, Any]) -> bool:
    """Validate basic configuration structure."""
    required_sections = ["site", "seo", "theme", "content"]
    return all(section in config_data for section in required_sections)


def get_config_version(config_data: dict[str, Any]) -> str:
    """Extract configuration version if available."""
    return config_data.get("_meta", {}).get("version", "1.0")

