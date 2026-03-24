import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Rating(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id     = models.UUIDField(db_index=True)
    customer_id = models.UUIDField()
    score       = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ratings"
        unique_together = [("book_id", "customer_id")]

class Comment(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id     = models.UUIDField(db_index=True)
    customer_id = models.UUIDField()
    author_name = models.CharField(max_length=200, blank=True)
    body        = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
