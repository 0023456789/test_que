from django.contrib import admin

from .models import Appointment, Encounter, Invoice, Patient, Prescription


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "date_of_birth", "created_at")
    search_fields = ("full_name", "phone")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor_name", "room", "start_time", "status")
    list_filter = ("status", "doctor_name")


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "appointment", "created_at")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "encounter", "created_at")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "encounter",
        "amount",
        "insurance_covered",
        "patient_payable",
        "status",
    )
    list_filter = ("status",)