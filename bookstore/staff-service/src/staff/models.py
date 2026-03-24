import uuid
from django.db import models

class StaffMember(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id     = models.UUIDField(unique=True)
    email       = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    department  = models.CharField(max_length=100, blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff_members"

class InventoryAction(models.Model):
    """Audit trail for all inventory changes performed by staff."""
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff       = models.ForeignKey(StaffMember, on_delete=models.SET_NULL, null=True)
    book_id     = models.UUIDField()
    action      = models.CharField(max_length=20)  # add / subtract / set
    quantity    = models.IntegerField()
    note        = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_actions"
        ordering = ["-created_at"]
