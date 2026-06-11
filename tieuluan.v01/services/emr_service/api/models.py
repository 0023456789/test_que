from django.db import models

class Encounter(models.Model):
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    appointment_id = models.IntegerField(null=True, blank=True)
    symptoms = models.TextField()
    diagnosis = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encounter {self.id} for Patient {self.patient_id}"

class LabTest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name='lab_tests')
    test_name = models.CharField(max_length=255)
    result = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LabTest {self.test_name} - {self.status}"
