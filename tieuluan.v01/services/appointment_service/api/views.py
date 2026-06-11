import os
import requests
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import jwt
from datetime import datetime, timedelta
from .models import Appointment
from .serializers import AppointmentSerializer
from .authentication import MicroserviceJWTAuthentication

JWT_SECRET = os.environ.get("JWT_SECRET", "super-secret-demo-key")
PATIENT_SERVICE_URL = os.environ.get("PATIENT_SERVICE_URL", "http://patient_service:8001")

def create_jwt(payload):
    exp = datetime.utcnow() + timedelta(hours=2)
    payload["exp"] = exp
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    
    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username exists"}, status=400)
    
    user = User.objects.create_user(username=username, password=password)
    
    internal_token = create_jwt({"role": "staff"})
    
    patient_data = {
        "full_name": data.get("full_name", username),
        "age": int(data.get("age", 30)),
        "phone": data.get("phone", "")
    }
    try:
        resp = requests.post(f"{PATIENT_SERVICE_URL}/api/patients/", json=patient_data, headers={"Authorization": f"Bearer {internal_token}"})
        resp.raise_for_status()
        patient_id = resp.json().get("id")
    except Exception as e:
        user.delete()
        return Response({"detail": f"Failed to create patient: {str(e)}"}, status=500)
    
    token = create_jwt({
        "username": username,
        "role": "patient",
        "patient_id": patient_id
    })
    
    return Response({
        "access_token": token,
        "role": "patient",
        "patient_id": patient_id,
        "username": username
    })

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)
    
    role = "staff" if user.is_staff else "patient"
    patient_id = None
    
    if role == "patient":
        internal_token = create_jwt({"role": "staff"})
        try:
            resp = requests.get(f"{PATIENT_SERVICE_URL}/api/patients/", headers={"Authorization": f"Bearer {internal_token}"})
            if resp.ok:
                pts = resp.json()
                for p in pts:
                    if p.get("full_name") == username or str(p.get("id")) == username:
                        patient_id = p.get("id")
                        break
        except:
            pass
            
    token = create_jwt({
        "username": username,
        "role": role,
        "patient_id": patient_id
    })
    
    return Response({
        "access_token": token,
        "role": role,
        "patient_id": patient_id,
        "username": username
    })

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('-appointment_time')
    serializer_class = AppointmentSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        new_status = request.data.get("status")
        if new_status:
            appointment.status = new_status
            appointment.save(update_fields=["status"])
        return Response(self.get_serializer(appointment).data)
