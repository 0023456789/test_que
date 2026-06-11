from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Patient
from .serializers import PatientSerializer
from .authentication import MicroserviceJWTAuthentication

class IsAuthenticatedMicroservice(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('id')
    serializer_class = PatientSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

    def create(self, request, *args, **kwargs):
        # Anyone authenticated (e.g. staff/appointment service token) can create
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def self(self, request):
        if request.user.role != "patient":
            return Response({"detail": "Only patients can view their own profile via this endpoint."}, status=status.HTTP_403_FORBIDDEN)
        
        patient_id = request.user.patient_id
        if not patient_id:
            return Response({"detail": "No patient ID in token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(patient)
        return Response(serializer.data)
