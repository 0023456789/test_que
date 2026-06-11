from django.urls import path

from . import views

urlpatterns = [
    path("customers/register/", views.register_customer, name="register-customer"),
    path("customers/login/", views.login_customer, name="login-customer"),
    path("catalog/browse/", views.browse_catalog, name="browse-catalog"),
    path("catalog/search/", views.search_catalog, name="search-catalog"),
    path("cart/create/", views.create_cart, name="create-cart"),
    path("cart/current/", views.get_current_cart, name="current-cart"),
    path("cart/items/", views.add_cart_item, name="add-cart-item"),
    path("orders/recent/", views.recent_orders, name="recent-orders"),
    path("orders/purchase/", views.purchase_order, name="purchase-order"),
]
