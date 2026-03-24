from django.urls import path, re_path
from gateway.views import gateway, health_check, aggregate_health, list_routes

urlpatterns = [
    path("health/",           health_check),
    path("gateway/health/",   aggregate_health),
    path("gateway/routes/",   list_routes),
    re_path(r"^(?P<path>.*)$", gateway),
]
