from django.db import models


class GamingConsoleProduct(models.Model):
    TYPE_CHOICES = [
        ('home', 'Home Console'),
        ('handheld', 'Handheld'),
        ('hybrid', 'Hybrid'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    console_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    generation = models.CharField(max_length=50, blank=True)
    storage_gb = models.PositiveIntegerField()
    max_resolution = models.CharField(max_length=50, blank=True)
    max_fps = models.PositiveIntegerField(null=True, blank=True)
    has_disc_drive = models.BooleanField(default=False)
    has_4k_support = models.BooleanField(default=False)
    has_ray_tracing = models.BooleanField(default=False)
    has_online_gaming = models.BooleanField(default=True)
    controller_included = models.BooleanField(default=True)
    backward_compatibility = models.TextField(blank=True)  # JSON string of compatible generations
    subscription_required = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Gaming Console)"
