from decimal import Decimal

from django.core.management.base import BaseCommand

from app.models import ProductItem


class Command(BaseCommand):
	help = "Seed demo catalog data for products."

	def handle(self, *args, **options):
		product_items = [
			{
				"category": "computer",
				"name": "MacBook Pro 14 M3",
				"brand": "Apple",
				"cpu_or_chipset": "Apple M3 Pro",
				"ram_gb": 18,
				"storage_gb": 512,
				"price": Decimal("1999.00"),
				"stock": 8,
				"description": "Compact pro laptop with Liquid Retina XDR display.",
			},
			{
				"category": "computer",
				"name": "ThinkPad X1 Carbon Gen 12",
				"brand": "Lenovo",
				"cpu_or_chipset": "Intel Core Ultra 7",
				"ram_gb": 32,
				"storage_gb": 1024,
				"price": Decimal("2149.00"),
				"stock": 5,
				"description": "Lightweight enterprise ultrabook with premium keyboard.",
			},
			{
				"category": "mobile",
				"name": "iPhone 16 Pro",
				"brand": "Apple",
				"cpu_or_chipset": "A18 Pro",
				"ram_gb": 8,
				"storage_gb": 256,
				"price": Decimal("1199.00"),
				"stock": 12,
				"description": "Titanium flagship with advanced camera system.",
			},
			{
				"category": "mobile",
				"name": "Galaxy S25 Ultra",
				"brand": "Samsung",
				"cpu_or_chipset": "Snapdragon 8 Elite",
				"ram_gb": 12,
				"storage_gb": 512,
				"price": Decimal("1299.00"),
				"stock": 10,
				"description": "Premium Android flagship with S Pen support.",
			},
			{
				"category": "tablet",
				"name": "iPad Pro M4",
				"brand": "Apple",
				"cpu_or_chipset": "Apple M4",
				"ram_gb": 8,
				"storage_gb": 256,
				"price": Decimal("999.00"),
				"stock": 15,
				"description": "Ultra-thin tablet with OLED display.",
			},
		]

		created_items = 0
		for data in product_items:
			_, created = ProductItem.objects.update_or_create(
				name=data["name"],
				brand=data["brand"],
				defaults=data,
			)
			created_items += int(created)

		self.stdout.write(
			self.style.SUCCESS(
				f"Seeded {created_items} product item(s)."
			)
		)
