import requests
import logging
from requests.exceptions import Timeout, RequestException

def trigger_payment(order_id: int, amount: float, user_jwt: str) -> dict:
    url = "http://payment-service:8004/api/payment/pay/"
    payload = {"order_id": order_id, "amount": amount}
    headers = {"Authorization": f"Bearer {user_jwt}"}
    
    try:
        # Thiết lập timeout chặt chẽ để không treo luồng của Order Service
        response = requests.post(url, json=payload, headers=headers, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Timeout:
        logging.error(f"Timeout khi gọi Payment Service cho Order {order_id}")
        return {"status": "FAILED", "reason": "TIMEOUT"}
    except RequestException as e:
        logging.error(f"Lỗi mạng: {e}")
        return {"status": "FAILED", "reason": "NETWORK_ERROR"}
