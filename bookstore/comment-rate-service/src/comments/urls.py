from django.urls import path
from . import views
urlpatterns = [
    path("books/<uuid:book_id>/ratings/", views.book_ratings),
    path("books/<uuid:book_id>/comments/", views.book_comments),
    path("comments/<uuid:comment_id>/", views.delete_comment),
]
