from django.urls import path, include
from managers.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/managers/", include("managers.urls")),
]
