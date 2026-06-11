import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import ProductItem


def _json_body(request):
	if not request.body:
		return {}
	try:
		return json.loads(request.body.decode("utf-8"))
	except json.JSONDecodeError:
		return None


def _to_dict(item):
	data = {
		"id": item.id,
		"category": item.category,
		"name": item.name,
		"brand": item.brand,
		"ram_gb": item.ram_gb,
		"storage_gb": item.storage_gb,
		"price": float(item.price),
		"stock": item.stock,
		"description": item.description,
		"is_active": item.is_active,
		"created_at": item.created_at.isoformat(),
		"updated_at": item.updated_at.isoformat(),
	}
	if item.category == "mobile":
		data["chipset"] = item.cpu_or_chipset
	else:
		data["cpu"] = item.cpu_or_chipset
	return data


@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request):
	if request.method == "GET":
		queryset = ProductItem.objects.filter(is_active=True)

		category = request.GET.get("category")
		if category:
			queryset = queryset.filter(category=category)

		q = request.GET.get("q")
		if q:
			queryset = queryset.filter(name__icontains=q)

		brand = request.GET.get("brand")
		if brand:
			queryset = queryset.filter(brand__icontains=brand)

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

	category = payload.get("category", request.GET.get("category", "computer"))
	cpu_or_chipset = payload.get("chipset") if category == "mobile" else payload.get("cpu", "")

	required = ["name", "brand", "ram_gb", "storage_gb", "price", "stock"]
	for key in required:
		if key not in payload:
			return JsonResponse({"error": f"Missing field: {key}"}, status=400)

	item = ProductItem.objects.create(
		category=category,
		name=payload["name"],
		brand=payload["brand"],
		cpu_or_chipset=cpu_or_chipset,
		ram_gb=payload["ram_gb"],
		storage_gb=payload["storage_gb"],
		price=Decimal(str(payload["price"])),
		stock=payload["stock"],
		description=payload.get("description", ""),
		is_active=payload.get("is_active", True),
	)
	return JsonResponse({"item": _to_dict(item)}, status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "PUT"])
def product_detail(request, item_id):
	item = ProductItem.objects.filter(id=item_id).first()
	if not item:
		return JsonResponse({"error": "Product item not found."}, status=404)

	if request.method == "GET":
		return JsonResponse({"item": _to_dict(item)})

	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	editable_fields = [
		"category",
		"name",
		"brand",
		"ram_gb",
		"storage_gb",
		"price",
		"stock",
		"description",
		"is_active",
	]
	for key in editable_fields:
		if key in payload:
			value = payload[key]
			if key == "price":
				value = Decimal(str(value))
			setattr(item, key, value)
			
	if "cpu" in payload:
		item.cpu_or_chipset = payload["cpu"]
	elif "chipset" in payload:
		item.cpu_or_chipset = payload["chipset"]

	item.save()
	return JsonResponse({"item": _to_dict(item)})
