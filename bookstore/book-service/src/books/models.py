import uuid
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "authors"

    def __str__(self):
        return self.name


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image_url = models.URLField(blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    published_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=50, default="English")
    pages = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="books")
    authors = models.ManyToManyField(Author, related_name="books")

    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)

    # Stats (denormalized for performance)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books"

    def __str__(self):
        return f"{self.title} (ISBN: {self.isbn})"

    @property
    def available_quantity(self):
        return max(0, self.stock_quantity - self.reserved_quantity)

    def reserve_stock(self, quantity: int) -> bool:
        if self.available_quantity >= quantity:
            self.reserved_quantity += quantity
            self.save(update_fields=["reserved_quantity"])
            return True
        return False

    def release_stock(self, quantity: int):
        self.reserved_quantity = max(0, self.reserved_quantity - quantity)
        self.save(update_fields=["reserved_quantity"])

    def deduct_stock(self, quantity: int):
        self.stock_quantity = max(0, self.stock_quantity - quantity)
        self.reserved_quantity = max(0, self.reserved_quantity - quantity)
        self.save(update_fields=["stock_quantity", "reserved_quantity"])
