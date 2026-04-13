from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import hashlib
from django.db import transaction
from .models import AvailabilityTemplate, PitchSlot, SchedulingOutboxEvent, SchedulingIdempotencyRecord
from .serializers import (
    AvailabilityTemplateSerializer, 
    PitchSlotSerializer, 
    PitchSlotStatusUpdateSerializer
)


def _request_hash(request):
    payload = request.data if hasattr(request, 'data') else {}
    raw_payload = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(f'{request.path}:{raw_payload}'.encode('utf-8')).hexdigest()

def _get_idempotency_key(request):
    return request.headers.get('Idempotency-Key') or request.META.get('HTTP_IDEMPOTENCY_KEY')

def _get_replayed_response(request):
    idempotency_key = _get_idempotency_key(request)
    if not idempotency_key:
        return None

    request_signature = _request_hash(request)
    record = SchedulingIdempotencyRecord.objects.filter(key=idempotency_key).first()
    if not record:
        return None

    if record.request_hash != request_signature:
        return Response(
            {'error': 'Idempotency key already used with different payload'},
            status=status.HTTP_409_CONFLICT,
        )

    return Response(record.response_body, status=record.response_status)

def _store_idempotent_response(request, response):
    idempotency_key = _get_idempotency_key(request)
    if not idempotency_key:
        return

    payload = response.data if isinstance(response.data, (dict, list)) else {'detail': str(response.data)}
    SchedulingIdempotencyRecord.objects.update_or_create(
        key=idempotency_key,
        defaults={
            'endpoint': request.path,
            'request_hash': _request_hash(request),
            'response_status': int(response.status_code),
            'response_body': payload,
        },
    )

def _outbox_payload_with_saga_meta(request, payload):
    if not isinstance(payload, dict):
        return payload

    enriched_payload = dict(payload)
    saga_id = request.headers.get('X-Saga-Id') or request.META.get('HTTP_X_SAGA_ID')
    correlation_id = request.headers.get('X-Correlation-Id') or request.META.get('HTTP_X_CORRELATION_ID')
    idempotency_key = _get_idempotency_key(request)
    if saga_id:
        enriched_payload['_saga_id'] = saga_id
    if correlation_id:
        enriched_payload['_correlation_id'] = correlation_id
    if idempotency_key:
        enriched_payload['_idempotency_key'] = idempotency_key
    return enriched_payload

class AvailabilityTemplateViewSet(viewsets.ModelViewSet):
    """Availability templates for investors"""
    queryset = AvailabilityTemplate.objects.all()
    serializer_class = AvailabilityTemplateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        replayed = _get_replayed_response(request)
        if replayed: return replayed
        response = super().create(request, *args, **kwargs)
        _store_idempotent_response(request, response)
        return response

    def update(self, request, *args, **kwargs):
        replayed = _get_replayed_response(request)
        if replayed: return replayed
        response = super().update(request, *args, **kwargs)
        _store_idempotent_response(request, response)
        return response

    def destroy(self, request, *args, **kwargs):
        replayed = _get_replayed_response(request)
        if replayed: return replayed
        response = super().destroy(request, *args, **kwargs)
        _store_idempotent_response(request, response)
        return response

    def perform_create(self, serializer):
        with transaction.atomic():
            template = serializer.save()
            SchedulingOutboxEvent.objects.create(
                event_type='availability_template_created',
                payload=_outbox_payload_with_saga_meta(self.request, AvailabilityTemplateSerializer(template).data),
            )

    def perform_update(self, serializer):
        with transaction.atomic():
            template = serializer.save()
            SchedulingOutboxEvent.objects.create(
                event_type='availability_template_updated',
                payload=_outbox_payload_with_saga_meta(self.request, AvailabilityTemplateSerializer(template).data),
            )

    def perform_destroy(self, instance):
        with transaction.atomic():
            template_id = instance.id
            SchedulingOutboxEvent.objects.create(
                event_type='availability_template_deleted',
                payload=_outbox_payload_with_saga_meta(self.request, {'id': template_id}),
            )
            instance.delete()

    @action(detail=False, methods=['get'])
    def by_investor(self, request):
        investor_id = request.query_params.get('investor_id')
        if not investor_id:
            return Response({'error': 'investor_id is required'}, status=400)
        templates = AvailabilityTemplate.objects.filter(investor_id=investor_id)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

class PitchSlotViewSet(viewsets.ModelViewSet):
    """Investor availability slots"""
    queryset = PitchSlot.objects.all()
    serializer_class = PitchSlotSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        replayed = _get_replayed_response(request)
        if replayed: return replayed
        response = super().create(request, *args, **kwargs)
        _store_idempotent_response(request, response)
        return response

    def update(self, request, *args, **kwargs):
        replayed = _get_replayed_response(request)
        if replayed: return replayed
        response = super().update(request, *args, **kwargs)
        _store_idempotent_response(request, response)
        return response

    def destroy(self, request, *args, **kwargs):
        replayed = _get_replayed_response(request)
        if replayed: return replayed
        response = super().destroy(request, *args, **kwargs)
        _store_idempotent_response(request, response)
        return response

    def perform_create(self, serializer):
        with transaction.atomic():
            slot = serializer.save()
            SchedulingOutboxEvent.objects.create(
                event_type='pitch_slot_created',
                payload=_outbox_payload_with_saga_meta(self.request, PitchSlotSerializer(slot).data),
            )

    def perform_update(self, serializer):
        with transaction.atomic():
            slot = serializer.save()
            SchedulingOutboxEvent.objects.create(
                event_type='pitch_slot_updated',
                payload=_outbox_payload_with_saga_meta(self.request, PitchSlotSerializer(slot).data),
            )

    def perform_destroy(self, instance):
        with transaction.atomic():
            slot_id = instance.id
            SchedulingOutboxEvent.objects.create(
                event_type='pitch_slot_deleted',
                payload=_outbox_payload_with_saga_meta(self.request, {'id': slot_id}),
            )
            instance.delete()

    def get_serializer_class(self):
        if self.action == 'update_status':
            return PitchSlotStatusUpdateSerializer
        return PitchSlotSerializer

    def get_queryset(self):
        queryset = PitchSlot.objects.all()
        investor_id = self.request.query_params.get('investor_id')
        status_filter = self.request.query_params.get('status')

        if investor_id:
            queryset = queryset.filter(investor_id=investor_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        replayed = _get_replayed_response(request)
        if replayed: return replayed

        slot = self.get_object()
        serializer = PitchSlotStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                slot.status = serializer.validated_data['status']
                slot.save()
                SchedulingOutboxEvent.objects.create(
                    event_type='pitch_slot_status_updated',
                    payload=_outbox_payload_with_saga_meta(request, PitchSlotSerializer(slot).data),
                )
            response = Response({'success': True, 'status': slot.status})
            _store_idempotent_response(request, response)
            return response
        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        _store_idempotent_response(request, response)
        return response

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = PitchSlot.objects.count()
        booked = PitchSlot.objects.filter(status='BOOKED').count()
        return Response({
            'total_slots': total,
            'booked_slots': booked,
            'available_slots': total - booked
        })

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'scheduling-service'})
