from django.urls import path
from . import views

urlpatterns = [
    path("", views.books, name="books"),
    path("search/", views.search_books, name="search"),
    path("categories/", views.categories, name="categories"),
    path("authors/", views.authors, name="authors"),
    path("<uuid:book_id>/", views.book_detail, name="book-detail"),
    path("<uuid:book_id>/inventory/", views.update_inventory, name="inventory"),
    path("<uuid:book_id>/reserve/", views.reserve_stock, name="reserve"),
    path("<uuid:book_id>/release/", views.release_stock, name="release"),
    path("<uuid:book_id>/stats/", views.update_book_stats, name="stats"),
]
