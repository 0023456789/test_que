from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from app.models import StaffUser


class Command(BaseCommand):
	help = "Seed demo staff data."

	def handle(self, *args, **options):
		staff_members = [
			{
				"username": "demo_staff",
				"full_name": "Demo Staff",
				"email": "demo.staff@techvault.local",
				"password": "Password123!",
			},
			{
				"username": "inventory.lead",
				"full_name": "Inventory Lead",
				"email": "inventory.lead@techvault.local",
				"password": "Password123!",
			},
		]

		created_count = 0
		for data in staff_members:
			_, created = StaffUser.objects.update_or_create(
				username=data["username"],
				defaults={
					"full_name": data["full_name"],
					"email": data["email"],
					"password_hash": make_password(data["password"]),
				},
			)
			created_count += int(created)

		self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} staff account(s)."))
