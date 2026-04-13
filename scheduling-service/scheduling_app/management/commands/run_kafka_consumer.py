import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from scheduling_app.models import PitchSlot, SchedulingOutboxEvent
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Scheduling Service to handle Saga flow'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'scheduling-service-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Scheduling Service (Brokers: {bootstrap_servers})'))
        
        try:
            while True:
                msg = consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break

                # Process message
                try:
                    payload = json.loads(msg.value().decode('utf-8'))
                    event_type = payload.get('event_type')
                    data = payload.get('data')

                    if event_type == 'pitch_booking_initiated':
                        self.handle_booking_initiated(data)
                    elif event_type == 'meeting_failed':
                        self.handle_compensation(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def handle_booking_initiated(self, booking_data):
        """Handle initial booking request by reserving a slot"""
        slot_id = booking_data.get('pitch_slot_id')
        booking_id = booking_data.get('id')
        
        self.stdout.write(self.style.NOTICE(f" [SAGA] Nhận yêu cầu đặt lịch cho Booking #{booking_id}, Slot #{slot_id}"))

        with transaction.atomic():
            try:
                # Select for update to prevent race conditions
                slot = PitchSlot.objects.select_for_update().get(id=slot_id)
                
                if slot.status == 'AVAILABLE':
                    slot.status = 'BOOKED'
                    slot.save()
                    
                    # Confirm success
                    SchedulingOutboxEvent.objects.create(
                        event_type='slot_confirmed',
                        payload={
                            'booking_id': booking_id,
                            'pitch_slot_id': slot_id,
                            'investor_id': slot.investor_id
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f" ✅ [SAGA] Slot #{slot_id} đã được giữ chỗ thành công."))
                else:
                    # Slot already taken
                    SchedulingOutboxEvent.objects.create(
                        event_type='slot_failed',
                        payload={
                            'booking_id': booking_id,
                            'reason': 'Slot is no longer available'
                        }
                    )
                    self.stdout.write(self.style.WARNING(f" ❌ [SAGA] Slot #{slot_id} không khả dụng (Trạng thái: {slot.status})."))
            
            except PitchSlot.DoesNotExist:
                SchedulingOutboxEvent.objects.create(
                    event_type='slot_failed',
                    payload={
                        'booking_id': booking_id,
                        'reason': 'Slot not found'
                    }
                )
                self.stdout.write(self.style.ERROR(f" ❌ [SAGA] Không tìm thấy Slot #{slot_id}."))

    def handle_compensation(self, data):
        """Compensating transaction: Release slot if downstream service (Meeting) fails"""
        slot_id = data.get('pitch_slot_id')
        booking_id = data.get('booking_id')
        
        self.stdout.write(self.style.WARNING(f" [SAGA-COMPENSATION] Nhận tin báo Meeting thất bại cho Booking #{booking_id}. Đang giải phóng Slot #{slot_id}..."))

        with transaction.atomic():
            try:
                slot = PitchSlot.objects.select_for_update().get(id=slot_id)
                if slot.status == 'BOOKED':
                    slot.status = 'AVAILABLE'
                    slot.save()
                    self.stdout.write(self.style.SUCCESS(f" ✅ [SAGA-COMPENSATION] Đã giải phóng Slot #{slot_id} thành công."))
            except PitchSlot.DoesNotExist:
                logger.error(f"Cannot release non-existent slot #{slot_id}")
