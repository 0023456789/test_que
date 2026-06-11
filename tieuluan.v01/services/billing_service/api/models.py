from django.db import models

class InsurancePolicy(models.Model):
    patient_id = models.IntegerField()
    provider_name = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100)
    coverage_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage covered by insurance (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Policy {self.policy_number} for Patient {self.patient_id}"

class Invoice(models.Model):
    STATUS_UNPAID = 'UNPAID'
    STATUS_PAID = 'PAID'

    STATUS_CHOICES = [
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PAID, 'Paid'),
    ]

    patient_id = models.IntegerField()
    encounter_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    amount_total = models.DecimalField(max_digits=12, decimal_places=2)
    insurance_covered = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    patient_payable = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} - Status: {self.status}"
