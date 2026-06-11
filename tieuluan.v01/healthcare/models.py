from django.db import models


class Patient(models.Model):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    allergies = models.TextField(blank=True, default="")
    history = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.full_name}"


class Appointment(models.Model):
    STATUS_BOOKED = "BOOKED"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELED = "CANCELED"

    STATUS_CHOICES = [
        (STATUS_BOOKED, "Booked"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor_name = models.CharField(max_length=255)
    room = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOOKED)
    reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"APM-{self.id} ({self.status})"


class Encounter(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="encounter")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="encounters")
    symptoms = models.TextField()
    diagnosis = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"ENC-{self.id}"


class LabTest(models.Model):
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="lab_tests")
    test_name = models.CharField(max_length=255)
    result = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"TEST-{self.id} ({self.test_name})"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="prescriptions")
    items = models.TextField(help_text="Medication and dosage instructions (JSON or plain text)")
    interaction_warnings = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"RX-{self.id}"


class Invoice(models.Model):
    STATUS_UNPAID = "UNPAID"
    STATUS_PAID = "PAID"

    STATUS_CHOICES = [
        (STATUS_UNPAID, "Unpaid"),
        (STATUS_PAID, "Paid"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="invoices")
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    insurance_covered = models.DecimalField(max_digits=12, decimal_places=2)
    patient_payable = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"INV-{self.id} ({self.status})"


class Notification(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"NOTIF-{self.id} for PATIENT-{self.patient.id}"