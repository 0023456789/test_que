"""
vector_service.py – Embedding + FAISS vector store for product search.

Loads the embedding model ONCE at startup and keeps the FAISS index in
memory. Index is built from the product catalogue the first time it is
needed, then cached to disk so restarts are fast.
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import httpx
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Small, CPU-friendly model: ~90 MB, 384-dim embeddings
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
INDEX_DIR = Path(os.getenv("INDEX_DIR", "data/faiss_index"))
INDEX_FILE = INDEX_DIR / "products.index"
META_FILE = INDEX_DIR / "products_meta.json"

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "").strip()
PRODUCT_SERVICE_TIMEOUT = float(os.getenv("PRODUCT_SERVICE_TIMEOUT_SECONDS", "5"))
PRODUCT_CATALOG_FILE = Path(os.getenv("PRODUCT_CATALOG_FILE", "data/products.json"))

SEARCH_CACHE_TTL_SECONDS = int(os.getenv("SEARCH_CACHE_TTL_SECONDS", "120"))
SEARCH_CACHE_MAX_ITEMS = int(os.getenv("SEARCH_CACHE_MAX_ITEMS", "1024"))


class VectorService:
    """
    Manages sentence-transformer embeddings and a FAISS flat index.

    Usage:
        svc = VectorService()
        await svc.initialise()          # load model + index
        results = svc.search(query, k=5)
    """

    def __init__(self):
        self._model: SentenceTransformer | None = None
        self._index: faiss.IndexFlatIP | None = None
        self._meta: List[Dict[str, Any]] = []  # parallel list to index rows
        self._product_lookup: Dict[str, Dict[str, Any]] = {}
        self._search_cache = TTLCache(
            maxsize=SEARCH_CACHE_MAX_ITEMS,
            ttl=SEARCH_CACHE_TTL_SECONDS,
        )
        self._last_index_source = "none"

    # ------------------------------------------------------------------
    # Initialisation (called once from lifespan)
    # ------------------------------------------------------------------
    async def initialise(self):
        """Load model (blocking) in a thread so we don't block the event loop."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._load_model)
        await loop.run_in_executor(None, self._load_index_if_exists)

        if self._index is None or self._index.ntotal == 0:
            products = await loop.run_in_executor(None, self._load_products)
            if products:
                await loop.run_in_executor(None, self.build_index, products)
            else:
                logger.warning("No products available to build FAISS index.")

    def _load_model(self):
        logger.info("Loading embedding model: %s", EMBED_MODEL_NAME)
        self._model = SentenceTransformer(EMBED_MODEL_NAME)
        logger.info("Embedding model loaded.")

    def _load_index_if_exists(self):
        if INDEX_FILE.exists() and META_FILE.exists():
            logger.info("Loading existing FAISS index from %s", INDEX_FILE)
            self._index = faiss.read_index(str(INDEX_FILE))
            with open(META_FILE, "r", encoding="utf-8") as f:
                self._meta = json.load(f)
            self._build_lookup()
            logger.info("FAISS index loaded – %d products.", self._index.ntotal)
        else:
            logger.info("No existing FAISS index found; will build on first upsert.")

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------
    def build_index(self, products: List[Dict[str, Any]]):
        """
        (Re)build the FAISS index from a product list.

        Each product dict must have at least: id, name, category,
        description, price, stock, brand.
        """
        if not products:
            logger.warning("build_index called with empty product list – skipping.")
            return
        if self._model is None:
            raise RuntimeError("Embedding model not loaded yet.")

        products = [p for p in products if p.get("is_active", True)]

        texts = [self._product_to_text(p) for p in products]
        logger.info("Encoding %d products …", len(texts))
        embeddings = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype="float32")

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # Inner-Product = cosine on normalised vecs
        self._index.add(embeddings)
        self._meta = products
        self._build_lookup()
        self._search_cache.clear()

        # Persist
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(INDEX_FILE))
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, default=str)
        logger.info("FAISS index saved – %d products.", self._index.ntotal)

    def upsert_product(self, product: Dict[str, Any]):
        """Add / update a single product (appends to index; no dedup)."""
        text = self._product_to_text(product)
        vec = self._model.encode([text], normalize_embeddings=True).astype("float32")
        if self._index is None:
            dim = vec.shape[1]
            self._index = faiss.IndexFlatIP(dim)
        self._index.add(vec)
        self._meta.append(product)
        self._product_lookup[str(product.get("product_id"))] = product
        if product.get("id") is not None:
            self._product_lookup[str(product.get("id"))] = product
        self._search_cache.clear()

    def refresh_index(self) -> int:
        """Rebuild the index from the latest product catalogue."""
        products = self._load_products()
        if not products:
            logger.warning("refresh_index: no products available.")
            return 0
        self.build_index(products)
        return len(products)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Return the top-k most similar products for a free-text query."""
        if self._index is None or self._index.ntotal == 0:
            logger.warning("FAISS index is empty – returning no results.")
            return []

        cache_key = (query.strip().lower(), int(k))
        cached = self._search_cache.get(cache_key)
        if cached is not None:
            return cached

        vec = self._model.encode([query], normalize_embeddings=True).astype("float32")
        k = min(k, self._index.ntotal)
        scores, indices = self._index.search(vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            item = dict(self._meta[idx])
            item["_score"] = float(score)
            results.append(item)
        self._search_cache[cache_key] = results
        return results

    def get_products_by_product_ids(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Return product dicts matching product IDs or numeric IDs."""
        if not self._meta:
            return []

        results = []
        seen = set()
        for pid in product_ids:
            key = str(pid)
            item = self._product_lookup.get(key)
            if item is None:
                continue
            unique_key = item.get("product_id") or item.get("id") or key
            if unique_key in seen:
                continue
            seen.add(unique_key)
            results.append(dict(item))
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _product_to_text(p: Dict[str, Any]) -> str:
        """Flatten product fields into a single string for embedding."""
        cpu = p.get("cpu") or p.get("chipset") or p.get("cpu_or_chipset", "")
        ram = p.get("ram_gb") or ""
        storage = p.get("storage_gb") or ""
        return (
            f"{p.get('name', '')} "
            f"{p.get('brand', '')} "
            f"{p.get('category', '')} "
            f"{cpu} "
            f"{p.get('description', '')} "
            f"RAM {ram}GB "
            f"Storage {storage}GB "
            f"Price {p.get('price', '')}"
        ).strip()

    def _build_lookup(self):
        self._product_lookup = {}
        for item in self._meta:
            if not isinstance(item, dict):
                continue
            product_id = item.get("product_id")
            if not product_id and item.get("id") is not None:
                try:
                    product_id = f"P{int(item.get('id')):03d}"
                except (TypeError, ValueError):
                    product_id = None
            if product_id:
                self._product_lookup[str(product_id)] = item
            if item.get("id") is not None:
                self._product_lookup[str(item.get("id"))] = item

    # ------------------------------------------------------------------
    # Product loading
    # ------------------------------------------------------------------
    def _load_products(self) -> List[Dict[str, Any]]:
        products = []

        if PRODUCT_SERVICE_URL:
            products = self._fetch_products_from_api()
            if products:
                self._last_index_source = "product_service"
                return products

        products = self._load_products_from_file()
        if products:
            self._last_index_source = "file"
            return products

        self._last_index_source = "none"
        return []

    def _fetch_products_from_api(self) -> List[Dict[str, Any]]:
        url = PRODUCT_SERVICE_URL.rstrip("/")
        if not url:
            return []
        url = f"{url}/"
        try:
            with httpx.Client(timeout=PRODUCT_SERVICE_TIMEOUT) as client:
                response = client.get(url)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Product service fetch failed: %s", exc)
            return []

        if isinstance(payload, dict):
            items = payload.get("items", payload.get("data", []))
        else:
            items = payload

        if not isinstance(items, list):
            logger.warning("Product service payload is not a list.")
            return []

        products = [self._normalize_product(item) for item in items]
        products = [p for p in products if p.get("name")]
        logger.info("Loaded %d products from product service.", len(products))
        return products

    def _load_products_from_file(self) -> List[Dict[str, Any]]:
        if not PRODUCT_CATALOG_FILE.exists():
            logger.warning("Product catalog file not found: %s", PRODUCT_CATALOG_FILE)
            return []

        try:
            with open(PRODUCT_CATALOG_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as exc:
            logger.warning("Failed to read product catalog: %s", exc)
            return []

        if isinstance(payload, dict):
            items = payload.get("items", [])
        else:
            items = payload

        if not isinstance(items, list):
            logger.warning("Product catalog payload is not a list.")
            return []

        products = [self._normalize_product(item) for item in items]
        products = [p for p in products if p.get("name")]
        logger.info("Loaded %d products from file.", len(products))
        return products

    @staticmethod
    def _normalize_product(item: Dict[str, Any]) -> Dict[str, Any]:
        def _to_int(value, default=None):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def _to_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        product_id = None
        if isinstance(item, dict):
            product_id = item.get("product_id")
            if product_id is None:
                raw_id = item.get("id")
                try:
                    product_id = f"P{int(raw_id):03d}"
                except (TypeError, ValueError):
                    product_id = None

        return {
            "id": _to_int(item.get("id"), default=None) if isinstance(item, dict) else None,
            "product_id": product_id,
            "category": str(item.get("category", "unknown")) if isinstance(item, dict) else "unknown",
            "name": str(item.get("name", "")) if isinstance(item, dict) else "",
            "brand": str(item.get("brand", "")) if isinstance(item, dict) else "",
            "cpu": item.get("cpu") if isinstance(item, dict) else None,
            "chipset": item.get("chipset") if isinstance(item, dict) else None,
            "ram_gb": _to_int(item.get("ram_gb")) if isinstance(item, dict) else None,
            "storage_gb": _to_int(item.get("storage_gb")) if isinstance(item, dict) else None,
            "price": _to_float(item.get("price")) if isinstance(item, dict) else 0.0,
            "stock": _to_int(item.get("stock"), default=0) if isinstance(item, dict) else 0,
            "description": str(item.get("description", "")) if isinstance(item, dict) else "",
            "is_active": bool(item.get("is_active", True)) if isinstance(item, dict) else True,
        }

    @property
    def last_index_source(self) -> str:
        return self._last_index_source
