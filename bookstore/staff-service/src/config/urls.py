from django.urls import path, include
from staff.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/staff/", include("staff.urls")),
]
