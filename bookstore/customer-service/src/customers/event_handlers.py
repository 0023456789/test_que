import logging
import sys
import os

sys.path.insert(0, "/app")
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def publish_customer_registered(customer):
    try:
        import pika, json
        params = pika.URLParameters(RABBITMQ_URL)
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        ch.exchange_declare(exchange="bookstore.events", exchange_type="topic", durable=True)
        ch.basic_publish(
            exchange="bookstore.events",
            routing_key="customer.registered",
            body=json.dumps({
                "event": "customer.registered",
                "customer_id": str(customer.id),
                "user_id": str(customer.user_id),
                "email": customer.email,
            }),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        conn.close()
        logger.info(f"Published customer.registered for {customer.id}")
    except Exception as e:
        logger.warning(f"Could not publish customer event: {e}")
