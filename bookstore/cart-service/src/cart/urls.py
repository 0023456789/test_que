from django.urls import path
from . import views

urlpatterns = [
    path("internal/create/", views.create_cart_internal),
    path("by-id/<uuid:cart_id>/", views.get_cart_by_id),
    path("<uuid:customer_id>/", views.get_cart),
    path("<uuid:customer_id>/add/", views.add_item),
    path("<uuid:customer_id>/items/<uuid:item_id>/", views.update_item),
    path("<uuid:customer_id>/clear/", views.clear_cart),
]
