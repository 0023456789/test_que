from django.urls import path, include
from books.views import health_check

urlpatterns = [
    path("health/", health_check),
    path("api/books/", include("books.urls")),
]
