from django.urls import path, include
from catalog.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/catalog/", include("catalog.urls")),
]
