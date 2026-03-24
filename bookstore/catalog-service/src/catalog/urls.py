from django.urls import path
from . import views
urlpatterns = [
    path("", views.browse),
    path("featured/", views.featured),
    path("categories/", views.categories),
]
