import datetime

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Patient


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name")
    phone = data.get("phone", "")

    if not username or not password or not full_name:
        return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    # Create Django user
    user = User.objects.create_user(username=username, password=password)
    
    # Create associated Patient profile
    age = data.get("age", 30)
    dob = datetime.date.today() - datetime.timedelta(days=int(age) * 365)
    
    patient = Patient.objects.create(
        full_name=full_name,
        phone=phone,
        date_of_birth=dob
    )

    # Generate token
    refresh = RefreshToken.for_user(user)
    
    return Response({
        "access_token": str(refresh.access_token),
        "username": user.username,
        "role": "patient",
        "patient_id": patient.id,
        "doctor_id": None
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    
    username = request.data.get("username")
    password = request.data.get("password")
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
    refresh = RefreshToken.for_user(user)
    
    # Determine role (simplified logic)
    role = "staff" if user.is_staff else "patient"
    patient_id = None
    
    # Try to find associated patient (hacky link by name/username for demo)
    if role == "patient":
        patient = Patient.objects.filter(full_name=username).first()
        if patient:
            patient_id = patient.id
            
    return Response({
        "access_token": str(refresh.access_token),
        "username": user.username,
        "role": role,
        "patient_id": patient_id,
        "doctor_id": None
    })
