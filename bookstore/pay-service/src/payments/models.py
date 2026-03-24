import uuid
from django.db import models

class PaymentStatus(models.TextChoices):
    RESERVED   = "reserved",   "Reserved"
    CONFIRMED  = "confirmed",  "Confirmed"
    CANCELLED  = "cancelled",  "Cancelled"
    FAILED     = "failed",     "Failed"

class Payment(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id    = models.UUIDField(db_index=True)
    customer_id = models.UUIDField()
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    status      = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.RESERVED)
    method      = models.CharField(max_length=50, default="credit_card")
    transaction_ref = models.CharField(max_length=100, blank=True)
    failure_reason  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
