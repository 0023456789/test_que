from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("validate/", views.validate_token, name="validate-token"),
    path("logout/", views.logout, name="logout"),
    path("me/", views.me, name="me"),
    path("users/", views.list_users, name="list-users"),
    path("users/<uuid:user_id>/", views.update_user, name="update-user"),
]
