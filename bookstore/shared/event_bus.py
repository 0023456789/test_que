"""
Shared Event Bus utility using RabbitMQ (pika).
Each service imports this to publish or consume events.
"""
import json
import logging
import os
import threading
import time
from typing import Callable, Optional

import pika

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def get_connection():
    """Create a robust RabbitMQ connection with retry logic."""
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 60
    params.blocked_connection_timeout = 300
    for attempt in range(5):
        try:
            return pika.BlockingConnection(params)
        except Exception as e:
            logger.warning(f"RabbitMQ connection attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    raise ConnectionError("Cannot connect to RabbitMQ after 5 attempts")


def publish_event(exchange: str, routing_key: str, payload: dict):
    """Publish an event to a fanout/topic exchange."""
    try:
        connection = get_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent
                content_type="application/json",
            ),
        )
        connection.close()
        logger.info(f"Published event: {exchange}/{routing_key}")
    except Exception as e:
        logger.error(f"Failed to publish event {exchange}/{routing_key}: {e}")
        raise


def consume_events(
    queue_name: str,
    exchange: str,
    routing_keys: list[str],
    handler: Callable[[dict], None],
    auto_ack: bool = False,
):
    """Start consuming events from a queue (blocking — run in a thread)."""

    def _run():
        while True:
            try:
                connection = get_connection()
                channel = connection.channel()
                channel.exchange_declare(
                    exchange=exchange, exchange_type="topic", durable=True
                )
                channel.queue_declare(queue=queue_name, durable=True)
                for rk in routing_keys:
                    channel.queue_bind(
                        exchange=exchange, queue=queue_name, routing_key=rk
                    )
                channel.basic_qos(prefetch_count=1)

                def callback(ch, method, properties, body):
                    try:
                        data = json.loads(body)
                        handler(data)
                        if not auto_ack:
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as e:
                        logger.error(f"Error handling event: {e}")
                        if not auto_ack:
                            ch.basic_nack(
                                delivery_tag=method.delivery_tag, requeue=False
                            )

                channel.basic_consume(
                    queue=queue_name, on_message_callback=callback, auto_ack=auto_ack
                )
                logger.info(f"Consuming from {queue_name}")
                channel.start_consuming()
            except Exception as e:
                logger.error(f"Consumer error, reconnecting in 5s: {e}")
                time.sleep(5)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread


# ── Exchange / Routing Key Constants ──────────────────────────────────────────

class Exchanges:
    BOOKSTORE = "bookstore.events"


class Events:
    # Customer
    CUSTOMER_REGISTERED = "customer.registered"
    CUSTOMER_UPDATED = "customer.updated"

    # Order / Saga
    ORDER_CREATED = "order.created"
    ORDER_COMPLETED = "order.completed"
    ORDER_FAILED = "order.failed"
    ORDER_CANCELLED = "order.cancelled"

    # Payment
    PAYMENT_RESERVED = "payment.reserved"
    PAYMENT_CONFIRMED = "payment.confirmed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_CANCELLED = "payment.cancelled"

    # Shipping
    SHIPPING_RESERVED = "shipping.reserved"
    SHIPPING_CONFIRMED = "shipping.confirmed"
    SHIPPING_FAILED = "shipping.failed"
    SHIPPING_CANCELLED = "shipping.cancelled"

    # Book / Inventory
    BOOK_CREATED = "book.created"
    BOOK_UPDATED = "book.updated"
    BOOK_INVENTORY_UPDATED = "book.inventory.updated"
    BOOK_INVENTORY_RESERVED = "book.inventory.reserved"
    BOOK_INVENTORY_RELEASED = "book.inventory.released"

    # Cart
    CART_CHECKED_OUT = "cart.checked_out"

    # Comment / Rating
    COMMENT_CREATED = "comment.created"
    RATING_CREATED = "rating.created"
