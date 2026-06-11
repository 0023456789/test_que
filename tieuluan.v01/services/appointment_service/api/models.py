from django.db import models

class Appointment(models.Model):
    STATUS_BOOKED = 'BOOKED'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELED = 'CANCELED'

    STATUS_CHOICES = [
        (STATUS_BOOKED, 'Booked'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    appointment_time = models.DateTimeField()
    reason = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appt {self.id} - Patient {self.patient_id} - Doctor {self.doctor_id}"
