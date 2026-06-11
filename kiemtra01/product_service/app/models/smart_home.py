from django.db import models


class SmartHomeProduct(models.Model):
    CATEGORY_CHOICES = [
        ('speaker', 'Smart Speaker'),
        ('display', 'Smart Display'),
        ('lighting', 'Smart Lighting'),
        ('thermostat', 'Smart Thermostat'),
        ('security', 'Security Camera'),
        ('lock', 'Smart Lock'),
        ('plug', 'Smart Plug'),
        ('switch', 'Smart Switch'),
        ('sensor', 'Smart Sensor'),
        ('hub', 'Smart Hub'),
    ]
    
    VOICE_CHOICES = [
        ('alexa', 'Amazon Alexa'),
        ('google_assistant', 'Google Assistant'),
        ('siri', 'Apple Siri'),
        ('none', 'None'),
        ('multiple', 'Multiple'),
    ]
    
    POWER_CHOICES = [
        ('battery', 'Battery'),
        ('wired', 'Wired'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=120)
    smart_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    voice_assistant = models.CharField(max_length=50, choices=VOICE_CHOICES, blank=True)
    connectivity = models.TextField(blank=True)  # JSON string of connectivity options
    power_source = models.CharField(max_length=50, choices=POWER_CHOICES, blank=True)
    mobile_app_support = models.BooleanField(default=True)
    has_scheduling = models.BooleanField(default=False)
    has_automation = models.BooleanField(default=False)
    installation_required = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.brand} - Smart Home)"
