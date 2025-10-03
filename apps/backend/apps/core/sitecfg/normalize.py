"""
Normalization helpers that adapt raw dicts and ORM models to Pydantic schemas.
Kept separate from schemas.py to avoid mixing concerns and to keep schemas pure.
"""

from __future__ import annotations

from typing import Any

from .schemas import (
    ContentConfigSchema,
    GlobalConfigSchema,
    SEOConfigSchema,
    SiteConfigSchema,
    ThemeConfigSchema,
)
from .schemas import PydanticAvailable as SchemasPydanticAvailable

# Re-expose availability flag for tests and callers
PydanticAvailable = SchemasPydanticAvailable

__all__ = [
    "PydanticAvailable",
    "normalize_config_dict",
    "to_global_config",
    "normalize_from_models",
]


def normalize_config_dict(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a raw config dict using Pydantic schemas.

    Accepts a partial dict with optional keys: "site", "seo", "theme", "content".
    Returns a normalized dict with only the provided sections validated and
    coerced. Unknown keys are preserved as-is for forwards compatibility.
    """
    if not PydanticAvailable:
        # Signal to caller (loader) that normalization isn't available
        raise ImportError("pydantic is not installed")

    normalized: dict[str, Any] = {}

    if "site" in raw and raw["site"] is not None:
        site_model = SiteConfigSchema.model_validate(raw["site"])  # type: ignore[arg-type]
        normalized["site"] = site_model.model_dump()

    if "seo" in raw and raw["seo"] is not None:
        seo_model = SEOConfigSchema.model_validate(raw["seo"])  # type: ignore[arg-type]
        normalized["seo"] = seo_model.model_dump()

    if "theme" in raw and raw["theme"] is not None:
        theme_model = ThemeConfigSchema.model_validate(raw["theme"])  # type: ignore[arg-type]
        normalized["theme"] = theme_model.model_dump()

    if "content" in raw and raw["content"] is not None:
        content_model = ContentConfigSchema.model_validate(raw["content"])  # type: ignore[arg-type]
        normalized["content"] = content_model.model_dump()

    # Preserve extra sections untouched
    for k, v in raw.items():
        if k not in normalized:
            normalized[k] = v

    return normalized


def normalize_from_models(
    site=None,
    seo=None,
    theme=None,
    content=None,
) -> dict[str, Any]:
    """Build and normalize a config dict from ORM model instances.

    Any argument can be None. Only provided sections are included in the result.
    """

    def model_to_dict(instance):
        if not instance:
            return None
        data: dict[str, Any] = {}
        for f in instance._meta.fields:  # type: ignore[attr-defined]
            data[f.name] = getattr(instance, f.name)
        return data

    raw: dict[str, Any] = {}
    if site is not None:
        raw["site"] = model_to_dict(site)
    if seo is not None:
        raw["seo"] = model_to_dict(seo)
    if theme is not None:
        raw["theme"] = model_to_dict(theme)
    if content is not None:
        raw["content"] = model_to_dict(content)

    return normalize_config_dict(raw)


def to_global_config(raw: dict[str, Any] | None = None) -> GlobalConfigSchema:
    """Create a GlobalConfigSchema from a partial raw dict.

    Missing sections will fall back to defaults provided by Pydantic models.
    """
    if not PydanticAvailable:
        raise ImportError("pydantic is not installed")
    raw = raw or {}
    parts: dict[str, Any] = {}
    if "site" in raw:
        parts["site"] = SiteConfigSchema.model_validate(raw["site"]).model_dump()
    if "seo" in raw:
        parts["seo"] = SEOConfigSchema.model_validate(raw["seo"]).model_dump()
    if "theme" in raw:
        parts["theme"] = ThemeConfigSchema.model_validate(raw["theme"]).model_dump()
    if "content" in raw:
        parts["content"] = ContentConfigSchema.model_validate(
            raw["content"]
        ).model_dump()

    return GlobalConfigSchema(**parts)
