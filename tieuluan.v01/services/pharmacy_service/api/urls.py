from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicationViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register('medications', MedicationViewSet, basename='medication')
router.register('prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
]
