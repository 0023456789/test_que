from django.db import models

class Patient(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    phone = models.CharField(max_length=20)
    medical_history = models.TextField(blank=True, default="")
    allergies = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.full_name}"
