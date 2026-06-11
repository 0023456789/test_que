from django.db import models


class ComputerProduct(models.Model):
    CPU_CHOICES = [
        ('intel_i3', 'Intel Core i3'),
        ('intel_i5', 'Intel Core i5'),
        ('intel_i7', 'Intel Core i7'),
        ('intel_i9', 'Intel Core i9'),
        ('amd_ryzen3', 'AMD Ryzen 3'),
        ('amd_ryzen5', 'AMD Ryzen 5'),
        ('amd_ryzen7', 'AMD Ryzen 7'),
        ('amd_ryzen9', 'AMD Ryzen 9'),
        ('apple_m1', 'Apple M1'),
        ('apple_m2', 'Apple M2'),
        ('apple_m3', 'Apple M3'),
    ]
    
    STORAGE_CHOICES = [
        ('ssd', 'SSD'),
        ('hdd', 'HDD'),
        ('hybrid', 'Hybrid'),
    ]
    
    OS_CHOICES = [
        ('windows', 'Windows'),
        ('macos', 'macOS'),
        ('linux', 'Linux'),
        ('chromeos', 'Chrome OS'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    cpu = models.CharField(max_length=20, choices=CPU_CHOICES)
    ram_gb = models.PositiveIntegerField()
    storage_type = models.CharField(max_length=20, choices=STORAGE_CHOICES)
    storage_gb = models.PositiveIntegerField()
    gpu = models.CharField(max_length=100, blank=True)
    display_size_inches = models.DecimalField(max_digits=4, decimal_places=1)
    display_resolution = models.CharField(max_length=50, blank=True)
    refresh_rate_hz = models.PositiveIntegerField(null=True, blank=True)
    operating_system = models.CharField(max_length=50, choices=OS_CHOICES, blank=True)
    has_touchscreen = models.BooleanField(default=False)
    has_backlit_keyboard = models.BooleanField(default=False)
    has_fingerprint_reader = models.BooleanField(default=False)
    has_webcam = models.BooleanField(default=True)
    battery_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    ports = models.TextField(blank=True)  # JSON string of ports
    warranty_months = models.PositiveIntegerField(default=12)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Computer)"
