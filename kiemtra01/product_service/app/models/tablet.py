from django.db import models


class TabletProduct(models.Model):
    OS_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('windows', 'Windows'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    cpu = models.CharField(max_length=100)
    ram_gb = models.PositiveIntegerField()
    storage_gb = models.PositiveIntegerField()
    display_size_inches = models.DecimalField(max_digits=4, decimal_places=1)
    display_resolution = models.CharField(max_length=50, blank=True)
    refresh_rate_hz = models.PositiveIntegerField(null=True, blank=True)
    main_camera_mp = models.PositiveIntegerField(null=True, blank=True)
    front_camera_mp = models.PositiveIntegerField(null=True, blank=True)
    battery_mah = models.PositiveIntegerField()
    has_cellular = models.BooleanField(default=False)
    has_stylus_support = models.BooleanField(default=False)
    has_keyboard_support = models.BooleanField(default=False)
    operating_system = models.CharField(max_length=50, choices=OS_CHOICES)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Tablet)"
