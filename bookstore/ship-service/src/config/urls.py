from django.urls import path, include
from shipping.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/shipping/", include("shipping.urls")),
]
