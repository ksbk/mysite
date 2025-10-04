from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, TemplateView

from .models import Page


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


class PageListView(ListView):
    """List of published pages."""

    model = Page
    template_name = "pages/page_list.html"
    context_object_name = "pages"

    def get_queryset(self):  # noqa: D401
        """Filter to published pages and order by published_at desc."""
        return (
            Page.objects.filter(is_published=True)
            .order_by("-published_at", "-created_at")
            .only("id", "title", "slug", "published_at")
        )


class PageDetailView(DetailView):
    """Detail page fetched by slug."""

    model = Page
    template_name = "pages/page_detail.html"
    context_object_name = "page"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):  # noqa: D401
        """Fetch published page by slug or 404."""
        return get_object_or_404(Page, slug=self.kwargs["slug"], is_published=True)
