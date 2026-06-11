from django.urls import path

from .views.product_views import products, product_detail, all_products
from .views.computer_views import computers, computer_detail

urlpatterns = [
    # Legacy endpoints
    path("products/", computers, name="products"),
    path("products/<int:item_id>/", computer_detail, name="product-detail"),
    
    # New product type endpoints
    path("api/computers/", computers, name="computers"),
    path("api/computers/<int:item_id>/", computer_detail, name="computer-detail"),

    # Generic aggregate endpoint (must be before typed-products route)
    path("api/all-products/", all_products, name="all-products"),
    
    # Generic product endpoints
    path("api/<str:product_type>/", products, name="typed-products"),
    path("api/<str:product_type>/<int:item_id>/", product_detail, name="typed-product-detail"),
]
