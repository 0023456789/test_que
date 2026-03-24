from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_orders),
    path("create/", views.create_order),
    path("<uuid:order_id>/", views.get_order),
    path("<uuid:order_id>/status/", views.get_order_status),
    path("<uuid:order_id>/cancel/", views.cancel_order),
]
