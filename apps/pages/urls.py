"""URLs for pages app."""

from django.urls import path

from .views import contact, home, privacy, terms

urlpatterns = [
    path("", home, name="home"),
    path("privacy/", privacy, name="privacy"),
    path("terms/", terms, name="terms"),
    path("contact/", contact, name="contact"),
]
