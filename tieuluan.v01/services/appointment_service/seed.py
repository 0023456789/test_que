import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def seed():
    # Staff
    if not User.objects.filter(username="staff").exists():
        User.objects.create_superuser("staff", "admin@example.com", "staff123")
    
    # Patients
    for p in ["patient1", "patient2"]:
        if not User.objects.filter(username=p).exists():
            User.objects.create_user(p, f"{p}@example.com", "patient123")
            
    # Doctors
    for d in ["doctor1", "doctor2"]:
        if not User.objects.filter(username=d).exists():
            u = User.objects.create_user(d, f"{d}@example.com", "doctor123")
            u.is_staff = True # Doctors have staff-like access in this demo
            u.save()
        
    print("Demo Users seed complete.")

if __name__ == "__main__":
    seed()
