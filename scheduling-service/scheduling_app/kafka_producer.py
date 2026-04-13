import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'startup-service-producer'
        }
        try:
            self.producer = Producer(self.conf)
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            self.producer = None

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish_event(self, topic, event_type, data):
        if not self.producer:
            logger.warning("Kafka producer not initialized. Skipping event.")
            return

        message = {
            'event_type': event_type,
            'data': data
        }
        
        try:
            self.producer.produce(
                topic, 
                key=str(data.get('id', '')),
                value=json.dumps(message).encode('utf-8'),
                callback=self.delivery_report
            )
            # Use flush() with a timeout to ensure reliable delivery
            self.producer.flush(timeout=5.0)
            logger.info(f"Published {event_type} to {topic} (Confirmed)")
        except Exception as e:
            logger.error(f"Error publishing to Kafka: {e}")

# Global instance
producer = KafkaProducer()

def publish_startup_created(startup_data):
    producer.publish_event('pitching_events', 'startup_created', startup_data)

def publish_startup_deleted(startup_id):
    producer.publish_event('pitching_events', 'startup_deleted', {'id': startup_id})
