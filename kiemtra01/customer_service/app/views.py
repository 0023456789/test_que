import json
import uuid
from datetime import timedelta
from decimal import Decimal
from urllib import error, parse, request as urlrequest

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Cart, CartItem, CustomerSession, CustomerUser, Order, OrderItem


SERVICE_CATALOG_ROUTES = {
	"computer": ("PRODUCT_SERVICE_URL", "/products/", "?category=computer"),
	"mobile": ("PRODUCT_SERVICE_URL", "/products/", "?category=mobile"),
	"tablet": ("PRODUCT_SERVICE_URL", "/products/", "?category=tablet"),
	"monitor": ("PRODUCT_SERVICE_URL", "/products/", "?category=monitor"),
	"keyboard": ("PRODUCT_SERVICE_URL", "/products/", "?category=keyboard"),
	"mouse": ("PRODUCT_SERVICE_URL", "/products/", "?category=mouse"),
	"headphone": ("PRODUCT_SERVICE_URL", "/products/", "?category=headphone"),
	"speaker": ("PRODUCT_SERVICE_URL", "/products/", "?category=speaker"),
	"camera": ("PRODUCT_SERVICE_URL", "/products/", "?category=camera"),
	"printer": ("PRODUCT_SERVICE_URL", "/products/", "?category=printer"),
}


def _json_body(request):
	if not request.body:
		return {}
	try:
		return json.loads(request.body.decode("utf-8"))
	except json.JSONDecodeError:
		return None


def _get_token(request):
	auth = request.headers.get("Authorization", "")
	if auth.startswith("Bearer "):
		return auth.replace("Bearer ", "", 1).strip()
	return request.headers.get("X-Customer-Token", "").strip()


def _authenticate_customer(request):
	token = _get_token(request)
	if not token:
		return None
	session = CustomerSession.objects.filter(
		token=token,
		expires_at__gt=timezone.now(),
	).select_related("customer").first()
	if not session:
		return None
	return session.customer


def _service_request(method, base_url, path, payload=None, query_params=None):
	url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
	if query_params:
		url = f"{url}?{parse.urlencode(query_params)}"

	data = None
	headers = {"Content-Type": "application/json"}
	if payload is not None:
		data = json.dumps(payload).encode("utf-8")

	req = urlrequest.Request(url=url, data=data, headers=headers, method=method.upper())
	try:
		with urlrequest.urlopen(req, timeout=15) as response:
			body = response.read().decode("utf-8")
			parsed = json.loads(body) if body else {}
			return response.status, parsed
	except error.HTTPError as exc:
		body = exc.read().decode("utf-8") if exc.fp else ""
		try:
			parsed = json.loads(body) if body else {"error": exc.reason}
		except json.JSONDecodeError:
			parsed = {"error": body or exc.reason}
		return exc.code, parsed
	except Exception as exc:
		return 503, {"error": f"Service unreachable: {exc}"}


def _serialize_cart(cart):
	items = []
	total = Decimal("0")
	for item in cart.items.all():
		line_total = item.unit_price * item.quantity
		total += line_total
		items.append(
			{
				"id": item.id,
				"item_type": item.item_type,
				"item_id": item.item_id,
				"item_name": item.item_name,
				"unit_price": float(item.unit_price),
				"quantity": item.quantity,
				"line_total": float(line_total),
			}
		)
	return {
		"id": cart.id,
		"customer_id": cart.customer_id,
		"status": cart.status,
		"items": items,
		"total_amount": float(total),
		"updated_at": cart.updated_at.isoformat(),
	}


def _serialize_order(order):
	items = []
	for item in order.items.all():
		items.append(
			{
				"item_type": item.item_type,
				"item_id": item.item_id,
				"item_name": item.item_name,
				"unit_price": float(item.unit_price),
				"quantity": item.quantity,
			}
		)
	return {
		"id": order.id,
		"customer_id": order.customer_id,
		"status": order.status,
		"shipping_address": order.shipping_address,
		"total_amount": float(order.total_amount),
		"created_at": order.created_at.isoformat(),
		"items": items,
	}


def _fetch_catalog(query_params):
	results = []
	for item_type, (setting_name, route, query_suffix) in SERVICE_CATALOG_ROUTES.items():
		base_url = getattr(settings, setting_name, "")
		if not base_url:
			continue

		status_code, payload = _service_request(
			"GET",
			base_url,
			f"{route}{query_suffix}",
			query_params=query_params,
		)
		if 200 <= status_code < 300:
			for item in payload.get("items", []):
				item["item_type"] = item_type
				results.append(item)

	return results


