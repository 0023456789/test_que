import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Doctor

def seed():
    Doctor.objects.all().delete()
    Doctor.objects.create(id=1, full_name="Doctor 1 (Cardiology)", specialty="Cardiology")
    Doctor.objects.create(id=2, full_name="Doctor 2 (Neurology)", specialty="Neurology")
    print("Demo Doctors seed complete.")

if __name__ == "__main__":
    seed()
