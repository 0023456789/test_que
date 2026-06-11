from django.db import models


class HeadphoneProduct(models.Model):
    TYPE_CHOICES = [
        ('over_ear', 'Over-Ear'),
        ('on_ear', 'On-Ear'),
        ('in_ear', 'In-Ear'),
        ('true_wireless', 'True Wireless'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    headphone_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_wireless = models.BooleanField(default=True)
    has_noise_cancelling = models.BooleanField(default=False)
    has_microphone = models.BooleanField(default=True)
    battery_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    charging_time_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bluetooth_version = models.CharField(max_length=10, blank=True)
    frequency_response = models.CharField(max_length=50, blank=True)
    impedance_ohms = models.PositiveIntegerField(null=True, blank=True)
    driver_size_mm = models.PositiveIntegerField(null=True, blank=True)
    has_fast_charging = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Headphone)"
