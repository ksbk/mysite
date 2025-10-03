from django.http import HttpResponse


def project_list(request):
    """Basic project list view."""
    return HttpResponse("Projects coming soon!")
