from django.db import models

class Medication(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    # For basic interaction checks (e.g. comma separated strings of incompatible medication names)
    incompatible_with = models.TextField(blank=True, default="", help_text="Comma-separated medication names")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Prescription(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_DISPENSED = 'DISPENSED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_DISPENSED, 'Dispensed'),
    ]

    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    encounter_id = models.IntegerField(null=True, blank=True)
    medications = models.ManyToManyField(Medication, related_name='prescriptions')
    dosage_instructions = models.TextField(blank=True, default="")
    interaction_warnings = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
