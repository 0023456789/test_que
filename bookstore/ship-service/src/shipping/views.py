import uuid, logging, os
from datetime import date, timedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from .models import Shipment, ShipmentItem, ShipmentStatus

logger = logging.getLogger(__name__)

class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = ["id", "book_id", "quantity"]

class ShipmentSerializer(serializers.ModelSerializer):
    items = ShipmentItemSerializer(many=True, read_only=True)
    class Meta:
        model = Shipment
        fields = "__all__"

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "ship-service"})

@api_view(["POST"])
@permission_classes([AllowAny])
def reserve_shipment(request):
    order_id    = request.data.get("order_id")
    customer_id = request.data.get("customer_id")
    address     = request.data.get("address", {})
    items       = request.data.get("items", [])
    if not order_id:
        return Response({"error": "order_id required"}, status=400)
    shipment = Shipment.objects.create(
        order_id=order_id, customer_id=customer_id,
        status=ShipmentStatus.RESERVED,
        tracking_number=f"TRK-{uuid.uuid4().hex[:10].upper()}",
        street=address.get("street",""), city=address.get("city",""),
        state=address.get("state",""), postal_code=address.get("postal_code",""),
        country=address.get("country","US"),
        estimated_delivery=date.today() + timedelta(days=7),
    )
    for item in items:
        ShipmentItem.objects.create(shipment=shipment, book_id=item["book_id"], quantity=item["quantity"])
    logger.info(f"Shipment reserved: {shipment.id} for order {order_id}")
    return Response({"shipment_id": str(shipment.id), "tracking_number": shipment.tracking_number, "status": shipment.status}, status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_shipment(request, shipment_id):
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if shipment.status != ShipmentStatus.RESERVED:
        return Response({"error": f"Cannot confirm in status {shipment.status}"}, status=400)
    shipment.status = ShipmentStatus.CONFIRMED
    shipment.save()
    return Response(ShipmentSerializer(shipment).data)

@api_view(["POST"])
@permission_classes([AllowAny])
def cancel_shipment(request, shipment_id):
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    shipment.status = ShipmentStatus.CANCELLED
    shipment.failure_reason = request.data.get("reason", "Cancelled by saga")
    shipment.save()
    return Response(ShipmentSerializer(shipment).data)

@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_shipment_status(request, shipment_id):
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    new_status = request.data.get("status")
    if new_status not in [s[0] for s in ShipmentStatus.choices]:
        return Response({"error": "Invalid status"}, status=400)
    shipment.status = new_status
    shipment.save()
    return Response(ShipmentSerializer(shipment).data)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_shipment(request, shipment_id):
    try:
        return Response(ShipmentSerializer(Shipment.objects.prefetch_related("items").get(id=shipment_id)).data)
    except Shipment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

@api_view(["GET"])
@permission_classes([AllowAny])
def list_shipments_for_order(request, order_id):
    return Response(ShipmentSerializer(Shipment.objects.filter(order_id=order_id), many=True).data)
