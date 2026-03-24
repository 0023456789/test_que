import uuid
from django.db import models

class CatalogEntry(models.Model):
    """Lightweight read model mirroring book data for catalog browsing."""
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id         = models.UUIDField(unique=True, db_index=True)
    title           = models.CharField(max_length=300)
    isbn            = models.CharField(max_length=20, blank=True)
    author_names    = models.CharField(max_length=500, blank=True)
    category_name   = models.CharField(max_length=100, blank=True)
    category_slug   = models.CharField(max_length=100, blank=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cover_image_url = models.URLField(blank=True)
    average_rating  = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews   = models.PositiveIntegerField(default=0)
    in_stock        = models.BooleanField(default=True)
    is_featured     = models.BooleanField(default=False)
    tags            = models.CharField(max_length=500, blank=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_entries"
        ordering = ["-updated_at"]
