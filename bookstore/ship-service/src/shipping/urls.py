from django.urls import path
from . import views
urlpatterns = [
    path("reserve/", views.reserve_shipment),
    path("order/<uuid:order_id>/", views.list_shipments_for_order),
    path("<uuid:shipment_id>/", views.get_shipment),
    path("<uuid:shipment_id>/confirm/", views.confirm_shipment),
    path("<uuid:shipment_id>/cancel/", views.cancel_shipment),
    path("<uuid:shipment_id>/status/", views.update_shipment_status),
]
