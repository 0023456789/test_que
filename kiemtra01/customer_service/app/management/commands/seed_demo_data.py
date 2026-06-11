from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from app.models import Cart, CustomerUser


class Command(BaseCommand):
	help = "Seed demo customer data."

	def handle(self, *args, **options):
		customers = [
			{
				"username": "demo_customer",
				"full_name": "Demo Customer",
				"email": "demo.customer@techvault.local",
				"password": "Password123!",
			},
			{
				"username": "alex.wong",
				"full_name": "Alex Wong",
				"email": "alex.wong@techvault.local",
				"password": "Password123!",
			},
		]

		created_count = 0
		for data in customers:
			customer, created = CustomerUser.objects.update_or_create(
				username=data["username"],
				defaults={
					"full_name": data["full_name"],
					"email": data["email"],
					"password_hash": make_password(data["password"]),
				},
			)
			Cart.objects.get_or_create(customer=customer, status="active")
			created_count += int(created)

		self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} customer account(s)."))
