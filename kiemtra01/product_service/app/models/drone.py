from django.db import models


class DroneProduct(models.Model):
    TYPE_CHOICES = [
        ('consumer', 'Consumer'),
        ('professional', 'Professional'),
        ('racing', 'Racing'),
        ('toy', 'Toy'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    drone_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    camera_resolution_mp = models.PositiveIntegerField(null=True, blank=True)
    video_resolution = models.CharField(max_length=50, blank=True)
    flight_time_minutes = models.PositiveIntegerField()
    max_range_km = models.DecimalField(max_digits=4, decimal_places=1)
    max_speed_kmh = models.PositiveIntegerField(null=True, blank=True)
    has_gps = models.BooleanField(default=True)
    has_obstacle_avoidance = models.BooleanField(default=False)
    has_follow_me = models.BooleanField(default=False)
    has_return_to_home = models.BooleanField(default=True)
    controller_included = models.BooleanField(default=True)
    battery_charging_time = models.PositiveIntegerField(null=True, blank=True)
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
        return f"{self.name} ({self.brand} - Drone)"
