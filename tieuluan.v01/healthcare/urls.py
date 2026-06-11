from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .auth import login, register
from .views import (
    AppointmentViewSet,
    EncounterViewSet,
    InvoiceViewSet,
    LabTestViewSet,
    NotificationViewSet,
    PatientViewSet,
    PrescriptionViewSet,
)

router = DefaultRouter()
router.register("patients", PatientViewSet, basename="patient")
router.register("appointments", AppointmentViewSet, basename="appointment")
router.register("encounters", EncounterViewSet, basename="encounter")
router.register("prescriptions", PrescriptionViewSet, basename="prescription")
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("lab_tests", LabTestViewSet, basename="lab_test")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("auth/register/", register, name="register"),
    path("auth/login/", login, name="login"),
    path("", include(router.urls)),
]