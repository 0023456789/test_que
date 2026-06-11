import json
import uuid
from datetime import timedelta
from urllib import error, parse, request as urlrequest

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import ImportLog, StaffSession, StaffUser


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
	return request.headers.get("X-Staff-Token", "").strip()


def _authenticate_staff(request):
	token = _get_token(request)
	if not token:
		return None
	session = StaffSession.objects.filter(token=token, expires_at__gt=timezone.now()).select_related("staff").first()
	if not session:
		return None
	return session.staff


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


@csrf_exempt
@require_http_methods(["POST"])
def register_staff(request):
	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	required = ["username", "password", "full_name", "email"]
	for key in required:
		if not payload.get(key):
			return JsonResponse({"error": f"Missing field: {key}"}, status=400)

	if StaffUser.objects.filter(username=payload["username"]).exists():
		return JsonResponse({"error": "Username already exists."}, status=409)

	if StaffUser.objects.filter(email=payload["email"]).exists():
		return JsonResponse({"error": "Email already exists."}, status=409)

	staff = StaffUser.objects.create(
		username=payload["username"],
		password_hash=make_password(payload["password"]),
		full_name=payload["full_name"],
		email=payload["email"],
	)
	return JsonResponse(
		{
			"staff": {
				"id": staff.id,
				"username": staff.username,
				"full_name": staff.full_name,
				"email": staff.email,
			}
		},
		status=201,
	)


@csrf_exempt
@require_http_methods(["POST"])
def login_staff(request):
	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	username = payload.get("username", "")
	password = payload.get("password", "")
	staff = StaffUser.objects.filter(username=username).first()

	if not staff or not check_password(password, staff.password_hash):
		return JsonResponse({"error": "Invalid credentials."}, status=401)

	token = uuid.uuid4().hex
	expires_at = timezone.now() + timedelta(hours=12)
	StaffSession.objects.create(staff=staff, token=token, expires_at=expires_at)

	return JsonResponse(
		{
			"token": token,
			"expires_at": expires_at.isoformat(),
			"staff": {
				"id": staff.id,
				"username": staff.username,
				"full_name": staff.full_name,
				"email": staff.email,
			},
		}
	)


@require_http_methods(["GET"])
def computer_import_ui(_request):
	html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Computer Import</title>
</head>
<body>
  <h1>Import Computer Item</h1>
  <p>POST JSON to <code>/api/staff/import/computer/</code> with a valid staff token.</p>
  <pre>{
  "name": "Gaming PC",
  "brand": "ASUS",
  "cpu": "Core i7",
  "ram_gb": 16,
  "storage_gb": 512,
  "price": 1899.0,
  "stock": 5,
  "description": "RTX GPU"
}</pre>
</body>
</html>
"""
	return HttpResponse(html)


@require_http_methods(["GET"])
def mobile_import_ui(_request):
	html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mobile Import</title>
</head>
<body>
  <h1>Import Mobile Item</h1>
  <p>POST JSON to <code>/api/staff/import/mobile/</code> with a valid staff token.</p>
  <pre>{
  "name": "Phone X",
  "brand": "Samsung",
  "chipset": "Snapdragon",
  "ram_gb": 8,
  "storage_gb": 256,
  "price": 999.0,
  "stock": 12,
  "description": "AMOLED"
}</pre>
</body>
</html>
"""
	return HttpResponse(html)


def _proxy_item_create(staff, item_type, payload):
	payload["category"] = item_type
	status_code, data = _service_request("POST", settings.PRODUCT_SERVICE_URL, "/products/", payload)

	ImportLog.objects.create(
		staff=staff,
		item_type=item_type,
		payload=payload,
		target_item_id=(data.get("item") or {}).get("id") if isinstance(data, dict) else None,
		is_success=200 <= status_code < 300,
	)
	return status_code, data


@csrf_exempt
@require_http_methods(["POST"])
def import_item(request, item_type):
	staff = _authenticate_staff(request)
	if not staff:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	status_code, data = _proxy_item_create(staff, item_type, payload)
	return JsonResponse(data, status=status_code)


@csrf_exempt
@require_http_methods(["PATCH", "PUT"])
def update_item(request, item_type, item_id):
	staff = _authenticate_staff(request)
	if not staff:
		return JsonResponse({"error": "Unauthorized."}, status=401)

	payload = _json_body(request)
	if payload is None:
		return JsonResponse({"error": "Invalid JSON payload."}, status=400)

	status_code, data = _service_request(
		request.method,
		settings.PRODUCT_SERVICE_URL,
		f"/products/{item_id}/",
		payload,
	)
	return JsonResponse(data, status=status_code)
