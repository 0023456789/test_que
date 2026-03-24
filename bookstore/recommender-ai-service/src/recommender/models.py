import uuid
from django.db import models

class Recommendation(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id     = models.UUIDField(db_index=True)
    book_id         = models.UUIDField()
    score           = models.FloatField(default=0.0)  # 0.0 – 1.0
    reason          = models.CharField(max_length=255, blank=True)
    algorithm       = models.CharField(max_length=50, default="collaborative")
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendations"
        ordering = ["-score"]
        unique_together = [("customer_id", "book_id")]

class BookSimilarity(models.Model):
    """Content-based similarity between books."""
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id_a   = models.UUIDField(db_index=True)
    book_id_b   = models.UUIDField()
    similarity  = models.FloatField(default=0.0)

    class Meta:
        db_table = "book_similarities"
        unique_together = [("book_id_a", "book_id_b")]
