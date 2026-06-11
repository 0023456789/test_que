from django.db import models


class MobileProduct(models.Model):
    CHIPSET_CHOICES = [
        ('snapdragon_7', 'Snapdragon 7 Series'),
        ('snapdragon_8', 'Snapdragon 8 Series'),
        ('mediatek_dimensity', 'MediaTek Dimensity'),
        ('apple_a15', 'Apple A15'),
        ('apple_a16', 'Apple A16'),
        ('apple_a17', 'Apple A17'),
        ('exynos', 'Samsung Exynos'),
        ('kirin', 'Huawei Kirin'),
    ]
    
    OS_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]
    
    SIM_CHOICES = [
        ('dual_sim', 'Dual SIM'),
        ('single_sim', 'Single SIM'),
        ('esim', 'eSIM'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    chipset = models.CharField(max_length=20, choices=CHIPSET_CHOICES)
    ram_gb = models.PositiveIntegerField()
    storage_gb = models.PositiveIntegerField()
    display_size_inches = models.DecimalField(max_digits=4, decimal_places=1)
    display_resolution = models.CharField(max_length=50, blank=True)
    refresh_rate_hz = models.PositiveIntegerField(null=True, blank=True)
    main_camera_mp = models.PositiveIntegerField()
    front_camera_mp = models.PositiveIntegerField()
    battery_mah = models.PositiveIntegerField()
    fast_charging_w = models.PositiveIntegerField(null=True, blank=True)
    has_5g = models.BooleanField(default=False)
    has_nfc = models.BooleanField(default=False)
    has_wireless_charging = models.BooleanField(default=False)
    has_water_resistance = models.BooleanField(default=False)
    operating_system = models.CharField(max_length=50, choices=OS_CHOICES)
    sim_type = models.CharField(max_length=20, choices=SIM_CHOICES)
    color_options = models.TextField(blank=True)  # JSON string of colors
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Mobile)"
