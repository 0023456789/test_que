import logging
import os
import threading
import requests
from decimal import Decimal

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers

from .models import Order, OrderItem, SagaLog, OrderStatus
from .saga import SagaOrchestrator

logger = logging.getLogger(__name__)
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")


def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key"), algorithms=["HS256"])
    except Exception:
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    class Meta:
        model = OrderItem
        fields = ["id", "book_id", "book_title", "book_isbn", "unit_price", "quantity", "subtotal"]


class SagaLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagaLog
        fields = ["step", "status", "message", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    saga_logs = SagaLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "customer_id", "status",
            "shipping_street", "shipping_city", "shipping_state",
            "shipping_postal_code", "shipping_country",
            "subtotal", "shipping_fee", "total_amount",
            "payment_id", "shipment_id",
            "saga_step", "failure_reason",
            "items", "saga_logs",
            "created_at", "updated_at",
        ]


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "order-service"})


@api_view(["POST"])
@permission_classes([AllowAny])
def create_order(request):
    """
    Checkout endpoint. Triggers Saga Orchestration.
    Expects: { cart_id, shipping_address: {...} }
    """
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    if payload.get("role") != "customer" and payload.get("role") not in ["admin"]:
        return Response({"error": "Only customers can place orders"}, status=403)

    cart_id = request.data.get("cart_id")
    shipping = request.data.get("shipping_address", {})

    if not cart_id:
        return Response({"error": "cart_id required"}, status=400)

    # Fetch cart
    try:
        resp = requests.get(f"{CART_SERVICE_URL}/api/cart/by-id/{cart_id}/", timeout=5)
        if resp.status_code != 200:
            return Response({"error": "Cart not found"}, status=404)
        cart = resp.json()
    except Exception as e:
        return Response({"error": f"Cart service unavailable: {e}"}, status=503)

    if not cart.get("items"):
        return Response({"error": "Cart is empty"}, status=400)

    # Create order record (Step 1)
    subtotal = Decimal(str(cart["total_price"]))
    shipping_fee = Decimal("5.00")
    total = subtotal + shipping_fee

    order = Order.objects.create(
        customer_id=payload["user_id"],
        cart_id=cart_id,
        status=OrderStatus.PENDING,
        shipping_street=shipping.get("street", ""),
        shipping_city=shipping.get("city", ""),
        shipping_state=shipping.get("state", ""),
        shipping_postal_code=shipping.get("postal_code", ""),
        shipping_country=shipping.get("country", "US"),
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=total,
    )

    for item in cart["items"]:
        OrderItem.objects.create(
            order=order,
            book_id=item["book_id"],
            book_title=item["book_title"],
            book_isbn=item.get("book_isbn", ""),
            unit_price=item["unit_price"],
            quantity=item["quantity"],
        )

    # Run saga in background thread (non-blocking response)
    def run_saga():
        SagaOrchestrator(order).execute()

    thread = threading.Thread(target=run_saga, daemon=True)
    thread.start()

    return Response(OrderSerializer(order).data, status=202)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_orders(request):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)

    if payload.get("role") in ["admin", "manager"]:
        orders = Order.objects.all().prefetch_related("items", "saga_logs").order_by("-created_at")
    else:
        orders = Order.objects.filter(customer_id=payload["user_id"]).prefetch_related("items", "saga_logs").order_by("-created_at")

    return Response(OrderSerializer(orders, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_order(request, order_id):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)

    try:
        order = Order.objects.prefetch_related("items", "saga_logs").get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if str(payload.get("user_id")) != str(order.customer_id) and payload.get("role") not in ["admin", "manager"]:
        return Response({"error": "Forbidden"}, status=403)

    return Response(OrderSerializer(order).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def cancel_order(request, order_id):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if str(payload.get("user_id")) != str(order.customer_id) and payload.get("role") != "admin":
        return Response({"error": "Forbidden"}, status=403)

    if order.status == OrderStatus.COMPLETED:
        return Response({"error": "Cannot cancel completed order"}, status=400)

    # Trigger compensations
    def compensate():
        orchestrator = SagaOrchestrator(order)
        if order.shipment_id:
            orchestrator._compensate_shipping()
        if order.payment_id:
            orchestrator._compensate_payment()
        order.status = OrderStatus.CANCELLED
        order.save()

    threading.Thread(target=compensate, daemon=True).start()
    return Response({"message": "Cancellation initiated", "order_id": str(order_id)})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_order_status(request, order_id):
    """Lightweight polling endpoint for saga status."""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    return Response({
        "order_id": str(order.id),
        "status": order.status,
        "saga_step": order.saga_step,
        "failure_reason": order.failure_reason,
    })
