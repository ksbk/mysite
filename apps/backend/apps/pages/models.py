from __future__ import annotations

from django.db import models
from django.urls import reverse


class Page(models.Model):
    """Simple CMS-like page model."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        help_text="URL-friendly identifier",
    )
    body = models.TextField(blank=True)

    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published", "published_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.title

    def get_absolute_url(self) -> str:
        """Return the canonical URL for this page."""
        return reverse("pages:detail", kwargs={"slug": self.slug})
