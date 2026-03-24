from django.urls import path
from . import views
urlpatterns = [
    path("", views.staff_list),
    path("books/", views.manage_books),
    path("books/<uuid:book_id>/inventory/", views.adjust_inventory),
    path("inventory/audit/", views.inventory_audit),
]
