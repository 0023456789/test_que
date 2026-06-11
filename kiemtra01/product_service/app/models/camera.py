from django.db import models


class CameraProduct(models.Model):
    TYPE_CHOICES = [
        ('dslr', 'DSLR'),
        ('mirrorless', 'Mirrorless'),
        ('compact', 'Compact'),
        ('action', 'Action Camera'),
        ('bridge', 'Bridge Camera'),
    ]
    
    SENSOR_CHOICES = [
        ('full_frame', 'Full Frame'),
        ('aps_c', 'APS-C'),
        ('micro_43', 'Micro Four Thirds'),
        ('1_inch', '1-inch'),
        ('smaller', 'Smaller'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    camera_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_CHOICES)
    megapixels = models.PositiveIntegerField()
    iso_range = models.CharField(max_length=50, blank=True)
    video_resolution = models.CharField(max_length=50, blank=True)
    video_fps = models.PositiveIntegerField(null=True, blank=True)
    has_image_stabilization = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    has_bluetooth = models.BooleanField(default=False)
    has_gps = models.BooleanField(default=False)
    battery_shots = models.PositiveIntegerField(null=True, blank=True)
    lens_mount = models.CharField(max_length=50, blank=True)
    viewfinder_type = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Camera)"
