from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Medication, Prescription
from .serializers import MedicationSerializer, PrescriptionSerializer
from .authentication import MicroserviceJWTAuthentication

class IsAuthenticatedMicroservice(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by('id')
    serializer_class = MedicationSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all().order_by('-created_at')
    serializer_class = PrescriptionSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

    def create(self, request, *args, **kwargs):
        medication_ids = request.data.get('medication_ids', [])
        
        # Check basic drug interactions
        warnings = []
        meds = Medication.objects.filter(id__in=medication_ids)
        med_names = [m.name.lower() for m in meds]
        
        for m in meds:
            if m.incompatible_with:
                incompatibles = [x.strip().lower() for x in m.incompatible_with.split(',')]
                for inc in incompatibles:
                    if inc in med_names:
                        warnings.append(f"{m.name} is incompatible with {inc.title()}")
                        
        warning_text = "; ".join(warnings)
        
        data = request.data.copy()
        if warning_text:
            data['interaction_warnings'] = warning_text
            
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Add M2M
        prescription = serializer.instance
        prescription.medications.set(meds)
        
        response_serializer = self.get_serializer(prescription)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='dispense')
    def dispense(self, request, pk=None):
        prescription = self.get_object()
        prescription.status = Prescription.STATUS_DISPENSED
        prescription.save(update_fields=['status'])
        return Response(self.get_serializer(prescription).data)
