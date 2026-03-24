from django.urls import path, include
from authentication import views

urlpatterns = [
    path("health/", views.health_check),
    path("api/auth/", include("authentication.urls")),
]
