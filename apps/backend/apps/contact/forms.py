# apps/contact/forms.py
"""
Contact app forms - This handles data validation and form rendering

Why we need forms:
- Server-side validation (security - never trust client data)
- Automatic HTML form generation (if needed)
- CSRF protection integration
- Consistent validation logic
- Error message handling
"""

from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Django ModelForm automatically creates form fields based on the model.

    Benefits:
    - Automatically matches model fields
    - Built-in validation from model constraints
    - Easy to maintain (changes to model auto-update form)
    - Handles saving to database
    """

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]

        # Custom HTML attributes for better UX
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Your full name",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "your.email@example.com",
                    "required": True,
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "What is this about?",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": "Tell us what you need help with...",
                    "rows": 5,
                    "required": True,
                }
            ),
        }

    def clean_message(self):
        """
        Custom validation for message field.

        Why custom validation:
        - Business rules (minimum length, content filtering)
        - Better user experience with specific error messages
        - Additional security checks
        """
        message = self.cleaned_data.get("message")

        if message and len(message.strip()) < 10:
            raise forms.ValidationError(
                "Please provide a more detailed message (at least 10 characters)."
            )

        return message

    def clean_email(self):
        """
        Custom email validation beyond basic format checking.
        """
        email = self.cleaned_data.get("email")

        # Basic domain blacklist (extend as needed)
        blocked_domains = ["spam.com", "fake.com"]
        if email:
            domain = email.split("@")[1].lower()
            if domain in blocked_domains:
                raise forms.ValidationError("Please use a different email provider.")

        return email
