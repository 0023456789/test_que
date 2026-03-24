import json
import logging
import os

import pika
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.db import models as django_models
from .models import Book, Category, Author
from .serializers import (
    BookSerializer, BookListSerializer, CategorySerializer,
    AuthorSerializer, InventoryUpdateSerializer,
)

logger = logging.getLogger(__name__)
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key"), algorithms=["HS256"])
    except Exception:
        return None


def publish(routing_key, data):
    try:
        conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        ch = conn.channel()
        ch.exchange_declare(exchange="bookstore.events", exchange_type="topic", durable=True)
        ch.basic_publish(
            exchange="bookstore.events", routing_key=routing_key,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        conn.close()
    except Exception as e:
        logger.warning(f"Publish failed: {e}")


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "book-service"})


# ─── Books ────────────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def books(request):
    if request.method == "GET":
        qs = Book.objects.filter(is_active=True).select_related("category").prefetch_related("authors")
        # Filtering
        category = request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        min_price = request.query_params.get("min_price")
        if min_price:
            qs = qs.filter(price__gte=min_price)
        max_price = request.query_params.get("max_price")
        if max_price:
            qs = qs.filter(price__lte=max_price)
        in_stock = request.query_params.get("in_stock")
        if in_stock == "true":
            qs = qs.filter(stock_quantity__gt=0)
        return Response(BookListSerializer(qs, many=True).data)

    # POST — staff/manager only
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)

    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        book = serializer.save()
        publish("book.created", {"event": "book.created", "book_id": str(book.id), "title": book.title})
        return Response(BookSerializer(book).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def book_detail(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if request.method == "GET":
        return Response(BookSerializer(book).data)

    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)

    if request.method in ["PUT", "PATCH"]:
        serializer = BookSerializer(book, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            book = serializer.save()
            publish("book.updated", {"event": "book.updated", "book_id": str(book.id)})
            return Response(BookSerializer(book).data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        book.is_active = False
        book.save()
        return Response({"message": "Book deactivated"}, status=204)


@api_view(["POST"])
@permission_classes([AllowAny])
def update_inventory(request, book_id):
    """Staff endpoint for adjusting stock levels."""
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    serializer = InventoryUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    qty = serializer.validated_data["quantity"]
    op = serializer.validated_data["operation"]

    if op == "add":
        book.stock_quantity += qty
    elif op == "subtract":
        book.stock_quantity = max(0, book.stock_quantity - qty)
    elif op == "set":
        book.stock_quantity = max(0, qty)

    book.save(update_fields=["stock_quantity"])
    publish("book.inventory.updated", {
        "event": "book.inventory.updated",
        "book_id": str(book.id),
        "stock_quantity": book.stock_quantity,
    })
    return Response({"book_id": str(book.id), "stock_quantity": book.stock_quantity})


@api_view(["POST"])
@permission_classes([AllowAny])
def reserve_stock(request, book_id):
    """Internal: reserve stock for an order."""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    qty = request.data.get("quantity", 1)
    if book.reserve_stock(qty):
        return Response({"reserved": True, "available_quantity": book.available_quantity})
    return Response({"reserved": False, "error": "Insufficient stock"}, status=409)


@api_view(["POST"])
@permission_classes([AllowAny])
def release_stock(request, book_id):
    """Internal: release reserved stock (compensation)."""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    qty = request.data.get("quantity", 1)
    book.release_stock(qty)
    return Response({"released": True})


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_book_stats(request, book_id):
    """Internal: update denormalized rating stats."""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    book.average_rating = request.data.get("average_rating", book.average_rating)
    book.total_reviews = request.data.get("total_reviews", book.total_reviews)
    book.save(update_fields=["average_rating", "total_reviews"])
    return Response({"updated": True})


# ─── Categories ───────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def categories(request):
    if request.method == "GET":
        return Response(CategorySerializer(Category.objects.all(), many=True).data)
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        return Response(CategorySerializer(serializer.save()).data, status=201)
    return Response(serializer.errors, status=400)


# ─── Authors ──────────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def authors(request):
    if request.method == "GET":
        return Response(AuthorSerializer(Author.objects.all(), many=True).data)
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)
    serializer = AuthorSerializer(data=request.data)
    if serializer.is_valid():
        return Response(AuthorSerializer(serializer.save()).data, status=201)
    return Response(serializer.errors, status=400)


# ─── Search ───────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def search_books(request):
    q = request.query_params.get("q", "").strip()
    if not q:
        return Response({"error": "Query parameter 'q' is required"}, status=400)

    qs = Book.objects.filter(is_active=True).select_related("category").prefetch_related("authors")
    qs = qs.filter(
        django_models.Q(title__icontains=q) |
        django_models.Q(isbn__icontains=q) |
        django_models.Q(description__icontains=q) |
        django_models.Q(authors__name__icontains=q) |
        django_models.Q(publisher__icontains=q)
    ).distinct()

    return Response(BookListSerializer(qs, many=True).data)
