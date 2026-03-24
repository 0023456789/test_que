from django.urls import path
from . import views
urlpatterns = [
    path("reserve/", views.reserve_payment),
    path("order/<uuid:order_id>/", views.list_payments_for_order),
    path("<uuid:payment_id>/", views.get_payment),
    path("<uuid:payment_id>/confirm/", views.confirm_payment),
    path("<uuid:payment_id>/cancel/", views.cancel_payment),
]
