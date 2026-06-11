You are a Senior AI Engineer and Backend Developer.

Your task is to implement a lightweight AI microservice for an E-Commerce system.

## 🎯 Constraints (VERY IMPORTANT)
- The system must run on a low-resource machine:
  - GPU: 4GB VRAM (or CPU fallback)
  - Docker environment
- Use ONLY lightweight models and libraries
- Avoid heavy frameworks and large models

---

## 🧠 AI FEATURES REQUIRED

Implement an AI service with 2 main features:

### 1. Recommendation API
- Hybrid approach:
  - Graph-based recommendation (Neo4j)
  - Train a model to recommend

### 2. Chatbot API
- Use a small LLM:
  - Prefer:
    - Llama 3.2 (3B) OR
    - Phi-3.5 Mini
- MUST use:
  - 4-bit quantized GGUF model
  - Run locally using llama.cpp or similar

---

## ⚙️ TECHNOLOGY STACK

- Backend: FastAPI
- LLM Runtime:
  - llama.cpp OR
  - :contentReference[oaicite:0]{index=0} (preferred for simplicity)
- Vector DB:
  - FAISS OR ChromaDB (lightweight)
- Graph DB:
  - :contentReference[oaicite:1]{index=1}
- Embedding:
  - sentence-transformers (small model only)

---

## 📦 SYSTEM ARCHITECTURE

Flow:

Client → FastAPI → 
    (1) Recommendation logic
    (2) Chatbot pipeline

Chatbot pipeline:
- Retrieve product info (vector search)
- Query Neo4j (optional)
- Send context to LLM
- Return generated response

---

## 📌 IMPLEMENTATION DETAILS

### 1. Project Structure

ai-service/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── recommend.py
│   │   └── chatbot.py
│   ├── services/
│   │   ├── graph_service.py
│   │   ├── vector_service.py
│   │   └── llm_service.py
│   └── models/
├── data/
├── Dockerfile
└── requirements.txt

---

### 2. Recommendation API

Endpoint:
GET /recommend?user_id=1

Logic:
- Query Neo4j:
  - Get categories user interacted with
- Find similar products
- Filter:
  - stock > 0
- Return top 5

DO NOT use heavy ML training

---

### 3. Chatbot API

Endpoint:
POST /chatbot

Input:
{
  "message": "I want a cheap gaming laptop"
}

Pipeline:
1. Embed user query
2. Retrieve top-k products from vector DB
3. Build prompt:
   - Include product info
4. Send to LLM (via Ollama or llama.cpp)
5. Return response

---

### 4. LLM REQUIREMENTS

- Use:
  - llama3.2:3b OR phi3.5-mini
- MUST be:
  - 4-bit quantized (GGUF)
- Must run locally
- No OpenAI API

Example (Ollama):
ollama run llama3.2:3b

---

### 5. Docker Requirements

- Must run with docker-compose
- Keep image small
- No GPU dependency required
- Use CPU-friendly inference

---

### 6. Performance Optimization

- Use caching if needed
- Limit context size
- Use small embedding model
- Avoid loading model per request

---

## 📤 OUTPUT REQUIRED

Generate:

1. Full FastAPI project
2. Code for:
   - recommendation
   - chatbot
3. Neo4j query example
4. Vector DB setup
5. LLM integration (Ollama or llama.cpp)
6. Dockerfile
7. docker-compose.yml
8. Instructions to run

Code must be:
- Clean
- Well-commented
- Minimal dependencies
- Runnable on low-end machine

---

## ⚠️ IMPORTANT

- DO NOT use large models (>4B)
- DO NOT use GPU-only frameworks
- DO NOT include unnecessary complexity
- Prioritize simplicity and performance

---

Start implementation step-by-step.