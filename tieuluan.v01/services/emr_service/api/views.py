from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Encounter, LabTest
from .serializers import EncounterSerializer, LabTestSerializer
from .authentication import MicroserviceJWTAuthentication

class IsAuthenticatedMicroservice(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all().order_by('-created_at')
    serializer_class = EncounterSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

    @action(detail=True, methods=['post'], url_path='order-test')
    def order_test(self, request, pk=None):
        encounter = self.get_object()
        test_name = request.data.get('test_name')
        if not test_name:
            return Response({"detail": "test_name is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        lab_test = LabTest.objects.create(encounter=encounter, test_name=test_name)
        return Response(LabTestSerializer(lab_test).data, status=status.HTTP_201_CREATED)

class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all().order_by('-created_at')
    serializer_class = LabTestSerializer
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAuthenticatedMicroservice]

    @action(detail=True, methods=['post'], url_path='upload-result')
    def upload_result(self, request, pk=None):
        lab_test = self.get_object()
        result_text = request.data.get('result')
        if not result_text:
            return Response({"detail": "result is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        lab_test.result = result_text
        lab_test.status = LabTest.STATUS_COMPLETED
        lab_test.save(update_fields=['result', 'status'])
        
        return Response(self.get_serializer(lab_test).data)
