import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Patient

def seed():
    # We clear and seed matching IDs if possible, but for simplicity just create if missing
    if not Patient.objects.filter(id=1).exists():
        Patient.objects.create(id=1, full_name="Patient 1", age=25, phone="0911111111")
    if not Patient.objects.filter(id=2).exists():
        Patient.objects.create(id=2, full_name="Patient 2", age=32, phone="0922222222")
    print("Demo Patients seed complete.")

if __name__ == "__main__":
    seed()
