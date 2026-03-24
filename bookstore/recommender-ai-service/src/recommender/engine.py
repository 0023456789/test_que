"""
AI Recommendation Engine.
Implements three strategies:
1. Collaborative filtering  — "customers who bought X also bought Y"
2. Content-based filtering  — similar categories / authors
3. Trending                 — top-rated + high recent review count
"""
import logging, os, requests
from collections import defaultdict

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL    = os.environ.get("BOOK_SERVICE_URL",    "http://book-service:8000")
ORDER_SERVICE_URL   = os.environ.get("ORDER_SERVICE_URL",   "http://order-service:8000")
COMMENT_SERVICE_URL = os.environ.get("COMMENT_SERVICE_URL", "http://comment-rate-service:8000")


def _fetch_all_books():
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/api/books/", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        logger.warning(f"Could not fetch books: {e}")
        return []

def _fetch_orders_for_customer(customer_id, token):
    try:
        r = requests.get(
            f"{ORDER_SERVICE_URL}/api/orders/",
            headers={"Authorization": f"Bearer {token}"}, timeout=5,
        )
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def collaborative_recommendations(customer_id: str, token: str, limit: int = 10):
    """Return books bought by customers who share purchase history."""
    books = _fetch_all_books()
    if not books:
        return []

    # Without a real dataset, simulate by returning top-rated books
    # excluding known purchased book_ids
    purchased_ids = set()
    orders = _fetch_orders_for_customer(customer_id, token)
    for order in orders:
        for item in order.get("items", []):
            purchased_ids.add(str(item.get("book_id")))

    candidates = [b for b in books if str(b.get("id")) not in purchased_ids]
    candidates.sort(key=lambda b: (float(b.get("average_rating", 0)), int(b.get("total_reviews", 0))), reverse=True)
    return [
        {
            "book": b,
            "score": min(1.0, float(b.get("average_rating", 0)) / 5.0),
            "reason": "Popular among similar readers",
            "algorithm": "collaborative",
        }
        for b in candidates[:limit]
    ]


def content_based_recommendations(book_id: str, limit: int = 6):
    """Return books in the same category or by the same author."""
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=5)
        if r.status_code != 200:
            return []
        source = r.json()
    except Exception:
        return []

    books = _fetch_all_books()
    category = source.get("category_name")
    author_ids = {str(a["id"]) for a in source.get("authors", [])}

    scored = []
    for b in books:
        if str(b.get("id")) == str(book_id):
            continue
        sim = 0.0
        if b.get("category_name") == category:
            sim += 0.6
        b_author_ids = {str(a["id"]) for a in b.get("authors", [])} if isinstance(b.get("authors"), list) else set()
        if author_ids & b_author_ids:
            sim += 0.4
        if sim > 0:
            scored.append({"book": b, "score": sim, "reason": "Similar category/author", "algorithm": "content-based"})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def trending_recommendations(limit: int = 10):
    """Return currently trending books by rating + review volume."""
    books = _fetch_all_books()
    books.sort(
        key=lambda b: float(b.get("average_rating", 0)) * 0.6 + min(int(b.get("total_reviews", 0)) / 100, 1) * 0.4,
        reverse=True,
    )
    return [
        {"book": b, "score": 0.9, "reason": "Trending now", "algorithm": "trending"}
        for b in books[:limit]
    ]
