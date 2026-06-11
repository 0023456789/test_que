"""
recommend.py – Recommendation endpoint.

GET /recommend?user_id=<int>&limit=<int>

Hybrid strategy:
  1. Query Neo4j for categories the user prefers.
  2. Use FAISS to find semantically similar products in those categories.
  3. Filter: stock > 0.
  4. Return top 5.

Falls back to pure vector search when Neo4j is unavailable.
"""

import asyncio
import logging
import os
from typing import List

import httpx
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel

from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter()

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8000/api")


def _unique_key(item: dict) -> str:
    return str(item.get("product_id") or item.get("id") or item.get("name") or "")


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------
class ProductOut(BaseModel):
    id: int | None = None
    name: str
    brand: str
    category: str
    product_type: str | None = None
    price: float
    stock: int
    ram_gb: int | None = None
    storage_gb: int | None = None
    score: float | None = None


class RecommendResponse(BaseModel):
    user_id: int
    recommendations: List[ProductOut]


class PersonalizedRecommendResponse(BaseModel):
    user_id: int | None = None
    summary: str
    recommendations: List[ProductOut]
    source: str


class ReindexResponse(BaseModel):
    products_indexed: int
    source: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.get("", response_model=RecommendResponse, summary="Get product recommendations")
async def get_recommendations(
    request: Request,
    user_id: int = Query(..., description="ID of the user to recommend for"),
    limit: int = Query(5, ge=1, le=20, description="Number of results to return"),
):
    """
    Hybrid recommendation:

    * **Neo4j** → preferred categories for the user
    * **FAISS**  → top semantically similar products per category
    * **Filter** → only in-stock items (stock > 0)
    """
    vector_svc = request.app.state.vector_service
    graph_svc = request.app.state.graph_service
    recommender_svc = request.app.state.recommender_service

    # -- Step 1: model-based recommendations from recent history --
    history = graph_svc.get_user_recent_products(user_id, limit=10)
    model_ids = []
    if recommender_svc.available:
        model_ids = recommender_svc.recommend_for_user(history, k=limit * 4)

    candidates = vector_svc.get_products_by_product_ids(model_ids)
    logger.info("User %d – model candidates: %d", user_id, len(candidates))

    # -- Step 2: vector fallback when model is empty/insufficient --
    if len(candidates) < limit:
        categories = graph_svc.get_user_preferred_categories(user_id)
        logger.info("User %d – preferred categories from Neo4j: %s", user_id, categories)

        if categories:
            query = " ".join(categories)  # e.g. "laptop gaming computer"
        else:
            query = "popular product"

        vector_candidates = vector_svc.search(query, k=limit * 4)
        candidates.extend(vector_candidates)

    # -- Step 3: filter in-stock and deduplicate --
    seen_ids: set = set()
    results: List[ProductOut] = []

    for item in candidates:
        if item.get("stock", 0) <= 0:
            continue
        pid = _unique_key(item)
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)

        # Convert pid to int if numeric, otherwise leave as None
        numeric_id: int | None = None
        try:
            numeric_id = int(pid)
        except (ValueError, TypeError):
            numeric_id = item.get("id")

        results.append(
            ProductOut(
                id=numeric_id,
                name=item.get("name", ""),
                brand=item.get("brand", ""),
                category=item.get("category", ""),
                product_type=item.get("product_type") or item.get("category"),
                price=float(item.get("price", 0)),
                stock=int(item.get("stock", 0)),
                ram_gb=item.get("ram_gb"),
                storage_gb=item.get("storage_gb"),
                score=item.get("_score"),
            )
        )
        if len(results) >= limit:
            break

    return RecommendResponse(user_id=user_id, recommendations=results)


@router.post("/reindex", response_model=ReindexResponse, summary="Rebuild FAISS index")
async def reindex_catalog(request: Request):
    """Rebuild the vector index from the latest product catalog."""
    vector_svc = request.app.state.vector_service
    loop = asyncio.get_running_loop()
    count = await loop.run_in_executor(None, vector_svc.refresh_index)
    if count <= 0:
        raise HTTPException(status_code=503, detail="No products available to index.")
    return ReindexResponse(products_indexed=count, source=vector_svc.last_index_source)


