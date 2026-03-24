import logging
import os
import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Customer, Address
from .serializers import CustomerSerializer, CustomerCreateSerializer, AddressSerializer
from .event_handlers import publish_customer_registered

logger = logging.getLogger(__name__)
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")


def get_user_from_token(request):
    import jwt, os
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key"), algorithms=["HS256"])
    except Exception:
        return None


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "customer-service"})


@api_view(["POST"])
@permission_classes([AllowAny])
def create_customer(request):
    """Called internally after auth registration, or directly."""
    serializer = CustomerCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    if Customer.objects.filter(user_id=serializer.validated_data["user_id"]).exists():
        return Response({"error": "Customer already exists"}, status=409)

    customer = serializer.save()

    # Auto-create cart via cart-service
    try:
        requests.post(
            f"{CART_SERVICE_URL}/api/cart/internal/create/",
            json={"customer_id": str(customer.id)},
            timeout=5,
        )
        logger.info(f"Cart created for customer {customer.id}")
    except Exception as e:
        logger.warning(f"Could not auto-create cart: {e}")

    publish_customer_registered(customer)
    return Response(CustomerSerializer(customer).data, status=201)


@api_view(["GET"])
def get_customer(request, customer_id):
    payload = get_user_from_token(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if str(payload.get("user_id")) != str(customer.user_id) and payload.get("role") not in ["admin", "manager"]:
        return Response({"error": "Forbidden"}, status=403)

    return Response(CustomerSerializer(customer).data)


@api_view(["GET"])
def get_my_profile(request):
    payload = get_user_from_token(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    try:
        customer = Customer.objects.get(user_id=payload["user_id"])
        return Response(CustomerSerializer(customer).data)
    except Customer.DoesNotExist:
        return Response({"error": "Customer profile not found"}, status=404)


@api_view(["PATCH"])
def update_customer(request, customer_id):
    payload = get_user_from_token(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if str(payload.get("user_id")) != str(customer.user_id) and payload.get("role") != "admin":
        return Response({"error": "Forbidden"}, status=403)

    serializer = CustomerSerializer(customer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["GET", "POST"])
def addresses(request, customer_id):
    payload = get_user_from_token(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if str(payload.get("user_id")) != str(customer.user_id) and payload.get("role") != "admin":
        return Response({"error": "Forbidden"}, status=403)

    if request.method == "GET":
        return Response(AddressSerializer(customer.addresses.all(), many=True).data)

    serializer = AddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(customer=customer)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def list_customers(request):
    """Admin/manager only."""
    payload = get_user_from_token(request)
    if not payload or payload.get("role") not in ["admin", "manager"]:
        return Response({"error": "Forbidden"}, status=403)
    customers = Customer.objects.all()
    return Response(CustomerSerializer(customers, many=True).data)
