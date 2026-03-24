import logging, os, requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from .models import Manager

logger = logging.getLogger(__name__)

def get_payload(request):
    import jwt
    auth = request.META.get("HTTP_AUTHORIZATION","")
    if not auth.startswith("Bearer "): return None
    try: return jwt.decode(auth[7:], os.environ.get("JWT_SECRET_KEY","super-secret-jwt-key"), algorithms=["HS256"])
    except: return None

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = "__all__"

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "manager-service"})

@api_view(["GET","POST"])
@permission_classes([AllowAny])
def manager_list(request):
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["manager","admin"]:
        return Response({"error":"Forbidden"}, status=403)
    if request.method == "GET":
        return Response(ManagerSerializer(Manager.objects.all(), many=True).data)
    s = ManagerSerializer(data=request.data)
    if s.is_valid():
        return Response(ManagerSerializer(s.save()).data, status=201)
    return Response(s.errors, status=400)

@api_view(["GET"])
@permission_classes([AllowAny])
def dashboard(request):
    """High-level metrics aggregated from multiple services."""
    payload = get_payload(request)
    if not payload or payload.get("role") not in ["manager","admin"]:
        return Response({"error":"Forbidden"}, status=403)

    AUTH_URL   = os.environ.get("AUTH_SERVICE_URL","http://auth-service:8000")
    headers = {"Authorization": request.META.get("HTTP_AUTHORIZATION","")}

    metrics = {}
    services = {
        "auth":   (AUTH_URL, "/api/auth/users/"),
    }
    for name, (url, path) in services.items():
        try:
            r = requests.get(f"{url}{path}", headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                metrics[f"{name}_count"] = len(data) if isinstance(data, list) else data
        except Exception as e:
            metrics[f"{name}_error"] = str(e)

    return Response({"service": "manager-dashboard", "metrics": metrics})