async def _fetch_customer_context(request: Request, limit: int) -> tuple[str, int | None]:
    token = request.headers.get("X-Customer-Token", "").strip()
    auth_header = request.headers.get("Authorization", "").strip()
    headers = {}
    if token:
        headers["X-Customer-Token"] = token
    if auth_header:
        headers["Authorization"] = auth_header

    if not headers:
        return "", None

    async with httpx.AsyncClient(timeout=15.0) as client:
        cart_resp = await client.get(f"{CUSTOMER_SERVICE_URL.rstrip('/')}/cart/current/", headers=headers)
        if cart_resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized.")
        cart_resp.raise_for_status()
        cart_payload = cart_resp.json().get("cart", {})

        orders_resp = await client.get(
            f"{CUSTOMER_SERVICE_URL.rstrip('/')}/orders/recent/",
            params={"limit": min(max(limit, 1), 5)},
            headers=headers,
        )
        orders_payload = []
        if orders_resp.status_code < 400:
            orders_payload = orders_resp.json().get("orders", [])

    profile_parts: list[str] = []
    user_id = None

    items = cart_payload.get("items", [])
    cart_customer_id = cart_payload.get("customer_id")
    if cart_customer_id is not None:
        user_id = cart_customer_id
    if items:
        profile_parts.append(
            "Current cart: " + ", ".join(f"{item['item_name']} x{item['quantity']}" for item in items[:8])
        )

    if orders_payload:
        recent_names = []
        for order in orders_payload:
            for item in order.get("items", [])[:8]:
                recent_names.append(item.get("item_name", ""))
        if recent_names:
            profile_parts.append("Recent purchases: " + ", ".join(recent_names[:12]))
            if user_id is None:
                order_customer_id = orders_payload[0].get("customer_id")
                if order_customer_id is not None:
                    user_id = order_customer_id

    if cart_payload:
        profile_parts.append(f"Cart total: ${cart_payload.get('total_amount', 0):.2f}")

    summary = " | ".join(part for part in profile_parts if part)
    if not summary:
        summary = "No recent user history available."

    return summary, user_id


@router.get("/personalized", response_model=PersonalizedRecommendResponse, summary="Get personalized AI recommendations")
async def get_personalized_recommendations(
    request: Request,
    limit: int = Query(6, ge=1, le=12, description="Number of results to return"),
):
    """RAG-based personalized recommendation using customer history + product retrieval."""
    vector_svc = request.app.state.vector_service
    llm_svc = request.app.state.llm_service

    profile_summary, user_id = await _fetch_customer_context(request, limit)
    query = profile_summary or "popular electronics for this customer"

    candidates = vector_svc.search(query, k=limit * 5)
    seen_ids: set[str] = set()
    results: List[ProductOut] = []

    for item in candidates:
        if item.get("stock", 0) <= 0:
            continue
        pid = _unique_key(item)
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)
        results.append(
            ProductOut(
                id=item.get("id"),
                name=item.get("name", ""),
                brand=item.get("brand", ""),
                category=item.get("category", ""),
                product_type=item.get("product_type") or item.get("category"),
                price=float(item.get("price", 0)),
                stock=int(item.get("stock", 0)),
                ram_gb=item.get("ram_gb"),
                storage_gb=item.get("storage_gb"),
                score=item.get("_score"),
            )
        )
        if len(results) >= limit:
            break

    prompt = LLMService.build_personalized_recommendation_prompt(
        profile_summary, [r.model_dump() for r in results], max_products=limit
    )
    summary = await llm_svc.generate(prompt)
    if summary.startswith("[LLM error:") or summary.startswith("[LLM unavailable"):
        summary = (
            f"Based on your history ({profile_summary}), these items are the best current matches."
        )

    return PersonalizedRecommendResponse(
        user_id=user_id,
        summary=summary,
        recommendations=results,
        source=vector_svc.last_index_source,
    )
