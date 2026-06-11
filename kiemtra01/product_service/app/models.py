from django.db import models

# Import all product models
from .models.computer import ComputerProduct
from .models.mobile import MobileProduct
from .models.tablet import TabletProduct
from .models.smartwatch import SmartwatchProduct
from .models.headphone import HeadphoneProduct
from .models.camera import CameraProduct
from .models.gaming_console import GamingConsoleProduct
from .models.tv import TVProduct
from .models.smart_home import SmartHomeProduct
from .models.fitness_tracker import FitnessTrackerProduct
from .models.drone import DroneProduct

# Legacy ProductItem for backward compatibility
class ProductItem(models.Model):
	category = models.CharField(max_length=50, default="computer")
	name = models.CharField(max_length=255)
	brand = models.CharField(max_length=120)
	cpu_or_chipset = models.CharField(max_length=120, blank=True)
	ram_gb = models.PositiveIntegerField()
	storage_gb = models.PositiveIntegerField()
	price = models.DecimalField(max_digits=12, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} ({self.brand} - {self.category})"
