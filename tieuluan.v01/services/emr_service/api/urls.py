from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EncounterViewSet, LabTestViewSet

router = DefaultRouter()
router.register('encounters', EncounterViewSet, basename='encounter')
router.register('lab-tests', LabTestViewSet, basename='lab_test')

urlpatterns = [
    path('', include(router.urls)),
]
