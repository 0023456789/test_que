from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, login, register

router = DefaultRouter()
router.register('appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('auth/login', login, name='login'),
    path('auth/register', register, name='register'),
    path('', include(router.urls)),
]
