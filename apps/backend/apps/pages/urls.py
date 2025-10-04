"""
URL configuration for the pages app.
"""

from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("pages/", views.PageListView.as_view(), name="list"),
    path("pages/<slug:slug>/", views.PageDetailView.as_view(), name="detail"),
    # Alternative using function-based view:
    # path('', views.home_page, name='home'),
]
