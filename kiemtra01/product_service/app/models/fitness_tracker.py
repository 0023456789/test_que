from django.db import models


class FitnessTrackerProduct(models.Model):
    TYPE_CHOICES = [
        ('band', 'Fitness Band'),
        ('clip', 'Fitness Clip'),
        ('ring', 'Smart Ring'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    tracker_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    display_type = models.CharField(max_length=50, blank=True)
    battery_days = models.DecimalField(max_digits=4, decimal_places=1)
    has_gps = models.BooleanField(default=False)
    has_heart_rate_monitor = models.BooleanField(default=True)
    has_blood_oxygen_monitor = models.BooleanField(default=False)
    has_sleep_tracking = models.BooleanField(default=True)
    has_step_counter = models.BooleanField(default=True)
    has_calorie_tracking = models.BooleanField(default=True)
    has_water_resistance = models.BooleanField(default=True)
    strap_material = models.CharField(max_length=50, blank=True)
    mobile_app_support = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Fitness Tracker)"
