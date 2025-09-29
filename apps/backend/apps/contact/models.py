from django.db import models


class ContactMessage(models.Model):
    """Store contact form submissions."""

    NEW = "new"
    READ = "read"
    ARCHIVED = "archived"
    STATUS_CHOICES = [
        (NEW, "New"),
        (READ, "Read"),
        (ARCHIVED, "Archived"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=NEW, db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.subject} ({self.email})"
