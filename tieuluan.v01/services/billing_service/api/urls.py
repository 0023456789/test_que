from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsurancePolicyViewSet, InvoiceViewSet

router = DefaultRouter()
router.register('insurance', InsurancePolicyViewSet, basename='insurance')
router.register('invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
]
