from django.urls import path, include
from cart.views import health_check

urlpatterns = [
    path("health/", health_check),
    path("api/cart/", include("cart.urls")),
]
