"""
Shared JWT authentication helpers used by all downstream services.
Validates tokens via the auth-service or locally with the shared secret.
"""
import logging
import os

import jwt
from django.http import JsonResponse
from functools import wraps

logger = logging.getLogger(__name__)

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def get_token_from_request(request) -> str | None:
    """Extract Bearer token from Authorization header."""
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def require_auth(roles: list[str] | None = None):
    """
    Decorator for DRF views to enforce JWT auth and optional RBAC.
    Usage:
        @require_auth(roles=["admin", "manager"])
        def my_view(request, *args, **kwargs): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            token = get_token_from_request(request)
            if not token:
                return JsonResponse({"error": "Authentication required"}, status=401)

            payload = decode_token(token)
            if not payload:
                return JsonResponse({"error": "Invalid or expired token"}, status=401)

            if roles and payload.get("role") not in roles:
                return JsonResponse(
                    {"error": f"Access denied. Required roles: {roles}"}, status=403
                )

            request.user_payload = payload
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class JWTAuthMiddleware:
    """
    Django middleware that sets request.user_payload from JWT.
    Does NOT block — just enriches the request object.
    Actual enforcement is done per-view with @require_auth.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = get_token_from_request(request)
        if token:
            request.user_payload = decode_token(token)
        else:
            request.user_payload = None
        return self.get_response(request)
