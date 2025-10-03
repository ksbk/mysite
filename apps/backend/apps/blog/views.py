from django.http import HttpResponse


def blog_list(request):
    """Basic blog list view."""
    return HttpResponse("Blog coming soon!")
