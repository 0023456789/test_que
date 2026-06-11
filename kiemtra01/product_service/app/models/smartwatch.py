from django.db import models


class SmartwatchProduct(models.Model):
    COMPATIBILITY_CHOICES = [
        ('ios_android', 'iOS & Android'),
        ('ios_only', 'iOS Only'),
        ('android_only', 'Android Only'),
        ('all', 'All Platforms'),
    ]
    
    DISPLAY_CHOICES = [
        ('amoled', 'AMOLED'),
        ('lcd', 'LCD'),
        ('oled', 'OLED'),
        ('e_ink', 'E-Ink'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    compatibility = models.CharField(max_length=20, choices=COMPATIBILITY_CHOICES)
    display_type = models.CharField(max_length=50, choices=DISPLAY_CHOICES)
    display_size_inches = models.DecimalField(max_digits=4, decimal_places=1)
    battery_days = models.DecimalField(max_digits=4, decimal_places=1)
    has_gps = models.BooleanField(default=True)
    has_heart_rate_monitor = models.BooleanField(default=True)
    has_blood_oxygen_monitor = models.BooleanField(default=False)
    has_ecg = models.BooleanField(default=False)
    has_sleep_tracking = models.BooleanField(default=True)
    has_water_resistance = models.BooleanField(default=False)
    strap_material = models.CharField(max_length=50, blank=True)
    case_material = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Smartwatch)"
