# Engram Memory API Reference

FastAPI service at `packages/core/src/memory_system/api.py`. Default port: 8000.

## Authentication

- JWT-based: `Authorization: Bearer <token>` (JWT_SECRET in .env)
- API Key: `X-API-Key: <MEMORY_API_KEY>` header
- Rate limited via slowapi (per-IP)

---

## Endpoints

### POST /memories

Create a new memory.

```python
# Request
{
    "content": "User prefers Python for data analysis",   # required
    "memory_type": "FACT",          # FACT, EVENT, RELATIONSHIP, CONTEXT
    "tier": "PROJECT",              # PROJECT, GENERAL, GLOBAL
    "project_id": "proj-123",       # required for PROJECT tier
    "user_id": "user-456",
    "importance": 0.8,              # 0.0 - 1.0
    "confidence": 0.9,
    "tags": ["preference", "language"],
    "metadata": {"source": "conversation"},
    "session_id": "sess-789",
    "expires_at": "2026-06-25T00:00:00Z"  # optional TTL
}

# Response: 201
{
    "id": "uuid-string",
    "content": "...",
    "memory_type": "FACT",
    "tier": "PROJECT",
    "importance": 0.8,
    "created_at": "2026-03-25T10:00:00Z",
    "embedding_model": "nomic-embed-text",
    "embedding_dimension": 768
}
```

### GET /memories/{memory_id}

Retrieve memory by UUID. Auto-traverses tiers if `tier` not specified.

```
GET /memories/abc-123?tier=PROJECT
```

### PATCH /memories/{memory_id}

Update metadata fields only.

```python
# Request
{
    "tier": "PROJECT",              # required
    "importance": 0.9,
    "tags": ["updated", "priority"],
    "metadata": {"reviewed": true},
    "expires_at": "2026-12-31T00:00:00Z"
}
```

### DELETE /memories/{memory_id}

```
DELETE /memories/abc-123?tier=PROJECT&soft=true
# soft=true: sets is_deprecated=True
# soft=false: hard delete via delete_by_id()
```

### GET /memories

List with pagination and filters.

```
GET /memories?tier=PROJECT&limit=50&offset=0&project_id=proj-123&memory_type=FACT
```

### POST /memories/search

Primary search endpoint. Supports vector and hybrid modes.

```python
# Request
{
    "query": "Python data analysis preferences",
    "query_vector": null,           # optional pre-computed embedding
    "limit": 10,
    "offset": 0,
    "tier": "PROJECT",             # optional, searches all tiers if null
    "filters": {
        "project_id": "proj-123",
        "memory_type": "FACT",
        "importance_min": 0.5,
        "date_range": {
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-03-25T23:59:59Z"
        },
        "tags": ["preference"]
    },
    "retrieval_mode": "hybrid"     # "vector" or "hybrid"
}

# Response: 200
{
    "results": [
        {
            "id": "uuid-string",
            "content": "User prefers Python for data analysis",
            "memory_type": "FACT",
            "importance": 0.8,
            "similarity": 0.92,
            "composite_score": 0.87,
            "created_at": "2026-03-20T10:00:00Z"
        }
    ],
    "count": 1,
    "total_count": 1
}
```

**Search Modes:**

- `vector`: Near-vector search with metadata filters (default)
- `hybrid`: Alpha-weighted combination of vector (70%) + BM25 keyword (30%)

**Composite Scoring:**

```
composite = (0.4 * vector_similarity) + (0.3 * recency_score) + (0.3 * importance)
```

### POST /memories/rag/context

Semantic search optimized for LLM context generation.

```python
{
    "query": "Redis caching patterns",
    "limit": 5,
    "tier": "GENERAL",
    "min_importance": 0.3
}
# Returns: top-k memories formatted for LLM context window
```

### POST /memories/rag/synthesize

Generate narrative from multiple memory chunks.

```python
{
    "query": "summarize user communication preferences",
    "limit": 10,
    "tier": "PROJECT",
    "project_id": "proj-123"
}
# Returns: coherent narrative synthesized from retrieved memories
```

### POST /memories/batch

Batch insert multiple memories.

```python
{
    "memories": [
        {"content": "...", "memory_type": "FACT", "tier": "PROJECT", ...},
        {"content": "...", "memory_type": "EVENT", "tier": "PROJECT", ...}
    ]
}

# Response: 200
{
    "successful": ["uuid-1", "uuid-2"],
    "failed": []
}
```

---

## Health & Stats

### GET /health

```json
{
    "status": "ok",
    "weaviate": "connected",
    "redis": "connected",
    "initialized": true
}
```

### GET /stats

```json
{
    "total_chunks": 15432,
    "collections": {
        "MemoryProject": 8200,
        "MemoryGeneral": 5100,
        "MemoryGlobal": 2132
    }
}
```

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| POST /auth/login | 10/minute |
| POST /memories/search | 100/minute |
| POST /memories | 60/minute |
| GET /memories | 120/minute |
| POST /memories/batch | 20/minute |

---

## Error Responses

```python
# 400 Bad Request
{"detail": "Invalid memory_type. Must be FACT, EVENT, RELATIONSHIP, or CONTEXT"}

# 401 Unauthorized
{"detail": "Invalid or missing authentication token"}

# 404 Not Found
{"detail": "Memory not found in any tier"}

# 422 Validation Error
{"detail": [{"loc": ["body", "content"], "msg": "field required", "type": "value_error"}]}

# 429 Too Many Requests
{"detail": "Rate limit exceeded. Try again in 60 seconds"}

# 503 Service Unavailable
{"detail": "Weaviate connection failed"}
```

---

## Internal Client Methods

Key methods from `WeaviateMemoryClient` in `client.py`:

```python
class WeaviateMemoryClient:
    async def add_memory(self, memory: Memory) -> str:
        """Insert memory with vector. Returns UUID."""

    async def get_memory(self, memory_id: str, tier: Optional[MemoryTier] = None) -> Memory:
        """Get by ID. Traverses all tiers if tier=None."""

    async def search_memories(self, query_vector: List[float], **filters) -> List[Memory]:
        """Vector search with optional filters."""

    async def add_memories_batch(self, memories: List[Memory]) -> Tuple[List[str], List]:
        """Batch insert. Returns (successful_ids, failed_objects)."""

    async def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Insert document chunks with embeddings."""

    async def get_stats(self) -> Dict:
        """Collection counts across all tiers."""

    def create_collections(self) -> None:
        """Initialize all Weaviate collections on startup."""
```

---

## Configuration (config.py)

```python
class MemorySystemConfig:
    # Embedding
    embedding_provider: str = "nomic"
    embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = 768
    embedding_batch_size: int = 32
    embedding_timeout: int = 30

    # Search
    search_retrieval_mode: str = "vector"
    hybrid_alpha: float = 0.7

    # Multi-tenancy
    multi_tenancy_enabled: bool = True

    # Consolidation
    consolidation_min_group_size: int = 3
    consolidation_hours_back: int = 48
    consolidation_confidence: float = 0.7

    # Decay
    decay_half_life_days: int = 7
    decay_fitness_threshold: float = 0.3
```
