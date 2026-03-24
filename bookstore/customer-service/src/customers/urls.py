from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_customers, name="list-customers"),
    path("create/", views.create_customer, name="create-customer"),
    path("me/", views.get_my_profile, name="my-profile"),
    path("<uuid:customer_id>/", views.get_customer, name="get-customer"),
    path("<uuid:customer_id>/update/", views.update_customer, name="update-customer"),
    path("<uuid:customer_id>/addresses/", views.addresses, name="addresses"),
]
