---
name: weaviate
description: Weaviate vector database implementation for AI agent memory systems, RAG pipelines, and semantic search. Covers Python client v4.x, cognitive memory architectures (episodic/semantic/procedural), hybrid search, embedding integration, memory consolidation, and production deployment. Use this skill when weaviate, vector database, AI agent memory, persistent memory, semantic memory, episodic memory, vector store, RAG pipeline, hybrid search, embedding search, weaviate collections, memory consolidation, AI memory system, vector retrieval, agent knowledge base, long-term memory, memory decay, memory architecture. Use this skill when setting up Weaviate, querying vector DB, storing embeddings, building agent memory systems, semantic search implementation.
---

# Weaviate AI Memory Repository

Vector database implementation for persistent AI agent memory, RAG pipelines, and semantic search using Weaviate v1.26+ with Python client v4.x.

## Quick Connection Setup

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from datetime import datetime

# Context manager for safe connection handling
with weaviate.connect_to_local(port=8080, grpc_port=50051) as client:
    memories = client.collections.get("EpisodicMemory")

    # Store memory
    memories.data.insert({
        "content": "User prefers concise responses",
        "timestamp": datetime.now().isoformat(),
        "importance": 0.8
    })

    # Hybrid search (semantic + BM25)
    results = memories.query.hybrid(
        query="communication preferences",
        alpha=0.7,  # 70% semantic, 30% keyword
        limit=5
    )
```

---

## Memory Architecture: Three Cognitive Types

| Type | Purpose | Example |
|------|---------|---------|
| **Episodic** | Experiences, conversations, events | "User asked about Python on Feb 23 at 2:15 PM" |
| **Semantic** | Facts, knowledge, extracted information | "Python lists are ordered, mutable collections" |
| **Procedural** | Workflows, processes, decision patterns | "When code requested: ask requirements → generate → test" |

---

## Schema Creation (Quick Reference)

```python
# Episodic Memory - Experiences
client.collections.create(
    name="EpisodicMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.DATE),
        Property(name="importance", data_type=DataType.NUMBER),
        Property(name="session_id", data_type=DataType.TEXT),
        Property(name="context", data_type=DataType.TEXT),
    ]
)

# Semantic Memory - Facts
client.collections.create(
    name="SemanticMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    properties=[
        Property(name="fact", data_type=DataType.TEXT),
        Property(name="confidence", data_type=DataType.NUMBER),
        Property(name="source", data_type=DataType.TEXT),
        Property(name="domain", data_type=DataType.TEXT),
    ]
)

# Procedural Memory - Workflows
client.collections.create(
    name="ProceduralMemory",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    properties=[
        Property(name="task", data_type=DataType.TEXT),
        Property(name="steps", data_type=DataType.TEXT_ARRAY),
        Property(name="success_criteria", data_type=DataType.TEXT),
    ]
)
```

---

## Query Patterns (Router to Advanced Strategies)

### Pattern 1: Hybrid Search
```python
results = memories.query.hybrid(
    query="find relevant memory",
    alpha=0.7,  # Balance semantic and keyword
    limit=10
)
```

### Pattern 2: Semantic Search with Filters
```python
from weaviate.classes.query import Filter

results = memories.query.near_text(
    query="user preferences",
    where=Filter.by_property("importance").greater_than(0.7),
    limit=5
)
```

### Pattern 3: Temporal Retrieval
```python
from datetime import timedelta

cutoff = (datetime.now() - timedelta(days=7)).isoformat()
results = memories.query.fetch_objects(
    where=Filter.by_property("timestamp").greater_or_equal(cutoff),
    limit=20
)
```

---

## Key Design Principles

1. **Always use context manager**: `with weaviate.connect_to_local() as client:`
2. **Implement memory decay**: Prevent unbounded memory growth (exponential decay model)
3. **Multi-tenancy**: Scope memories to tenant_id for security
4. **Batch operations**: Insert/update multiple memories efficiently
5. **Memory consolidation**: Move high-importance episodic to semantic regularly
6. **Cleanup**: Delete low-importance memories (importance < 0.1)

---

## Reference Files

| File | Purpose |
|------|---------|
| `crud-operations.md` | Store, retrieve, update, delete with access tracking, batch import |
| `schema-design.md` | Detailed schema design, field types, indexes, partitioning |
| `embedding-integration.md` | OpenAI, Ollama, LM Studio, named vectors setup |
| `retrieval-strategies.md` | Advanced queries, temporal, semantic, hybrid, filtering patterns |
| `memory-decay.md` | Exponential decay, forgetting strategies, consolidation |
| `consolidation.md` | Episodic→semantic consolidation, LLM-driven extraction |
| `deployment.md` | Docker single-node, HA multi-node, authentication, monitoring |

---

## Current Weaviate Version Notes (v1.26+)

- **Multi-target vector search**: Query across multiple vector embeddings
- **Scalar quantization (SQ)**: 75% storage reduction with 8-bit compression
- **Range filters**: Efficient quantitative data filtering
- **Async Python client**: Full async/await support for concurrent operations
- **Anthropic integration**: Native support for Anthropic embedding models

See `embedding-integration.md` for current model setup patterns and `deployment.md` for production configuration.

---

## Best Practices Summary

- Always validate that memories are retrievable after insertion (test queries)
- Monitor memory collection sizes; use decay to prevent overflow
- Consolidate episodic→semantic weekly to maintain semantic knowledge base
- Use importance scores (0-1) consistently; decay old memories automatically
- Multi-tenant systems must filter by tenant_id in all queries
- Batch import for historical data (1000+ memories) to improve performance
- Enable persistence and backups for production deployments
