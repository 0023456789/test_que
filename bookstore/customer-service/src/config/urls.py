from django.urls import path, include
from customers.views import health_check

urlpatterns = [
    path("health/", health_check),
    path("api/customers/", include("customers.urls")),
]
