from django.urls import path, include
from payments.views import health_check
urlpatterns = [
    path("health/", health_check),
    path("api/payments/", include("payments.urls")),
]
