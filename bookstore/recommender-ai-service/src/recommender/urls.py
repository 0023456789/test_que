from django.urls import path
from . import views
urlpatterns = [
    path("for-me/", views.for_customer),
    path("trending/", views.trending),
    path("similar/<uuid:book_id>/", views.similar_books),
]
