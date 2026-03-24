import logging
import os
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers

from .models import Cart, CartItem

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key"), algorithms=["HS256"])
    except Exception:
        return None


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "book_id", "book_title", "book_isbn", "unit_price", "quantity", "subtotal", "added_at"]
        read_only_fields = ["id", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "customer_id", "items", "total_price", "total_items", "updated_at"]


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "cart-service"})


@api_view(["POST"])
@permission_classes([AllowAny])
def create_cart_internal(request):
    """Internal endpoint — called by customer-service on registration."""
    customer_id = request.data.get("customer_id")
    if not customer_id:
        return Response({"error": "customer_id required"}, status=400)
    cart, created = Cart.objects.get_or_create(customer_id=customer_id)
    return Response(CartSerializer(cart).data, status=201 if created else 200)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart(request, customer_id):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    if str(payload.get("user_id")) != str(customer_id) and payload.get("role") not in ["admin", "manager"]:
        return Response({"error": "Forbidden"}, status=403)

    try:
        cart = Cart.objects.prefetch_related("items").get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)
    return Response(CartSerializer(cart).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_item(request, customer_id):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    if str(payload.get("user_id")) != str(customer_id) and payload.get("role") != "admin":
        return Response({"error": "Forbidden"}, status=403)

    try:
        cart = Cart.objects.get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)

    book_id = request.data.get("book_id")
    quantity = int(request.data.get("quantity", 1))

    if not book_id:
        return Response({"error": "book_id required"}, status=400)

    # Fetch book info
    try:
        resp = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=5)
        if resp.status_code != 200:
            return Response({"error": "Book not found"}, status=404)
        book = resp.json()
    except Exception as e:
        return Response({"error": f"Book service unavailable: {e}"}, status=503)

    if book.get("available_quantity", 0) < quantity:
        return Response({"error": "Insufficient stock"}, status=409)

    item, created = CartItem.objects.get_or_create(
        cart=cart, book_id=book_id,
        defaults={
            "book_title": book["title"],
            "book_isbn": book.get("isbn", ""),
            "unit_price": book["price"],
            "quantity": quantity,
        }
    )
    if not created:
        item.quantity += quantity
        item.unit_price = book["price"]  # refresh price
        item.save()

    return Response(CartSerializer(cart).data)


@api_view(["PATCH", "DELETE"])
@permission_classes([AllowAny])
def update_item(request, customer_id, item_id):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    if str(payload.get("user_id")) != str(customer_id) and payload.get("role") != "admin":
        return Response({"error": "Forbidden"}, status=403)

    try:
        cart = Cart.objects.get(customer_id=customer_id)
        item = CartItem.objects.get(id=item_id, cart=cart)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({"error": "Not found"}, status=404)

    if request.method == "DELETE":
        item.delete()
        return Response({"message": "Item removed"})

    quantity = request.data.get("quantity")
    if quantity is not None:
        qty = int(quantity)
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()
    return Response(CartSerializer(cart).data)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def clear_cart(request, customer_id):
    payload = get_payload(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)
    if str(payload.get("user_id")) != str(customer_id) and payload.get("role") != "admin":
        return Response({"error": "Forbidden"}, status=403)

    try:
        cart = Cart.objects.get(customer_id=customer_id)
        cart.items.all().delete()
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)

    return Response({"message": "Cart cleared"})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart_by_id(request, cart_id):
    """Internal: get cart by cart UUID (for order service)."""
    try:
        cart = Cart.objects.prefetch_related("items").get(id=cart_id)
    except Cart.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(CartSerializer(cart).data)
