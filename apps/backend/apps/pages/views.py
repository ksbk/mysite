from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Homepage view displaying the main landing page."""

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Home",
            "meta_description": (
                "Welcome to MySite - a modern web application built with "
                "Django and Vite."
            ),
        })
        return context


# Function-based view alternative (can use either one)
def home_page(request):
    """Simple function-based homepage view."""
    context = {
        "page_title": "Home",
        "meta_description": (
            "Welcome to MySite - a modern web application built with Django and Vite."
        ),
    }
    return render(request, "pages/home.html", context)
