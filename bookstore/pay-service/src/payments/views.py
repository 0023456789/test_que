import uuid, logging, os
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from .models import Payment, PaymentStatus

logger = logging.getLogger(__name__)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "pay-service"})

@api_view(["POST"])
@permission_classes([AllowAny])
def reserve_payment(request):
    order_id    = request.data.get("order_id")
    customer_id = request.data.get("customer_id")
    amount      = request.data.get("amount")
    if not all([order_id, customer_id, amount]):
        return Response({"error": "order_id, customer_id, amount required"}, status=400)
    payment = Payment.objects.create(
        order_id=order_id, customer_id=customer_id,
        amount=amount, status=PaymentStatus.RESERVED,
        transaction_ref=f"TXN-{uuid.uuid4().hex[:12].upper()}"
    )
    logger.info(f"Payment reserved: {payment.id} for order {order_id}")
    return Response({"payment_id": str(payment.id), "status": payment.status, "transaction_ref": payment.transaction_ref}, status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if payment.status != PaymentStatus.RESERVED:
        return Response({"error": f"Cannot confirm payment in status {payment.status}"}, status=400)
    payment.status = PaymentStatus.CONFIRMED
    payment.save()
    logger.info(f"Payment confirmed: {payment.id}")
    return Response(PaymentSerializer(payment).data)

@api_view(["POST"])
@permission_classes([AllowAny])
def cancel_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    payment.status = PaymentStatus.CANCELLED
    payment.failure_reason = request.data.get("reason", "Cancelled by saga")
    payment.save()
    logger.info(f"Payment cancelled: {payment.id}")
    return Response(PaymentSerializer(payment).data)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_payment(request, payment_id):
    try:
        return Response(PaymentSerializer(Payment.objects.get(id=payment_id)).data)
    except Payment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

@api_view(["GET"])
@permission_classes([AllowAny])
def list_payments_for_order(request, order_id):
    payments = Payment.objects.filter(order_id=order_id)
    return Response(PaymentSerializer(payments, many=True).data)
