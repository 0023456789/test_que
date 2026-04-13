from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'availability-templates', views.AvailabilityTemplateViewSet)
router.register(r'pitch-slots', views.PitchSlotViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check),
]
