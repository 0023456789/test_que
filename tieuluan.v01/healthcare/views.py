from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Appointment, Encounter, Invoice, LabTest, Notification, Patient, Prescription
from .serializers import (
    AppointmentSerializer,
    EncounterSerializer,
    InvoiceSerializer,
    LabTestSerializer,
    NotificationSerializer,
    PatientSerializer,
    PrescriptionSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("-start_time")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["patch"], url_path="reschedule")
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        new_time = request.data.get("start_time")
        reason = request.data.get("reason")
        
        if new_time:
            appointment.start_time = new_time
        if reason:
            appointment.reason = reason
            
        appointment.save(update_fields=["start_time", "reason"])
        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all().order_by("-created_at")
    serializer_class = EncounterSerializer
    permission_classes = [IsAuthenticated]


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all().order_by("-created_at")
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by("-created_at")
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = Invoice.STATUS_PAID
        invoice.save(update_fields=["status"])
        serializer = self.get_serializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all().order_by("-created_at")
    serializer_class = LabTestSerializer
    permission_classes = [IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="read")
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)