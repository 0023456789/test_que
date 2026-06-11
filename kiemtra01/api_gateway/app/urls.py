from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="gateway-home"),

    path("customer/browse/", views.customer_browse, name="gateway-customer-browse"),
    path("customer/login/", views.customer_login, name="gateway-customer-login"),
    path("customer/register/", views.customer_register, name="gateway-customer-register"),
    path("customer/cart/", views.customer_cart, name="gateway-customer-cart"),
    path("customer/checkout/", views.customer_checkout, name="gateway-customer-checkout"),

    path("staff/login/", views.staff_login, name="gateway-staff-login"),
    path("staff/register/", views.staff_register, name="gateway-staff-register"),
    path("staff/import/computer/", views.staff_import_computer, name="gateway-staff-import-computer"),
    path("staff/import/mobile/", views.staff_import_mobile, name="gateway-staff-import-mobile"),
    path("staff/update/", views.staff_update_item, name="gateway-staff-update-item"),

    path("products/<str:product_type>/<int:item_id>/", views.product_detail_page, name="gateway-product-detail"),
    path("shop/", views.shop, name="gateway-shop"),
    path("account/", views.account, name="gateway-account"),
    path("cart/", views.cart, name="gateway-cart"),
    path("staff/", views.staff, name="gateway-staff"),

    path("health/", views.health, name="gateway-health"),
    path("proxy/<str:service>/", views.proxy, name="gateway-proxy-root"),
    path("proxy/<str:service>/<path:path>", views.proxy, name="gateway-proxy"),
]
