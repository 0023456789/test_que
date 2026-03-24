"""
Saga Orchestrator for Order Creation.

Steps:
  1. Create Order (status: PENDING)
  2. Reserve Payment via pay-service
  3. Reserve Shipping via ship-service
  4. Confirm Order (status: COMPLETED)

Compensations (reverse order):
  - Cancel Shipping (if reserved)
  - Cancel Payment (if reserved)
  - Mark Order as FAILED
"""
import logging
import os
import requests

from .models import Order, OrderItem, SagaLog, OrderStatus, SagaStep

logger = logging.getLogger(__name__)

PAY_SERVICE_URL = os.environ.get("PAY_SERVICE_URL", "http://pay-service:8000")
SHIP_SERVICE_URL = os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8000")
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")


class SagaOrchestrator:
    def __init__(self, order: Order):
        self.order = order

    def _log(self, step: str, status: str, message: str = ""):
        SagaLog.objects.create(order=self.order, step=step, status=status, message=message)
        logger.info(f"[Saga] order={self.order.id} step={step} status={status} {message}")

    def _update_order(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self.order, key, val)
        self.order.save()

    # ── Step 2: Reserve Payment ───────────────────────────────────────────────

    def _reserve_payment(self) -> bool:
        self._update_order(saga_step=SagaStep.RESERVE_PAYMENT)
        self._log(SagaStep.RESERVE_PAYMENT, "started")
        try:
            resp = requests.post(
                f"{PAY_SERVICE_URL}/api/payments/reserve/",
                json={
                    "order_id": str(self.order.id),
                    "customer_id": str(self.order.customer_id),
                    "amount": str(self.order.total_amount),
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                self._update_order(
                    payment_id=data.get("payment_id"),
                    status=OrderStatus.PAYMENT_RESERVED,
                )
                self._log(SagaStep.RESERVE_PAYMENT, "succeeded", f"payment_id={data.get('payment_id')}")
                return True
            else:
                self._log(SagaStep.RESERVE_PAYMENT, "failed", resp.text[:200])
                return False
        except Exception as e:
            self._log(SagaStep.RESERVE_PAYMENT, "failed", str(e))
            return False

    # ── Step 3: Reserve Shipping ──────────────────────────────────────────────

    def _reserve_shipping(self) -> bool:
        self._update_order(saga_step=SagaStep.RESERVE_SHIPPING)
        self._log(SagaStep.RESERVE_SHIPPING, "started")
        try:
            resp = requests.post(
                f"{SHIP_SERVICE_URL}/api/shipping/reserve/",
                json={
                    "order_id": str(self.order.id),
                    "customer_id": str(self.order.customer_id),
                    "address": {
                        "street": self.order.shipping_street,
                        "city": self.order.shipping_city,
                        "state": self.order.shipping_state,
                        "postal_code": self.order.shipping_postal_code,
                        "country": self.order.shipping_country,
                    },
                    "items": [
                        {"book_id": str(i.book_id), "quantity": i.quantity}
                        for i in self.order.items.all()
                    ],
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                self._update_order(
                    shipment_id=data.get("shipment_id"),
                    status=OrderStatus.SHIPPING_RESERVED,
                )
                self._log(SagaStep.RESERVE_SHIPPING, "succeeded", f"shipment_id={data.get('shipment_id')}")
                return True
            else:
                self._log(SagaStep.RESERVE_SHIPPING, "failed", resp.text[:200])
                return False
        except Exception as e:
            self._log(SagaStep.RESERVE_SHIPPING, "failed", str(e))
            return False

    # ── Step 4: Confirm Order ─────────────────────────────────────────────────

    def _confirm_order(self) -> bool:
        self._update_order(saga_step=SagaStep.CONFIRM_ORDER)
        self._log(SagaStep.CONFIRM_ORDER, "started")
        try:
            # Confirm payment
            if self.order.payment_id:
                requests.post(
                    f"{PAY_SERVICE_URL}/api/payments/{self.order.payment_id}/confirm/",
                    timeout=10,
                )
            # Confirm shipping
            if self.order.shipment_id:
                requests.post(
                    f"{SHIP_SERVICE_URL}/api/shipping/{self.order.shipment_id}/confirm/",
                    timeout=10,
                )

            self._update_order(status=OrderStatus.COMPLETED)
            self._log(SagaStep.CONFIRM_ORDER, "succeeded")
            return True
        except Exception as e:
            self._log(SagaStep.CONFIRM_ORDER, "failed", str(e))
            return False

    # ── Compensations ─────────────────────────────────────────────────────────

    def _compensate_payment(self):
        self._log(SagaStep.COMPENSATE_PAYMENT, "started")
        try:
            if self.order.payment_id:
                requests.post(
                    f"{PAY_SERVICE_URL}/api/payments/{self.order.payment_id}/cancel/",
                    timeout=10,
                )
            self._log(SagaStep.COMPENSATE_PAYMENT, "succeeded")
        except Exception as e:
            self._log(SagaStep.COMPENSATE_PAYMENT, "failed", str(e))

    def _compensate_shipping(self):
        self._log(SagaStep.COMPENSATE_SHIPPING, "started")
        try:
            if self.order.shipment_id:
                requests.post(
                    f"{SHIP_SERVICE_URL}/api/shipping/{self.order.shipment_id}/cancel/",
                    timeout=10,
                )
            self._log(SagaStep.COMPENSATE_SHIPPING, "succeeded")
        except Exception as e:
            self._log(SagaStep.COMPENSATE_SHIPPING, "failed", str(e))

    # ── Main Orchestration ────────────────────────────────────────────────────

    def execute(self) -> Order:
        """
        Execute the full Saga. Returns updated order.
        """
        logger.info(f"[Saga] Starting saga for order {self.order.id}")

        # Step 2: Reserve payment
        if not self._reserve_payment():
            self._update_order(
                status=OrderStatus.FAILED,
                failure_reason="Payment reservation failed",
            )
            return self.order

        # Step 3: Reserve shipping
        if not self._reserve_shipping():
            # Compensate payment
            self._compensate_payment()
            self._update_order(
                status=OrderStatus.FAILED,
                failure_reason="Shipping reservation failed",
            )
            return self.order

        # Step 4: Confirm order
        if not self._confirm_order():
            # Compensate both
            self._compensate_shipping()
            self._compensate_payment()
            self._update_order(
                status=OrderStatus.FAILED,
                failure_reason="Order confirmation failed",
            )
            return self.order

        logger.info(f"[Saga] Order {self.order.id} completed successfully")
        return self.order
