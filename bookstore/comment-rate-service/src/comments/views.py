import logging, os, requests
from django.http import JsonResponse
from django.db.models import Avg, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from .models import Rating, Comment

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL  = os.environ.get("BOOK_SERVICE_URL",  "http://book-service:8000")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8000")

def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION","")
    if not auth.startswith("Bearer "): return None
    try: return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY","super-secret-jwt-key"), algorithms=["HS256"])
    except: return None

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id","book_id","customer_id","score","created_at"]
        read_only_fields = ["id","customer_id","created_at"]

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id","book_id","customer_id","author_name","body","is_verified_purchase","is_approved","created_at"]
        read_only_fields = ["id","customer_id","is_verified_purchase","created_at"]

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status":"healthy","service":"comment-rate-service"})

@api_view(["GET","POST"])
@permission_classes([AllowAny])
def book_ratings(request, book_id):
    if request.method == "GET":
        ratings = Rating.objects.filter(book_id=book_id)
        agg = ratings.aggregate(avg=Avg("score"), count=Count("id"))
        return Response({
            "book_id": str(book_id),
            "average_score": round(agg["avg"] or 0, 2),
            "total_ratings": agg["count"],
            "ratings": RatingSerializer(ratings, many=True).data,
        })

    payload = get_payload(request)
    if not payload: return Response({"error":"Unauthorized"}, status=401)

    data = {**request.data, "book_id": str(book_id)}
    existing = Rating.objects.filter(book_id=book_id, customer_id=payload["user_id"]).first()
    if existing:
        s = RatingSerializer(existing, data=data, partial=True)
    else:
        s = RatingSerializer(data=data)

    if not s.is_valid():
        return Response(s.errors, status=400)

    rating = s.save(customer_id=payload["user_id"], book_id=book_id)

    # Push updated stats to book-service
    try:
        agg = Rating.objects.filter(book_id=book_id).aggregate(avg=Avg("score"), count=Count("id"))
        requests.patch(
            f"{BOOK_SERVICE_URL}/api/books/{book_id}/stats/",
            json={"average_rating": round(agg["avg"] or 0, 2), "total_reviews": agg["count"]},
            timeout=3,
        )
    except Exception as e:
        logger.warning(f"Could not update book stats: {e}")

    return Response(RatingSerializer(rating).data, status=201)

@api_view(["GET","POST"])
@permission_classes([AllowAny])
def book_comments(request, book_id):
    if request.method == "GET":
        comments = Comment.objects.filter(book_id=book_id, is_approved=True)
        return Response(CommentSerializer(comments, many=True).data)

    payload = get_payload(request)
    if not payload: return Response({"error":"Unauthorized"}, status=401)

    # Check for verified purchase
    is_verified = False
    try:
        r = requests.get(
            f"{ORDER_SERVICE_URL}/api/orders/",
            headers={"Authorization": request.META.get("HTTP_AUTHORIZATION","")},
            timeout=3,
        )
        if r.status_code == 200:
            orders = r.json()
            is_verified = any(
                any(str(item.get("book_id")) == str(book_id) for item in o.get("items", []))
                and o.get("status") == "completed"
                for o in orders
            )
    except Exception:
        pass

    data = {**request.data, "book_id": str(book_id)}
    s = CommentSerializer(data=data)
    if not s.is_valid():
        return Response(s.errors, status=400)

    comment = s.save(
        customer_id=payload["user_id"],
        book_id=book_id,
        author_name=f"{payload.get('first_name','')} {payload.get('last_name','')}".strip(),
        is_verified_purchase=is_verified,
    )
    return Response(CommentSerializer(comment).data, status=201)

@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_comment(request, comment_id):
    payload = get_payload(request)
    if not payload: return Response({"error":"Unauthorized"}, status=401)
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error":"Not found"}, status=404)
    if str(payload.get("user_id")) != str(comment.customer_id) and payload.get("role") not in ["admin","manager"]:
        return Response({"error":"Forbidden"}, status=403)
    comment.delete()
    return Response({"message":"Deleted"})
