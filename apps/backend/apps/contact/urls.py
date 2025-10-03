"""
URLs for contact app.

Teaching: URL patterns map URLs to views
- app_name creates namespace (prevents name conflicts)
- name parameter allows reverse URL lookup
- path() connects URL patterns to view classes
"""

from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    # Main contact form (GET = show form, POST = process form)
    path("", views.ContactFormView.as_view(), name="form"),
    # API endpoint for AJAX/TypeScript calls
    path("api/", views.ContactAPIView.as_view(), name="api"),
    # Success page after form submission
    path("success/", views.ContactSuccessView.as_view(), name="success"),
    # Optional: Admin view for listing messages
    path("messages/", views.ContactListView.as_view(), name="list"),
]
