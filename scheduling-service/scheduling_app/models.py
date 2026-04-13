from django.db import models

class AvailabilityTemplate(models.Model):
    """Recurring availability for investors"""
    investor_id = models.BigIntegerField()
    day_of_week = models.IntegerField() # 0-6 (Mon-Sun)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'availability_templates'

class PitchSlot(models.Model):
    """Investor availability slots"""
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BOOKED', 'Booked'),
        ('BLOCKED', 'Blocked'),
    ]
    
    investor_id = models.BigIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pitch_slots'
        ordering = ['start_time']

class SchedulingOutboxEvent(models.Model):
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'scheduling_outbox_events'
        ordering = ['created_at']


class SchedulingIdempotencyRecord(models.Model):
    key = models.CharField(max_length=255, unique=True)
    endpoint = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    response_status = models.IntegerField()
    response_body = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheduling_idempotency_records'
        ordering = ['-created_at']
