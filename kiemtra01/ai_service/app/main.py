"""
main.py – FastAPI entry point for the AI microservice.

Initialises shared resources on startup (embedding model, FAISS index,
Neo4j driver) so they are loaded ONCE and reused across every request.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.services.vector_service import VectorService
from app.services.graph_service import GraphService
from app.services.llm_service import LLMService
from app.services.recommender_service import RecommenderService
from app.routes import recommend, chatbot


# ---------------------------------------------------------------------------
# Lifespan: load heavy objects once, share via app.state
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialise services; Shutdown: release resources."""
    # Vector / embedding service (loads sentence-transformer + FAISS index)
    app.state.vector_service = VectorService()
    await app.state.vector_service.initialise()

    # Graph service (Neo4j connection pool)
    app.state.graph_service = GraphService()
    app.state.graph_service.connect()

    # LLM service (Ollama HTTP client)
    app.state.llm_service = LLMService()

    # Recommender service (precomputed model)
    app.state.recommender_service = RecommenderService()
    app.state.recommender_service.load()

    yield  # <-- application runs here

    # Teardown
    app.state.graph_service.close()
    await app.state.llm_service.close()


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="E-Commerce AI Service",
    description="Lightweight recommendation & chatbot microservice",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(recommend.router, prefix="/recommend", tags=["Recommendation"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
