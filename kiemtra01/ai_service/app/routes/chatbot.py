"""
chatbot.py – RAG chatbot endpoint.

POST /chatbot
Body: { "message": "I want a cheap gaming laptop" }

Pipeline:
  1. Embed user message (sentence-transformers).
  2. Retrieve top-k products from FAISS vector store.
  3. Build a concise prompt including product context.
  4. Send prompt to Ollama (phi3.5:mini, 4-bit quantized).
  5. Return LLM response.
"""

import logging
import re

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str       # original user message
    response: str      # LLM answer
    products_used: int  # how many products were injected as context


def _extract_budget(user_message: str) -> float | None:
    match = re.search(r"(\d{2,6}(?:\.\d{1,2})?)", user_message.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _fallback_recommendation(user_message: str, products: list[dict]) -> str:
    if not products:
        return (
            "I could not find matching products right now. "
            "Please try a more specific request like budget, category, or brand."
        )

    query = user_message.lower()
    budget = _extract_budget(user_message)

    keyword_map = {
        "laptop": ["computer", "laptop"],
        "computer": ["computer", "laptop"],
        "phone": ["mobile", "phone", "iphone", "galaxy"],
        "mobile": ["mobile", "phone", "iphone", "galaxy"],
        "tablet": ["tablet", "ipad"],
        "watch": ["smartwatch", "watch"],
        "headphone": ["headphone", "airpods", "earbud"],
        "camera": ["camera"],
        "tv": ["tv", "television"],
        "console": ["gaming_console", "console", "playstation", "xbox", "switch"],
        "drone": ["drone"],
    }

    matched_tokens = []
    for tokens in keyword_map.values():
        if any(token in query for token in tokens):
            matched_tokens.extend(tokens)

    def _matches_query(item: dict) -> bool:
        name = str(item.get("name", "")).lower()
        brand = str(item.get("brand", "")).lower()
        category = str(item.get("category", "")).lower()
        if not matched_tokens:
            return True
        return any(token in name or token in brand or token in category for token in matched_tokens)

    candidates = [p for p in products if _matches_query(p)]
    if not candidates:
        candidates = list(products)

    if budget is not None:
        under_budget = [p for p in candidates if float(p.get("price", 0) or 0) <= budget]
        if under_budget:
            candidates = sorted(under_budget, key=lambda p: float(p.get("price", 0) or 0), reverse=True)
        else:
            candidates = sorted(
                candidates,
                key=lambda p: abs(float(p.get("price", 0) or 0) - budget),
            )

    top = candidates[0]
    lines = [
        "Here are product suggestions based on your request:",
        f"1) {top.get('name', 'Unknown')} by {top.get('brand', 'Unknown')} "
        f"(price: ${top.get('price', 'N/A')}, stock: {top.get('stock', 'N/A')})",
    ]
    for idx, p in enumerate(candidates[1:3], start=2):
        lines.append(
            f"{idx}) {p.get('name', 'Unknown')} by {p.get('brand', 'Unknown')} "
            f"(price: ${p.get('price', 'N/A')}, stock: {p.get('stock', 'N/A')})"
        )
    lines.append("If you share your budget and preferred type, I can narrow this down further.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("", response_model=ChatResponse, summary="Chat with the AI assistant")
async def chat(
    body: ChatRequest,
    request: Request,
):
    """
    RAG chatbot pipeline:

    1. **Embed** the user query with a lightweight sentence-transformer.
    2. **Retrieve** the top-5 most relevant products from FAISS.
    3. **Augment** a system prompt with the retrieved product context.
    4. **Generate** a response via Ollama (phi3.5:mini, 4-bit GGUF).
    """
    vector_svc = request.app.state.vector_service
    user_message = body.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # -- Step 1 & 2: embed + retrieve --
    top_products = vector_svc.search(user_message, k=5)
    logger.info(
        "Chatbot query '%s' – retrieved %d products from FAISS.",
        user_message,
        len(top_products),
    )

    # -- Step 3: build prompt --
    prompt = LLMService.build_rag_prompt(user_message, top_products)

    # -- Step 4: call LLM --
    llm_svc = request.app.state.llm_service
    answer = await llm_svc.generate(prompt)
    if answer.startswith("[LLM error:") or answer.startswith("[LLM unavailable"):
        answer = _fallback_recommendation(user_message, top_products)

    return ChatResponse(
        message=user_message,
        response=answer,
        products_used=len(top_products),
    )
