"""
API Gateway — reverse proxy with:
  • JWT token validation (via auth-service or local decode)
  • RBAC enforcement per route
  • Rate limiting (Redis sliding window)
  • Request/response proxying with header forwarding
  • Health aggregation endpoint
"""
import logging
import os
import jwt
import requests

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .middleware import check_rate_limit, _get_client_ip

logger = logging.getLogger(__name__)

# ── Route Table ───────────────────────────────────────────────────────────────
# Each entry: (prefix, upstream_base, required_roles or None for public)
ROUTES = [
    # Auth — public
    ("/api/auth/",           settings.AUTH_SERVICE_URL,          None),
    # Catalog — public
    ("/api/catalog/",        settings.CATALOG_SERVICE_URL,       None),
    # Books — public read, restricted write (enforced downstream)
    ("/api/books/",          settings.BOOK_SERVICE_URL,          None),
    # Customers
    ("/api/customers/",      settings.CUSTOMER_SERVICE_URL,      None),
    # Cart
    ("/api/cart/",           settings.CART_SERVICE_URL,          ["customer", "admin"]),
    # Orders
    ("/api/orders/",         settings.ORDER_SERVICE_URL,         ["customer", "admin", "manager"]),
    # Payments (internal + manager)
    ("/api/payments/",       settings.PAY_SERVICE_URL,           ["admin", "manager"]),
    # Shipping
    ("/api/shipping/",       settings.SHIP_SERVICE_URL,          ["admin", "manager"]),
    # Reviews — public read
    ("/api/reviews/",        settings.COMMENT_RATE_SERVICE_URL,  None),
    # Recommendations — public + personalised
    ("/api/recommendations/",settings.RECOMMENDER_SERVICE_URL,   None),
    # Staff panel
    ("/api/staff/",          settings.STAFF_SERVICE_URL,         ["staff", "manager", "admin"]),
    # Manager panel
    ("/api/managers/",       settings.MANAGER_SERVICE_URL,       ["manager", "admin"]),
]

# ── JWT Validation ────────────────────────────────────────────────────────────

def validate_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token(request) -> str | None:
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    return auth[7:] if auth.startswith("Bearer ") else None


# ── Proxy Helper ──────────────────────────────────────────────────────────────

EXCLUDED_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade",
    "host",
}

def _build_upstream_headers(request, user_payload: dict | None) -> dict:
    headers = {}
    for key, val in request.META.items():
        if key.startswith("HTTP_"):
            header = key[5:].replace("_", "-").lower()
            if header not in EXCLUDED_HEADERS:
                headers[header] = val
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            headers[key.replace("_", "-").lower()] = val

    # Inject verified user claims as trusted headers for downstream services
    if user_payload:
        headers["x-user-id"]    = str(user_payload.get("user_id", ""))
        headers["x-user-email"] = str(user_payload.get("email", ""))
        headers["x-user-role"]  = str(user_payload.get("role", ""))

    headers["x-gateway"] = "bookstore-api-gateway"
    headers["x-real-ip"] = _get_client_ip(request)
    return headers


def proxy_request(upstream_url: str, request, user_payload: dict | None):
    """Forward the request to the upstream service and return its response."""
    headers = _build_upstream_headers(request, user_payload)

    # Read body once
    try:
        body = request.body
    except Exception:
        body = b""

    # Preserve query string
    qs = request.META.get("QUERY_STRING", "")
    url = f"{upstream_url}{'?' + qs if qs else ''}"

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=body,
            stream=False,
            timeout=30,
            allow_redirects=False,
        )
    except requests.exceptions.ConnectionError:
        return JsonResponse({"error": "Upstream service unavailable", "upstream": upstream_url}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Upstream service timed out"}, status=504)
    except Exception as e:
        return JsonResponse({"error": f"Gateway error: {str(e)}"}, status=502)

    # Build Django response
    django_resp = JsonResponse(
        resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"body": resp.text},
        status=resp.status_code,
        safe=False,
    )
    # Forward selected upstream headers
    for header in ["x-request-id", "content-type"]:
        if header in resp.headers:
            django_resp[header] = resp.headers[header]

    return django_resp


# ── Main Gateway View ─────────────────────────────────────────────────────────

def gateway(request, path=""):
    full_path = f"/{path}"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    client_ip = _get_client_ip(request)
    token = get_token(request)
    rl_key = token[:32] if token else client_ip  # per-token or per-IP

    allowed, remaining = check_rate_limit(rl_key)
    if not allowed:
        return JsonResponse(
            {"error": "Rate limit exceeded. Try again in 60 seconds."},
            status=429,
            headers={"X-RateLimit-Remaining": "0"},
        )

    # ── Route Matching ────────────────────────────────────────────────────────
    matched_upstream = None
    required_roles = None
    upstream_path = full_path

    for prefix, upstream_base, roles in ROUTES:
        if full_path.startswith(prefix):
            matched_upstream = upstream_base
            required_roles = roles
            upstream_path = full_path  # keep full path
            break

    if not matched_upstream:
        return JsonResponse({"error": f"No route for path: {full_path}"}, status=404)

    # ── Auth / RBAC ───────────────────────────────────────────────────────────
    user_payload = None

    if required_roles is not None:
        if not token:
            return JsonResponse({"error": "Authentication required"}, status=401)
        user_payload = validate_jwt(token)
        if not user_payload:
            return JsonResponse({"error": "Invalid or expired token"}, status=401)
        if user_payload.get("role") not in required_roles:
            return JsonResponse(
                {"error": f"Access denied. Required roles: {required_roles}"},
                status=403,
            )
    elif token:
        # Optional auth — enrich if token present
        user_payload = validate_jwt(token)

    # ── Proxy ─────────────────────────────────────────────────────────────────
    upstream_url = f"{matched_upstream}{upstream_path}"
    return proxy_request(upstream_url, request, user_payload)


# ── Utility Endpoints ─────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "api-gateway"})


@api_view(["GET"])
@permission_classes([AllowAny])
def aggregate_health(request):
    """Check health of all downstream services."""
    results = {}
    service_urls = {
        "auth":          settings.AUTH_SERVICE_URL,
        "customer":      settings.CUSTOMER_SERVICE_URL,
        "staff":         settings.STAFF_SERVICE_URL,
        "manager":       settings.MANAGER_SERVICE_URL,
        "catalog":       settings.CATALOG_SERVICE_URL,
        "book":          settings.BOOK_SERVICE_URL,
        "cart":          settings.CART_SERVICE_URL,
        "order":         settings.ORDER_SERVICE_URL,
        "ship":          settings.SHIP_SERVICE_URL,
        "pay":           settings.PAY_SERVICE_URL,
        "comment-rate":  settings.COMMENT_RATE_SERVICE_URL,
        "recommender":   settings.RECOMMENDER_SERVICE_URL,
    }
    overall = "healthy"
    for name, url in service_urls.items():
        try:
            r = requests.get(f"{url}/health/", timeout=3)
            results[name] = {"status": "healthy" if r.status_code == 200 else "degraded", "code": r.status_code}
            if r.status_code != 200:
                overall = "degraded"
        except Exception as e:
            results[name] = {"status": "unreachable", "error": str(e)}
            overall = "degraded"

    return JsonResponse({"overall": overall, "services": results})


@api_view(["GET"])
@permission_classes([AllowAny])
def list_routes(request):
    """Developer endpoint — list all registered routes."""
    return JsonResponse({
        "routes": [
            {"prefix": prefix, "upstream": base, "auth_required": roles is not None, "required_roles": roles}
            for prefix, base, roles in ROUTES
        ]
    })
