import uuid
from django.db import models

class ShipmentStatus(models.TextChoices):
    RESERVED   = "reserved",   "Reserved"
    CONFIRMED  = "confirmed",  "Confirmed"
    SHIPPED    = "shipped",    "Shipped"
    DELIVERED  = "delivered",  "Delivered"
    CANCELLED  = "cancelled",  "Cancelled"

class Shipment(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id    = models.UUIDField(db_index=True)
    customer_id = models.UUIDField()
    status      = models.CharField(max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.RESERVED)
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier     = models.CharField(max_length=100, default="Standard Shipping")
    # Address snapshot
    street      = models.CharField(max_length=255, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    state       = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country     = models.CharField(max_length=100, default="US")
    estimated_delivery = models.DateField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipments"

class ShipmentItem(models.Model):
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="items")
    book_id  = models.UUIDField()
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "shipment_items"
