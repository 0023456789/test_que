import json
import os
from urllib import error, parse, request


CUSTOMER_BASE_URL = os.getenv("CUSTOMER_BASE_URL", "http://localhost:8001/api")
PRODUCT_BASE_URL = os.getenv("PRODUCT_BASE_URL", "http://localhost:8002/api")
USERNAME = os.getenv("DEMO_USERNAME", "demo_customer")
PASSWORD = os.getenv("DEMO_PASSWORD", "Password123!")
SHIPPING_ADDRESS = os.getenv(
    "SHIPPING_ADDRESS",
    "123 Demo Street, District 1, Ho Chi Minh City",
)
ITEM_CATEGORY = os.getenv("ITEM_CATEGORY", "computer")


def json_request(url, method="GET", payload=None, headers=None):
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            parsed = json.loads(body) if body else {"error": exc.reason}
        except json.JSONDecodeError:
            parsed = {"error": body or exc.reason}
        return exc.code, parsed


def pick_first_in_stock_product():
    url = f"{PRODUCT_BASE_URL.rstrip('/')}/api/{ITEM_CATEGORY}s/"
    status, payload = json_request(url)
    if status >= 400:
        raise RuntimeError(f"Cannot load products from {url}: {payload}")

    items = payload.get("items", [])
    for item in items:
        if int(item.get("stock", 0)) > 0:
            return item
    raise RuntimeError(f"No in-stock {ITEM_CATEGORY} products found.")


def main():
    print("== Demo checkout flow ==")
    print(f"Customer service: {CUSTOMER_BASE_URL}")
    print(f"Product service: {PRODUCT_BASE_URL}")

    login_url = f"{CUSTOMER_BASE_URL.rstrip('/')}/customers/login/"
    status, login = json_request(
        login_url,
        method="POST",
        payload={"username": USERNAME, "password": PASSWORD},
    )
    if status >= 400:
        raise RuntimeError(f"Login failed: {login}")

    token = login["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in as {login['customer']['username']} -> token {token[:8]}...")

    product = pick_first_in_stock_product()
    print("Selected product:")
    print(json.dumps(product, indent=2, ensure_ascii=False))

    create_cart_url = f"{CUSTOMER_BASE_URL.rstrip('/')}/cart/create/"
    status, cart_created = json_request(create_cart_url, method="POST", headers=headers)
    if status >= 400:
        raise RuntimeError(f"Create cart failed: {cart_created}")
    print("Cart ready:")
    print(json.dumps(cart_created, indent=2, ensure_ascii=False))

    add_item_url = f"{CUSTOMER_BASE_URL.rstrip('/')}/cart/items/"
    status, cart_after_add = json_request(
        add_item_url,
        method="POST",
        headers=headers,
        payload={
            "item_type": ITEM_CATEGORY,
            "item_id": product["id"],
            "quantity": 1,
        },
    )
    if status >= 400:
        raise RuntimeError(f"Add-to-cart failed: {cart_after_add}")
    print("Cart after add-to-cart:")
    print(json.dumps(cart_after_add, indent=2, ensure_ascii=False))

    checkout_url = f"{CUSTOMER_BASE_URL.rstrip('/')}/orders/purchase/"
    status, order = json_request(
        checkout_url,
        method="POST",
        headers=headers,
        payload={"shipping_address": SHIPPING_ADDRESS},
    )
    if status >= 400:
        raise RuntimeError(f"Checkout failed: {order}")
    print("Order created:")
    print(json.dumps(order, indent=2, ensure_ascii=False))

    current_cart_url = f"{CUSTOMER_BASE_URL.rstrip('/')}/cart/current/"
    status, current_cart = json_request(current_cart_url, headers=headers)
    if status < 400:
        print("Current cart status after checkout:")
        print(json.dumps(current_cart, indent=2, ensure_ascii=False))

    print("== Demo complete ==")


if __name__ == "__main__":
    main()
