from django.urls import path
from . import views
urlpatterns = [
    path("", views.manager_list),
    path("dashboard/", views.dashboard),
]
