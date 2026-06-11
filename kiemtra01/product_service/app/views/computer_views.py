import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models.computer import ComputerProduct


def _json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _to_dict(item):
    return {
        "id": item.id,
        "name": item.name,
        "brand": item.brand,
        "cpu": item.get_cpu_display(),
        "ram_gb": item.ram_gb,
        "storage_type": item.get_storage_type_display(),
        "storage_gb": item.storage_gb,
        "gpu": item.gpu,
        "display_size_inches": float(item.display_size_inches),
        "display_resolution": item.display_resolution,
        "refresh_rate_hz": item.refresh_rate_hz,
        "operating_system": item.get_operating_system_display() if item.operating_system else "",
        "has_touchscreen": item.has_touchscreen,
        "has_backlit_keyboard": item.has_backlit_keyboard,
        "has_fingerprint_reader": item.has_fingerprint_reader,
        "has_webcam": item.has_webcam,
        "battery_hours": float(item.battery_hours) if item.battery_hours else None,
        "ports": item.ports,
        "warranty_months": item.warranty_months,
        "price": float(item.price),
        "stock": item.stock,
        "description": item.description,
        "is_active": item.is_active,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def computers(request):
    if request.method == "GET":
        queryset = ComputerProduct.objects.filter(is_active=True)

        brand = request.GET.get("brand")
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        cpu = request.GET.get("cpu")
        if cpu:
            queryset = queryset.filter(cpu=cpu)

        min_ram = request.GET.get("min_ram_gb")
        if min_ram:
            queryset = queryset.filter(ram_gb__gte=min_ram)

        min_storage = request.GET.get("min_storage_gb")
        if min_storage:
            queryset = queryset.filter(storage_gb__gte=min_storage)

        min_price = request.GET.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = request.GET.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        in_stock = request.GET.get("in_stock")
        if in_stock in ["1", "true", "True"]:
            queryset = queryset.filter(stock__gt=0)

        items = [_to_dict(item) for item in queryset]
        return JsonResponse({"items": items})

    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    required = ["name", "brand", "cpu", "ram_gb", "storage_type", "storage_gb", "price"]
    for key in required:
        if key not in payload:
            return JsonResponse({"error": f"Missing field: {key}"}, status=400)

    item = ComputerProduct.objects.create(
        name=payload["name"],
        brand=payload["brand"],
        cpu=payload["cpu"],
        ram_gb=payload["ram_gb"],
        storage_type=payload["storage_type"],
        storage_gb=payload["storage_gb"],
        gpu=payload.get("gpu", ""),
        display_size_inches=Decimal(str(payload.get("display_size_inches", "15.6"))),
        display_resolution=payload.get("display_resolution", ""),
        refresh_rate_hz=payload.get("refresh_rate_hz"),
        operating_system=payload.get("operating_system", ""),
        has_touchscreen=payload.get("has_touchscreen", False),
        has_backlit_keyboard=payload.get("has_backlit_keyboard", False),
        has_fingerprint_reader=payload.get("has_fingerprint_reader", False),
        has_webcam=payload.get("has_webcam", True),
        battery_hours=Decimal(str(payload["battery_hours"])) if payload.get("battery_hours") else None,
        ports=payload.get("ports", ""),
        warranty_months=payload.get("warranty_months", 12),
        price=Decimal(str(payload["price"])),
        stock=payload.get("stock", 0),
        description=payload.get("description", ""),
        is_active=payload.get("is_active", True),
    )
    return JsonResponse({"item": _to_dict(item)}, status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "PUT", "DELETE"])
def computer_detail(request, item_id):
    item = ComputerProduct.objects.filter(id=item_id).first()
    if not item:
        return JsonResponse({"error": "Computer product not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"item": _to_dict(item)})

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"message": "Computer product deleted successfully."})

    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    editable_fields = [
        "name", "brand", "cpu", "ram_gb", "storage_type", "storage_gb",
        "gpu", "display_size_inches", "display_resolution", "refresh_rate_hz",
        "operating_system", "has_touchscreen", "has_backlit_keyboard",
        "has_fingerprint_reader", "has_webcam", "battery_hours", "ports",
        "warranty_months", "price", "stock", "description", "is_active"
    ]
    
    for key in editable_fields:
        if key in payload:
            value = payload[key]
            if key in ["price", "display_size_inches", "battery_hours"]:
                value = Decimal(str(value))
            setattr(item, key, value)

    item.save()
    return JsonResponse({"item": _to_dict(item)})
