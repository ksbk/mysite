"""Basic page views."""

from django.shortcuts import render


def home(request):
    """Home page view."""
    return render(request, "pages/home.html")


def privacy(request):
    """Privacy policy page."""
    return render(request, "pages/privacy.html")


def terms(request):
    """Terms of service page."""
    return render(request, "pages/terms.html")


def contact(request):
    """Contact page."""
    return render(request, "pages/contact.html")
