"""
API Gateway Middleware:
  1. RequestLoggingMiddleware  — structured request/response logging
  2. RateLimitMiddleware       — Redis-backed sliding window rate limiter
"""
import json
import logging
import time

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# ── Redis client (lazy) ───────────────────────────────────────────────────────
_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis unavailable, rate limiting disabled: {e}")
    return _redis_client


# ── Request Logging Middleware ────────────────────────────────────────────────

class RequestLoggingMiddleware:
    """Log every proxied request with method, path, status, and duration."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = round((time.monotonic() - start) * 1000, 2)

        # Parse JWT for user context (best-effort)
        user_info = "-"
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            try:
                import jwt
                payload = jwt.decode(
                    auth[7:], settings.JWT_SECRET_KEY,
                    algorithms=["HS256"],
                    options={"verify_exp": False},
                )
                user_info = f"{payload.get('email','?')}[{payload.get('role','?')}]"
            except Exception:
                pass

        logger.info(
            f"{request.method} {request.path} "
            f"status={response.status_code} "
            f"user={user_info} "
            f"duration={duration_ms}ms "
            f"ip={_get_client_ip(request)}"
        )
        return response


def _get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded.split(",")[0] if x_forwarded else request.META.get("REMOTE_ADDR", "?")


# ── Rate Limit Helper (used by gateway view) ──────────────────────────────────

def check_rate_limit(identifier: str) -> tuple[bool, int]:
    """
    Sliding-window rate limiter using Redis.
    Returns (allowed: bool, remaining: int).
    Falls back to allow-all if Redis is unavailable.
    """
    r = _get_redis()
    if r is None:
        return True, 999

    limit = settings.RATE_LIMIT_PER_MINUTE
    window = 60  # seconds
    key = f"rl:{identifier}"

    try:
        pipe = r.pipeline()
        now = time.time()
        window_start = now - window

        pipe.zremrangebyscore(key, "-inf", window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = pipe.execute()

        count = results[2]
        remaining = max(0, limit - count)
        return count <= limit, remaining
    except Exception as e:
        logger.warning(f"Rate limit Redis error: {e}")
        return True, 999
