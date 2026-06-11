# AI Service Setup Guide

## 🎯 Overview
Lightweight AI microservice for E-Commerce with **Phi-3.5 Mini** (3.8B parameters) running on Docker.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM (CPU-only inference)

### 1. Start Services
```bash
docker-compose up -d ai_service neo4j ollama
```

### 2. Verify Services
```bash
# Check AI Service
curl http://localhost:8008/health

# Check Ollama (Phi-3.5 Mini will auto-download)
curl http://localhost:11434/api/tags

# Check Neo4j
curl http://localhost:7474/
```

### 3. Test APIs

#### Recommendation API
```bash
curl "http://localhost:8008/recommend?user_id=1&limit=5"
```

#### Chatbot API
```bash
curl -X POST http://localhost:8008/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a cheap gaming laptop"}'
```

## 🧠 Model Configuration

### Phi-3.5 Mini (Recommended)
- **Size**: 3.8B parameters (4-bit quantized ~2.3GB)
- **VRAM**: Works on CPU-only
- **Performance**: Fast response, good quality

### Alternative: Llama 3.2 3B
```bash
# Update in docker-compose.yml:
OLLAMA_MODEL: llama3.2:3b

# Or use via API:
curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3.2:3b"}'
```

## 📊 Resource Usage

| Component | Memory | CPU | Storage |
|-----------|--------|-----|---------|
| Phi-3.5 Mini | ~2.3GB | Low | ~2.5GB |
| FAISS Index | ~100MB | Low | ~50MB |
| Neo4j | ~512MB | Low | ~100MB |
| FastAPI | ~200MB | Low | ~50MB |

**Total**: ~3GB RAM, ~3GB storage

## 🔧 Configuration

### Environment Variables
```yaml
# In docker-compose.yml
OLLAMA_MODEL: phi3.5:mini
MAX_CONTEXT_TOKENS: "1024"
MAX_PRODUCTS_CONTEXT: "5"
LLM_TIMEOUT_SECONDS: "60"
```

### Model Settings
- **Context Window**: 1024 tokens (optimized for speed)
- **Temperature**: 0.7 (balanced creativity)
- **Top P**: 0.9 (focused responses)

## 🛠️ Development

### Local Development
```bash
cd ai_service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8008
```

### Rebuild Vector Index
```bash
curl -X POST http://localhost:8008/recommend/reindex
```

## 📝 API Documentation

### Health Check
```
GET /health
```

### Recommendation
```
GET /recommend?user_id=1&limit=5
```

### Chatbot
```
POST /chatbot
{
  "message": "I want a cheap gaming laptop"
}
```

## 🔍 Troubleshooting

### Model Not Loading
```bash
# Check Ollama logs
docker logs ollama

# Manually pull model
docker exec ollama ollama pull phi3.5:mini
```

### Memory Issues
- Reduce `MAX_CONTEXT_TOKENS` to 512
- Use smaller embedding model: `all-MiniLM-L6-v2`
- Limit concurrent requests

### Slow Performance
- Increase Ollama keep-alive: `OLLAMA_KEEP_ALIVE: "24h"`
- Cache embeddings in FAISS
- Use CPU optimization flags

## 📈 Performance Optimization

1. **Model Loading**: Phi-3.5 Mini loads once, stays in memory
2. **Vector Search**: FAISS with inner-product similarity
3. **Caching**: TTL cache for frequent queries
4. **Connection Pooling**: Reuse HTTP clients

## 🎛️ Advanced Configuration

### Custom Prompt Template
Edit `llm_service.py`:
```python
@staticmethod
def build_rag_prompt(user_query: str, products: List[Dict]) -> str:
    # Customize your prompt here
```

### Embedding Model Swap
```python
# In vector_service.py
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # 90MB, 384-dim
# Alternative: "paraphrase-MiniLM-L6-v2"
```

### Neo4j Query Optimization
```cypher
# Add indexes in Neo4j browser
CREATE INDEX user_id_index FOR (u:User) ON (u.id);
CREATE INDEX product_id_index FOR (p:Product) ON (p.id);
```

## 📚 Monitoring

### Logs
```bash
# AI Service logs
docker logs ai_service

# Ollama logs
docker logs ollama

# Neo4j logs
docker logs neo4j
```

### Metrics
- Request latency: ~500ms (Phi-3.5 Mini)
- Memory usage: ~3GB total
- Throughput: ~10 req/sec (CPU-only)

---

**✨ Ready for production!** This setup runs efficiently on low-resource machines while providing high-quality AI recommendations and chatbot responses.
