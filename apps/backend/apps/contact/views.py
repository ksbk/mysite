# apps/contact/views.py
"""
Contact app views using Class-Based Views (CBV)

Why Class-Based Views:
- DRY (Don't Repeat Yourself) - built-in functionality
- Mixins for reusable behavior
- Better organization and inheritance
- Built-in HTTP method handling (GET, POST, etc.)
- Easy to extend and customize
"""

import json

from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView

from .forms import ContactForm
from .models import ContactMessage


class ContactFormView(CreateView):
    """
    Main contact form view using CreateView.

    Why CreateView:
    - Automatically handles GET (show form) and POST (process form)
    - Built-in form validation and error handling
    - Automatic model instance creation
    - Template rendering with context
    """

    model = ContactMessage
    form_class = ContactForm
    template_name = "contact/contact_form_simple.html"  # Proper contact form
    success_url = reverse_lazy("contact:success")

    def get_context_data(self, **kwargs):
        """
        Add extra context to template.

        Teaching: get_context_data is the CBV way to add template variables
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Contact Us",
            "page_description": "Get in touch with our team",
        })
        return context

    def form_valid(self, form):
        """
        Called when form validation passes.

        Teaching: This is where you add custom logic after successful validation
        """
        # Save the form (CreateView does this automatically, but we can add logic)
        response = super().form_valid(form)

        # Add success message
        messages.success(
            self.request,
            f"Thanks {form.cleaned_data["name"]}! "
            f"We received your message and will respond soon.",
        )

        # Optional: Send email notification to admin
        # self.send_admin_notification(form.cleaned_data)

        return response

    def form_invalid(self, form):
        """
        Called when form validation fails.

        Teaching: This is where you handle validation errors
        """
        messages.error(self.request, "Please correct the errors below and try again.")
        return super().form_invalid(form)


class ContactAPIView(FormView):
    """
    API endpoint for AJAX/TypeScript frontend submissions.

    Why separate API view:
    - Different response format (JSON vs HTML)
    - Different error handling
    - Can be used by mobile apps, SPAs, etc.
    - Cleaner separation of concerns
    """

    form_class = ContactForm

    @method_decorator(csrf_exempt)  # For API calls, we'll handle CSRF differently
    def dispatch(self, request, *args, **kwargs):
        """
        Teaching: dispatch() is called for every request
        We use it to add CORS headers and method validation
        """
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests with JSON data.

        Teaching: In CBV, you can override specific HTTP methods
        """
        try:
            # Parse JSON data
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            # Create form with data
            form = self.form_class(data)

            if form.is_valid():
                # Save the contact message
                contact_message = form.save()

                return JsonResponse({
                    "success": True,
                    "message": (
                        f"Thanks {contact_message.name}! We received your message."
                    ),
                    "data": {
                        "id": contact_message.id,
                        "created_at": contact_message.created_at.isoformat(),
                    },
                })
            else:
                # Return validation errors
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Please correct the errors below.",
                        "errors": form.errors,
                    },
                    status=400,
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON data."}, status=400
            )
        except Exception:
            return JsonResponse(
                {"success": False, "message": "An error occurred. Please try again."},
                status=500,
            )

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests - return form schema for frontend.

        Teaching: Useful for frontend to understand form structure
        """
        form = self.form_class()

        return JsonResponse({
            "fields": {
                field_name: {
                    "label": field.label,
                    "help_text": field.help_text,
                    "required": field.required,
                    "widget_type": field.widget.__class__.__name__,
                }
                for field_name, field in form.fields.items()
            }
        })


class ContactSuccessView(TemplateView):
    """
    Success page after form submission.

    Why TemplateView:
    - Simple template rendering
    - No form processing needed
    - Can add context if needed
    """

    template_name = "contact/contact_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Message Sent!",
            "page_description": "Thank you for contacting us.",
        })
        return context


# Optional: Admin view for managing contact messages
class ContactListView(TemplateView):
    """
    Simple admin view to list contact messages.

    Teaching: In real apps, you'd use Django Admin or create
    a proper admin interface with pagination, filtering, etc.
    """

    template_name = "contact/contact_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get recent messages (in real apps, add pagination)
        context["messages"] = ContactMessage.objects.all()[:50]
        context["page_title"] = "Contact Messages"

        return context
