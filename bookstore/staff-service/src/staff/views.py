import logging, os, requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from .models import StaffMember, InventoryAction

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")

def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "): return None
    try:
        return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY","super-secret-jwt-key"), algorithms=["HS256"])
    except: return None

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = "__all__"

class InventoryActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAction
        fields = "__all__"

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "staff-service"})

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def staff_list(request):
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)
    if request.method == "GET":
        return Response(StaffSerializer(StaffMember.objects.all(), many=True).data)
    s = StaffSerializer(data=request.data)
    if s.is_valid():
        return Response(StaffSerializer(s.save()).data, status=201)
    return Response(s.errors, status=400)

@api_view(["POST"])
@permission_classes([AllowAny])
def adjust_inventory(request, book_id):
    """Staff adjusts book stock via book-service."""
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)

    action   = request.data.get("operation", "add")
    quantity = request.data.get("quantity", 0)
    note     = request.data.get("note", "")

    try:
        resp = requests.post(
            f"{BOOK_SERVICE_URL}/api/books/{book_id}/inventory/",
            json={"operation": action, "quantity": quantity},
            timeout=5,
        )
        if resp.status_code != 200:
            return Response({"error": resp.text}, status=resp.status_code)
    except Exception as e:
        return Response({"error": str(e)}, status=503)

    # Record audit trail
    try:
        staff = StaffMember.objects.get(user_id=payload["user_id"])
        InventoryAction.objects.create(staff=staff, book_id=book_id, action=action, quantity=quantity, note=note)
    except StaffMember.DoesNotExist:
        pass

    return Response({"message": "Inventory updated", "book_id": str(book_id)})

@api_view(["GET"])
@permission_classes([AllowAny])
def inventory_audit(request):
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)
    actions = InventoryAction.objects.select_related("staff").all()[:100]
    return Response(InventoryActionSerializer(actions, many=True).data)

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def manage_books(request):
    """Proxy book CRUD to book-service with staff auth."""
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["staff", "manager", "admin"]:
        return Response({"error": "Forbidden"}, status=403)
    headers = {"Authorization": request.META.get("HTTP_AUTHORIZATION", "")}
    if request.method == "GET":
        resp = requests.get(f"{BOOK_SERVICE_URL}/api/books/", headers=headers, timeout=5)
    else:
        resp = requests.post(f"{BOOK_SERVICE_URL}/api/books/", json=request.data, headers=headers, timeout=5)
    return Response(resp.json(), status=resp.status_code)
