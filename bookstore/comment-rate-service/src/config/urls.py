from django.urls import path, include
from comments.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/reviews/", include("comments.urls")),
]