def _fetch_item_detail(item_type, item_id):
	route_info = SERVICE_CATALOG_ROUTES.get(item_type)
	if not route_info:
		return None

	setting_name, route_prefix, _ = route_info
	base_url = getattr(settings, setting_name, "")
	if not base_url:
		return None

	status_code, data = _service_request("GET", base_url, f"{route_prefix}{item_id}/")

	if status_code < 200 or status_code >= 300:
		return None
	return data.get("item")


def _update_item_stock(item_type, item_id, new_stock):
	payload = {"stock": new_stock}
	route_info = SERVICE_CATALOG_ROUTES.get(item_type)
	if not route_info:
		return False

	setting_name, route_prefix, _ = route_info
	base_url = getattr(settings, setting_name, "")
	if not base_url:
		return False

	status_code, _data = _service_request(
		"PATCH",
		base_url,
		f"{route_prefix}{item_id}/",
		payload=payload,
	)
	return 200 <= status_code < 300


@csrf_exempt
@require_http_methods(["POST"])
def register_customer(request):
	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	required = ["username", "password", "full_name", "email"]
	for key in required:
		if not payload.get(key):
			return JsonResponse({"error": f"Missing field: {key}"}, status=400)

	if CustomerUser.objects.filter(username=payload["username"]).exists():
		return JsonResponse({"error": "Username already exists."}, status=409)

	if CustomerUser.objects.filter(email=payload["email"]).exists():
		return JsonResponse({"error": "Email already exists."}, status=409)

	customer = CustomerUser.objects.create(
		username=payload["username"],
		password_hash=make_password(payload["password"]),
		full_name=payload["full_name"],
		email=payload["email"],
	)
	return JsonResponse(
		{
			"customer": {
				"id": customer.id,
				"username": customer.username,
				"full_name": customer.full_name,
				"email": customer.email,
			}
		},
		status=201,
	)


@csrf_exempt
@require_http_methods(["POST"])
def login_customer(request):
	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	username = payload.get("username", "")
	password = payload.get("password", "")
	customer = CustomerUser.objects.filter(username=username).first()

	if not customer or not check_password(password, customer.password_hash):
		return JsonResponse({"error": "Invalid credentials."}, status=401)

	token = uuid.uuid4().hex
	expires_at = timezone.now() + timedelta(hours=12)
	CustomerSession.objects.create(customer=customer, token=token, expires_at=expires_at)

	return JsonResponse(
		{
			"token": token,
			"expires_at": expires_at.isoformat(),
			"customer": {
				"id": customer.id,
				"username": customer.username,
				"full_name": customer.full_name,
				"email": customer.email,
			},
		}
	)


@require_http_methods(["GET"])
def browse_catalog(request):
	params = {
		"q": request.GET.get("q", ""),
		"brand": request.GET.get("brand", ""),
		"min_price": request.GET.get("min_price", ""),
		"max_price": request.GET.get("max_price", ""),
		"in_stock": request.GET.get("in_stock", ""),
	}
	params = {k: v for k, v in params.items() if v != ""}

	items = _fetch_catalog(params)

	item_type = request.GET.get("item_type")
	if item_type in SERVICE_CATALOG_ROUTES:
		items = [item for item in items if item.get("item_type") == item_type]

	return JsonResponse({"items": items})


@require_http_methods(["GET"])
def search_catalog(request):
	params = {
		"q": request.GET.get("q", ""),
		"brand": request.GET.get("brand", ""),
		"min_price": request.GET.get("min_price", ""),
		"max_price": request.GET.get("max_price", ""),
		"in_stock": request.GET.get("in_stock", ""),
	}
	params = {k: v for k, v in params.items() if v != ""}
	items = _fetch_catalog(params)
	return JsonResponse({"items": items})


def _get_or_create_active_cart(customer):
	cart = Cart.objects.filter(customer=customer, status="active").first()
	if cart:
		return cart
	return Cart.objects.create(customer=customer, status="active")


@csrf_exempt
@require_http_methods(["POST"])
def create_cart(request):
	customer = _authenticate_customer(request)
	if not customer:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	cart = _get_or_create_active_cart(customer)
	return JsonResponse({"cart": _serialize_cart(cart)}, status=201)


@require_http_methods(["GET"])
def get_current_cart(request):
	customer = _authenticate_customer(request)
	if not customer:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	cart = _get_or_create_active_cart(customer)
	return JsonResponse({"cart": _serialize_cart(cart)})


