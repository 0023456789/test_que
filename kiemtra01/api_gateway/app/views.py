import json
from urllib import error, request as urlrequest

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt


SERVICE_MAP = {
	"customer": lambda: settings.CUSTOMER_SERVICE_URL,
	"staff": lambda: settings.STAFF_SERVICE_URL,
	"product": lambda: settings.PRODUCT_SERVICE_URL,
	"ai": lambda: settings.AI_SERVICE_URL,
	# Legacy mappings
	"computer": lambda: settings.PRODUCT_SERVICE_URL,
	"mobile": lambda: settings.PRODUCT_SERVICE_URL,
	"tablet": lambda: settings.PRODUCT_SERVICE_URL,
	"monitor": lambda: settings.PRODUCT_SERVICE_URL,
	"keyboard": lambda: settings.PRODUCT_SERVICE_URL,
	"mouse": lambda: settings.PRODUCT_SERVICE_URL,
	"headphone": lambda: settings.PRODUCT_SERVICE_URL,
	"speaker": lambda: settings.PRODUCT_SERVICE_URL,
	"camera": lambda: settings.PRODUCT_SERVICE_URL,
	"printer": lambda: settings.PRODUCT_SERVICE_URL,
}


def home(request):
	return render(request, "app/customer_browse.html", {"active_page": "customer-browse"})


def customer_browse(request):
	context = {
		"active_page": "customer-browse",
		"q": request.GET.get("q", ""),
		"item_type": request.GET.get("item_type", ""),
		"brand": request.GET.get("brand", ""),
		"min_price": request.GET.get("min_price", ""),
		"max_price": request.GET.get("max_price", ""),
	}
	return render(request, "app/customer_browse.html", context)


def customer_login(request):
	return render(request, "app/customer_login.html", {"active_page": "customer-login"})


def customer_register(request):
	return render(request, "app/customer_register.html", {"active_page": "customer-register"})


def customer_cart(request):
	return render(request, "app/customer_cart.html", {"active_page": "customer-cart"})


def customer_checkout(request):
	return render(request, "app/customer_checkout.html", {"active_page": "customer-checkout"})


def staff_login(request):
	return render(request, "app/staff_login.html", {"active_page": "staff-login"})


def staff_register(request):
	return render(request, "app/staff_register.html", {"active_page": "staff-register"})


def staff_import_computer(request):
	return render(request, "app/staff_import_computer.html", {"active_page": "staff-import-computer"})


def staff_import_mobile(request):
	return render(request, "app/staff_import_mobile.html", {"active_page": "staff-import-mobile"})


def staff_update_item(request):
	return render(request, "app/staff_update_item.html", {"active_page": "staff-update-item"})


def product_detail_page(request, product_type, item_id):
	return render(request, "app/product_detail.html", {
		"active_page": "customer-browse",
		"product_type": product_type,
		"item_id": item_id,
	})


def shop(request):
	return redirect("gateway-customer-browse")


def account(request):
	return redirect("gateway-customer-login")


def cart(request):
	return redirect("gateway-customer-cart")


def staff(request):
	return redirect("gateway-staff-login")


def health(_request):
    return JsonResponse(
        {
            "message": "API gateway is running",
            "services": {
                "customer": settings.CUSTOMER_SERVICE_URL,
                "staff": settings.STAFF_SERVICE_URL,
                "product": settings.PRODUCT_SERVICE_URL,
            },
        }
    )


@csrf_exempt
def proxy(request, service, path=""):
	if service not in SERVICE_MAP:
		return JsonResponse({"error": "Unknown service."}, status=404)

	base_url = SERVICE_MAP[service]()
	target_url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
	query = request.META.get("QUERY_STRING", "")
	if query:
		target_url = f"{target_url}?{query}"

	if request.method not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
		return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])

	headers = {"Content-Type": request.headers.get("Content-Type", "application/json")}
	auth_header = request.headers.get("Authorization")
	if auth_header:
		headers["Authorization"] = auth_header

	for token_header in ["X-Staff-Token", "X-Customer-Token"]:
		if token_header in request.headers:
			headers[token_header] = request.headers[token_header]

	body = request.body if request.body else None
	proxy_req = urlrequest.Request(
		url=target_url,
		data=body,
		headers=headers,
		method=request.method,
	)

	try:
		with urlrequest.urlopen(proxy_req, timeout=20) as response:
			payload = response.read().decode("utf-8")
			content_type = response.headers.get("Content-Type", "application/json")
			if "application/json" in content_type:
				content = json.loads(payload) if payload else {}
				return JsonResponse(content, status=response.status)
			return HttpResponse(payload, status=response.status, content_type=content_type)
	except error.HTTPError as exc:
		payload = exc.read().decode("utf-8") if exc.fp else ""
		content_type = exc.headers.get("Content-Type", "application/json") if exc.headers else "application/json"
		if "application/json" in content_type:
			try:
				content = json.loads(payload) if payload else {"error": exc.reason}
			except json.JSONDecodeError:
				content = {"error": payload or exc.reason}
			return JsonResponse(content, status=exc.code)
		return HttpResponse(payload or exc.reason, status=exc.code, content_type=content_type)
	except Exception as exc:
		return JsonResponse({"error": f"Proxy failed: {exc}"}, status=503)
