import hashlib
import json
from django.core.cache import cache
from django.http import JsonResponse


class IdempotencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return self.get_response(request)

        idempotency_key = request.META.get("HTTP_IDEMPOTENCY_KEY")
        if not idempotency_key:
            return self.get_response(request)

        request_signature = hashlib.sha256(
            f"{request.method}:{request.path}:{request.body.decode('utf-8', errors='ignore')}".encode("utf-8")
        ).hexdigest()

        cache_key = f"idempotency:{idempotency_key}"
        cached = cache.get(cache_key)
        if cached:
            if cached.get("request_signature") != request_signature:
                return JsonResponse(
                    {"error": "Idempotency key already used with different payload"},
                    status=409,
                )
            return JsonResponse(cached.get("response_body", {}), status=cached.get("status_code", 200), safe=False)

        response = self.get_response(request)

        if response.status_code < 500:
            response_body = None
            if hasattr(response, "data"):
                response_body = response.data
            else:
                try:
                    response_body = json.loads(response.content.decode("utf-8"))
                except Exception:
                    response_body = {"detail": response.content.decode("utf-8", errors="ignore")}

            cache.set(
                cache_key,
                {
                    "request_signature": request_signature,
                    "status_code": int(response.status_code),
                    "response_body": response_body,
                },
                timeout=86400,
            )

        return response
