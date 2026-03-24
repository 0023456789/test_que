import logging, os, requests
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from .models import CatalogEntry

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")

class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogEntry
        fields = "__all__"

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "catalog-service"})

@api_view(["GET"])
@permission_classes([AllowAny])
def browse(request):
    """
    Full-featured catalog browse with search + multi-filter.
    Proxies through to book-service and enriches with catalog metadata.
    """
    params = {}
    q = request.query_params.get("q")
    if q:
        params["q"] = q
    category = request.query_params.get("category")
    if category:
        params["category"] = category
    min_price = request.query_params.get("min_price")
    if min_price:
        params["min_price"] = min_price
    max_price = request.query_params.get("max_price")
    if max_price:
        params["max_price"] = max_price
    in_stock = request.query_params.get("in_stock")
    if in_stock:
        params["in_stock"] = in_stock

    try:
        endpoint = "/api/books/search/" if q else "/api/books/"
        resp = requests.get(f"{BOOK_SERVICE_URL}{endpoint}", params=params, timeout=5)
        books = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        logger.error(f"Book service error: {e}")
        books = []

    # Sort options
    sort = request.query_params.get("sort", "newest")
    if sort == "price_asc":
        books.sort(key=lambda b: float(b.get("price", 0)))
    elif sort == "price_desc":
        books.sort(key=lambda b: float(b.get("price", 0)), reverse=True)
    elif sort == "rating":
        books.sort(key=lambda b: float(b.get("average_rating", 0)), reverse=True)
    elif sort == "title":
        books.sort(key=lambda b: b.get("title", ""))

    # Pagination
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 20))
    total = len(books)
    start = (page - 1) * page_size
    end = start + page_size

    return Response({
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "results": books[start:end],
    })

@api_view(["GET"])
@permission_classes([AllowAny])
def featured(request):
    """Return featured/promoted books."""
    try:
        resp = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=5)
        books = resp.json() if resp.status_code == 200 else []
        # Feature books with highest rating
        books.sort(key=lambda b: float(b.get("average_rating", 0)), reverse=True)
        return Response(books[:10])
    except Exception as e:
        return Response({"error": str(e)}, status=503)

@api_view(["GET"])
@permission_classes([AllowAny])
def categories(request):
    """Proxy category list from book-service."""
    try:
        resp = requests.get(f"{BOOK_SERVICE_URL}/api/books/categories/", timeout=5)
        return Response(resp.json() if resp.status_code == 200 else [])
    except Exception as e:
        return Response({"error": str(e)}, status=503)
