"""
llm_service.py – Thin async wrapper around the Ollama HTTP API.

Ollama runs as a sidecar container and exposes a REST endpoint.
We keep the HTTP client alive for connection reuse.
"""

import os
import logging
from typing import List, Dict, Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3.5")  # 4-bit GGUF via Ollama
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "1024"))
MAX_PRODUCTS_CONTEXT = int(os.getenv("MAX_PRODUCTS_CONTEXT", "5"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))


class LLMService:
    """
    Async client for Ollama generate API.

    Keeps a single httpx.AsyncClient for connection pooling.
    """

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=OLLAMA_BASE_URL, timeout=LLM_TIMEOUT
        )
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def generate(self, prompt: str) -> str:
        """
        Send *prompt* to Ollama and return the generated text.

        Uses the /api/generate endpoint (non-streaming).
        Falls back to an error message if Ollama is unreachable.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=OLLAMA_BASE_URL, timeout=LLM_TIMEOUT
            )

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": MAX_CONTEXT_TOKENS,
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }

        try:
            response = await self._client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except httpx.HTTPStatusError as exc:
            logger.error("Ollama HTTP error %s: %s", exc.response.status_code, exc)
            return f"[LLM error: HTTP {exc.response.status_code}]"
        except httpx.RequestError as exc:
            logger.error("Ollama request error: %s", exc)
            return "[LLM unavailable – please ensure Ollama is running]"

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------
    @staticmethod
    def build_rag_prompt(user_query: str, products: List[Dict]) -> str:
        """
        Construct a RAG prompt that injects retrieved product context.

        Keeps context short to stay within MAX_CONTEXT_TOKENS.
        """
        def _fmt(value, suffix=""):
            return f"{value}{suffix}" if value is not None else "N/A"

        product_lines = []
        for i, p in enumerate(products[:MAX_PRODUCTS_CONTEXT], 1):
            line = (
                f"{i}. {p.get('name')} by {p.get('brand')} | "
                f"Category: {p.get('category')} | "
                f"Price: ${p.get('price')} | "
                f"RAM: {_fmt(p.get('ram_gb'), 'GB')} | "
                f"Storage: {_fmt(p.get('storage_gb'), 'GB')} | "
                f"Stock: {p.get('stock', 0)}"
            )
            product_lines.append(line)

        context_block = "\n".join(product_lines) if product_lines else "No products found."

        prompt = (
            "You are a helpful e-commerce assistant. "
            "Answer the customer's question using ONLY the product information provided below. "
            "Be concise and recommend the most suitable product.\n\n"
            f"### Available Products:\n{context_block}\n\n"
            f"### Customer Question:\n{user_query}\n\n"
            "### Your Answer:"
        )
        return prompt

    @staticmethod
    def build_personalized_recommendation_prompt(
        user_profile: str,
        products: List[Dict],
        max_products: int | None = None,
    ) -> str:
        """Build a concise RAG prompt for personalized shopping recommendations.

        Args:
            user_profile: Summary of the customer's cart and purchase history.
            products: Candidate product dicts retrieved from the vector store.
            max_products: Maximum number of products to inject into the prompt.
                Defaults to MAX_PRODUCTS_CONTEXT (env-configured, default 5).
        """
        context_limit = max_products if max_products is not None else MAX_PRODUCTS_CONTEXT

        def _fmt(value, suffix=""):
            return f"{value}{suffix}" if value is not None else "N/A"

        product_lines = []
        for i, p in enumerate(products[:context_limit], 1):
            product_lines.append(
                f"{i}. {p.get('name')} by {p.get('brand')} | "
                f"Category: {p.get('category')} | "
                f"Price: ${p.get('price')} | "
                f"RAM: {_fmt(p.get('ram_gb'), 'GB')} | "
                f"Storage: {_fmt(p.get('storage_gb'), 'GB')} | "
                f"Stock: {p.get('stock', 0)}"
            )

        context_block = "\n".join(product_lines) if product_lines else "No products found."

        return (
            "You are a personalized e-commerce recommender. "
            "Use the customer's profile and the retrieved product context to recommend the best items. "
            "Explain briefly why each choice fits the customer's behavior. "
            "Only recommend from the provided products.\n\n"
            f"### Customer Profile:\n{user_profile}\n\n"
            f"### Candidate Products:\n{context_block}\n\n"
            "### Your Answer:"
        )
