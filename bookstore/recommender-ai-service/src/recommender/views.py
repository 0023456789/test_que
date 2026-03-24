import logging, os
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .engine import collaborative_recommendations, content_based_recommendations, trending_recommendations

logger = logging.getLogger(__name__)

def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION","")
    if not auth.startswith("Bearer "): return None
    try: return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY","super-secret-jwt-key"), algorithms=["HS256"])
    except: return None

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status":"healthy","service":"recommender-ai-service"})

@api_view(["GET"])
@permission_classes([AllowAny])
def for_customer(request):
    """Personalised recommendations for the authenticated customer."""
    payload = get_payload(request)
    if not payload:
        return Response({"error":"Unauthorized"}, status=401)
    token = request.META.get("HTTP_AUTHORIZATION","").replace("Bearer ","")
    limit = int(request.query_params.get("limit", 10))
    recs  = collaborative_recommendations(str(payload["user_id"]), token, limit)
    return Response({"customer_id": payload["user_id"], "recommendations": recs})

@api_view(["GET"])
@permission_classes([AllowAny])
def similar_books(request, book_id):
    """Content-based: books similar to a given book."""
    limit = int(request.query_params.get("limit", 6))
    return Response({"book_id": str(book_id), "similar": content_based_recommendations(str(book_id), limit)})

@api_view(["GET"])
@permission_classes([AllowAny])
def trending(request):
    """Trending books — no auth required."""
    limit = int(request.query_params.get("limit", 10))
    return Response({"trending": trending_recommendations(limit)})
