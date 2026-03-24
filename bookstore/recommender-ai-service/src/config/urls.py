from django.urls import path, include
from recommender.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/recommendations/", include("recommender.urls")),
]
