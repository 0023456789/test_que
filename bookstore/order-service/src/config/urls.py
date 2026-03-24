from django.urls import path, include
from orders.views import health_check

urlpatterns = [
    path("health/", health_check),
    path("api/orders/", include("orders.urls")),
]