@csrf_exempt
@require_http_methods(["POST"])
def add_cart_item(request):
	customer = _authenticate_customer(request)
	if not customer:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	item_type = payload.get("item_type")
	item_id = payload.get("item_id")
	quantity = int(payload.get("quantity", 1))

	if item_type not in SERVICE_CATALOG_ROUTES:
		return JsonResponse({"error": f"Invalid item_type. Allowed types: {', '.join(SERVICE_CATALOG_ROUTES.keys())}"}, status=400)
	if not item_id or quantity <= 0:
		return JsonResponse({"error": "item_id and quantity must be valid."}, status=400)

	item_data = _fetch_item_detail(item_type, item_id)
	if not item_data:
		return JsonResponse({"error": "Item not found."}, status=404)

	if int(item_data.get("stock", 0)) < quantity:
		return JsonResponse({"error": "Not enough stock."}, status=400)

	cart = _get_or_create_active_cart(customer)
	cart_item = CartItem.objects.filter(cart=cart, item_type=item_type, item_id=item_id).first()
	if cart_item:
		new_qty = cart_item.quantity + quantity
		if int(item_data.get("stock", 0)) < new_qty:
			return JsonResponse({"error": "Not enough stock for requested quantity."}, status=400)
		cart_item.quantity = new_qty
		cart_item.unit_price = Decimal(str(item_data.get("price", 0)))
		cart_item.item_name = item_data.get("name", "Unknown")
		cart_item.save()
	else:
		CartItem.objects.create(
			cart=cart,
			item_type=item_type,
			item_id=item_id,
			item_name=item_data.get("name", "Unknown"),
			unit_price=Decimal(str(item_data.get("price", 0))),
			quantity=quantity,
		)

	cart.refresh_from_db()
	return JsonResponse({"cart": _serialize_cart(cart)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def purchase_order(request):
	customer = _authenticate_customer(request)
	if not customer:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	shipping_address = payload.get("shipping_address", "")
	if not shipping_address:
		return JsonResponse({"error": "shipping_address is required."}, status=400)

	cart = Cart.objects.filter(customer=customer, status="active").prefetch_related("items").first()
	if not cart:
		return JsonResponse({"error": "No active cart."}, status=400)

	cart_items = list(cart.items.all())
	if not cart_items:
		return JsonResponse({"error": "Cart is empty."}, status=400)

	for cart_item in cart_items:
		item_data = _fetch_item_detail(cart_item.item_type, cart_item.item_id)
		if not item_data:
			return JsonResponse({"error": f"Item unavailable: {cart_item.item_type} #{cart_item.item_id}"}, status=400)
		if int(item_data.get("stock", 0)) < cart_item.quantity:
			return JsonResponse(
				{"error": f"Not enough stock for {cart_item.item_name}"},
				status=400,
			)

	with transaction.atomic():
		total = sum((item.unit_price * item.quantity for item in cart_items), Decimal("0"))
		order = Order.objects.create(
			customer=customer,
			total_amount=total,
			status="created",
			shipping_address=shipping_address,
		)

		for cart_item in cart_items:
			OrderItem.objects.create(
				order=order,
				item_type=cart_item.item_type,
				item_id=cart_item.item_id,
				item_name=cart_item.item_name,
				unit_price=cart_item.unit_price,
				quantity=cart_item.quantity,
			)

		cart.status = "ordered"
		cart.save()

	for cart_item in cart_items:
		current_item = _fetch_item_detail(cart_item.item_type, cart_item.item_id)
		if current_item:
			new_stock = int(current_item.get("stock", 0)) - cart_item.quantity
			_update_item_stock(cart_item.item_type, cart_item.item_id, max(new_stock, 0))

	return JsonResponse(
		{
			"order": {
				"id": order.id,
				"customer_id": order.customer_id,
				"total_amount": float(order.total_amount),
				"status": order.status,
				"shipping_address": order.shipping_address,
				"created_at": order.created_at.isoformat(),
			}
		},
		status=201,
	)


@require_http_methods(["GET"])
def recent_orders(request):
	customer = _authenticate_customer(request)
	if not customer:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	limit = request.GET.get("limit", "5")
	try:
		limit_int = max(1, min(int(limit), 10))
	except ValueError:
		limit_int = 5

	orders = (
		Order.objects.filter(customer=customer)
		.prefetch_related("items")
		.order_by("-created_at")[:limit_int]
	)
	return JsonResponse({"orders": [_serialize_order(order) for order in orders]})
