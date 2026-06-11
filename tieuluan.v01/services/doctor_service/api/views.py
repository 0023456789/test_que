from rest_framework import viewsets, permissions
from .models import Doctor
from .serializers import DoctorSerializer
from .authentication import MicroserviceJWTAuthentication

class IsAuthenticatedMicroservice(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().order_by('id')
    serializer_class = DoctorSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]
