from decimal import Decimal
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import InsurancePolicy, Invoice
from .serializers import InsurancePolicySerializer, InvoiceSerializer
from .authentication import MicroserviceJWTAuthentication

class IsAuthenticatedMicroservice(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class InsurancePolicyViewSet(viewsets.ModelViewSet):
    queryset = InsurancePolicy.objects.all().order_by('id')
    serializer_class = InsurancePolicySerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

    def create(self, request, *args, **kwargs):
        patient_id = request.data.get('patient_id')
        amount_total = Decimal(str(request.data.get('amount_total', 0)))
        
        insurance_covered = Decimal(0)
        patient_payable = amount_total
        
        # Check for active insurance policy
        if patient_id:
            policy = InsurancePolicy.objects.filter(patient_id=patient_id).first()
            if policy:
                coverage_percent = Decimal(str(policy.coverage_percent))
                insurance_covered = (amount_total * coverage_percent) / Decimal(100)
                patient_payable = amount_total - insurance_covered

        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Save with calculated values
        invoice = serializer.save(
            insurance_covered=insurance_covered,
            patient_payable=patient_payable
        )
        
        response_serializer = self.get_serializer(invoice)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = Invoice.STATUS_PAID
        invoice.save(update_fields=['status'])
        return Response(self.get_serializer(invoice).data)
