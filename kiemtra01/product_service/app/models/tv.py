from django.db import models


class TVProduct(models.Model):
    DISPLAY_CHOICES = [
        ('led', 'LED'),
        ('oled', 'OLED'),
        ('qled', 'QLED'),
        ('mini_led', 'Mini-LED'),
        ('micro_led', 'Micro-LED'),
    ]
    
    RESOLUTION_CHOICES = [
        ('hd', 'HD (720p)'),
        ('full_hd', 'Full HD (1080p)'),
        ('4k', '4K UHD'),
        ('8k', '8K UHD'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    display_type = models.CharField(max_length=20, choices=DISPLAY_CHOICES)
    display_size_inches = models.PositiveIntegerField()
    resolution = models.CharField(max_length=50, choices=RESOLUTION_CHOICES)
    refresh_rate_hz = models.PositiveIntegerField()
    has_smart_tv = models.BooleanField(default=True)
    operating_system = models.CharField(max_length=50, blank=True)
    has_hdr = models.BooleanField(default=False)
    hdr_format = models.CharField(max_length=50, blank=True)
    has_dolby_vision = models.BooleanField(default=False)
    has_dolby_atmos = models.BooleanField(default=False)
    hdmi_ports = models.PositiveIntegerField(default=2)
    usb_ports = models.PositiveIntegerField(default=1)
    has_wifi = models.BooleanField(default=True)
    has_bluetooth = models.BooleanField(default=False)
    wall_mountable = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - TV)"
