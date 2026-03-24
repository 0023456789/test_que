import uuid
from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAYMENT_RESERVED = "payment_reserved", "Payment Reserved"
    SHIPPING_RESERVED = "shipping_reserved", "Shipping Reserved"
    COMPLETED = "completed", "Completed"
    CANCELLING = "cancelling", "Cancelling"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class SagaStep(models.TextChoices):
    CREATE_ORDER = "create_order", "Create Order"
    RESERVE_PAYMENT = "reserve_payment", "Reserve Payment"
    RESERVE_SHIPPING = "reserve_shipping", "Reserve Shipping"
    CONFIRM_ORDER = "confirm_order", "Confirm Order"
    COMPENSATE_PAYMENT = "compensate_payment", "Compensate Payment"
    COMPENSATE_SHIPPING = "compensate_shipping", "Compensate Shipping"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField(db_index=True)
    cart_id = models.UUIDField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    # Address snapshot
    shipping_street = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)

    # Financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=8, decimal_places=2, default=5.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # External references
    payment_id = models.UUIDField(null=True, blank=True)
    shipment_id = models.UUIDField(null=True, blank=True)

    # Saga tracking
    saga_step = models.CharField(max_length=30, choices=SagaStep.choices, default=SagaStep.CREATE_ORDER)
    failure_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"Order({self.id}) status={self.status}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book_id = models.UUIDField()
    book_title = models.CharField(max_length=300)
    book_isbn = models.CharField(max_length=20, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "order_items"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class SagaLog(models.Model):
    """Append-only log for Saga step tracking and audit."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="saga_logs")
    step = models.CharField(max_length=30)
    status = models.CharField(max_length=20)  # started / succeeded / failed
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saga_logs"
        ordering = ["created_at"]
