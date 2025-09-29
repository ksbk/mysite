"""
URL configuration for the pages app.
"""

from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    # Alternative using function-based view:
    # path('', views.home_page, name='home'),
]
