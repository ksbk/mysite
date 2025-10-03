# apps/contact/models.py
"""
Contact app models - This defines our database structure

Why we need models:
- Defines what data we store (name, email, message, etc.)
- Django ORM handles database operations automatically
- Provides data validation at the database level
- Makes it easy to query and manipulate data
"""

from django.db import models
from django.utils import timezone


class ContactMessage(models.Model):
    """
    Stores contact form submissions from users.

    Fields explained:
    - name: User's name (CharField = short text)
    - email: User's email (EmailField = validates email format)
    - subject: Message subject (optional, with default)
    - message: The actual message (TextField = long text)
    - created_at: When submitted (auto-populated)
    - is_read: Whether admin has read it (for management)
    """

    name = models.CharField(
        max_length=100, help_text="Full name of the person contacting us"
    )

    email = models.EmailField(help_text="Valid email address for response")

    subject = models.CharField(
        max_length=200, default="General Inquiry", help_text="Subject of the message"
    )

    message = models.TextField(help_text="The contact message content")

    created_at = models.DateTimeField(
        default=timezone.now, help_text="When this message was submitted"
    )

    is_read = models.BooleanField(
        default=False, help_text="Whether admin has read this message"
    )

    class Meta:
        """
        Meta options:
        - ordering: Shows newest messages first
        - verbose_name: How it appears in Django admin
        """

        ordering = ["-created_at"]  # Newest first
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        """How the object appears in admin interface and debugging"""
        return f"{self.name} - {self.subject} ({self.created_at.strftime("%Y-%m-%d")})"
