# Weaviate Memory System for AI Agents

A comprehensive memory management system implementing cognitive memory patterns for AI agents using Weaviate vector database.

## Features

- **Episodic Memory**: Specific events with full temporal and contextual information
- **Semantic Memory**: Generalized facts and knowledge extracted from experience
- **Procedural Memory**: Learned workflows and skill sequences
- **Working Memory**: Active session context with automatic expiration

### Advanced Capabilities

- **Hybrid Search**: Combines semantic similarity with BM25 keyword matching
- **Recency Decay**: Exponential decay function for memory freshness
- **Memory Consolidation**: Automatic conversion of episodic experiences to semantic knowledge
- **Multi-Tenant Isolation**: Per-agent or per-user memory partitioning
- **RAG Integration**: Memory-augmented generation with context management
- **Token Budget Management**: Intelligent context window optimization

## Quick Start

### 1. Start Weaviate

```bash
# Single node (development)
docker-compose up -d

# Or multi-node cluster (production)
docker-compose -f docker-compose-cluster.yml up -d
```

### 2. Start Ollama (for embeddings)

```bash
ollama serve
ollama pull nomic-embed-text
ollama pull llama3.2  # For generative features
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Basic Usage

```python
import weaviate
from weaviate_memory import (
    create_memory_collections,
    MemoryStore,
    MemoryRetrieval
)

# Connect
client = weaviate.connect_to_local()

# Initialize collections
create_memory_collections(client)

# Store memories
store = MemoryStore(client)

store.store_episode(
    content="User asked about Python async patterns",
    event_type="interaction",
    session_id="session-001",
    importance=0.7
)

# Retrieve relevant memories
retrieval = MemoryRetrieval(client)

results = retrieval.retrieve_relevant_memories(
    query="async programming",
    memory_types=["episodic", "semantic"],
    limit=10
)

client.close()
```

## Architecture

### Memory Types

| Type | Purpose | Key Properties |
|------|---------|----------------|
| **Episodic** | Specific events | content, eventType, timestamp, actions, outcomes, successScore |
| **Semantic** | Facts & knowledge | fact, factType, domain, confidence, derivedFromEpisodes |
| **Procedural** | Workflows | workflowName, steps, prerequisites, successRate |
| **Working** | Session context | content, sessionId, turnIndex, expiresAt |

### Scoring System

Memories are scored using a composite function:

```
composite = (similarity_weight × semantic_similarity) +
            (recency_weight × recency_score) +
            (importance_weight × importance_score)
```

Default weights: 0.4 similarity, 0.3 recency, 0.3 importance

### Recency Decay

Uses exponential decay with configurable half-life:

```
recency_score = 2^(-age_days / half_life_days)
```

Default half-life: 7 days

## Examples

See the `examples/` directory:

- `01_basic_usage.py` - Store, retrieve, and search memories
- `02_consolidation.py` - Convert episodic to semantic memory
- `03_rag_integration.py` - Memory-augmented generation
- `04_multi_tenant.py` - Per-agent memory isolation

## API Reference

### MemoryStore

```python
store = MemoryStore(client)

# Store episodic memory
uuid = store.store_episode(
    content="...",
    event_type="interaction",
    session_id="...",
    actions=["..."],
    outcomes=["..."],
    success_score=0.9,
    importance=0.7
)

# Store semantic fact
uuid = store.store_semantic_fact(
    fact="...",
    fact_type="preference",
    domain="programming",
    confidence=0.9
)

# Store procedure
uuid = store.store_procedure(
    name="Debug API",
    description="...",
    goal_type="troubleshooting",
    steps=["step1", "step2", "step3"]
)
```

### MemoryRetrieval

```python
retrieval = MemoryRetrieval(client)

# Hybrid search with composite scoring
results = retrieval.retrieve_relevant_memories(
    query="...",
    memory_types=["episodic", "semantic"],
    limit=10,
    min_importance=0.3
)

# Session context
session = retrieval.retrieve_session_context(session_id)

# User preferences
prefs = retrieval.retrieve_user_preferences(user_id)

# Applicable procedures
procs = retrieval.retrieve_applicable_procedures(
    goal="debug an issue",
    context="FastAPI"
)
```

### MemoryDecay

```python
decay = MemoryDecay(client, half_life_days=7)

# Update all recency scores
updated = decay.update_all_recency_scores("EpisodicMemory")

# Get decay statistics
stats = decay.get_decay_statistics()

# Intelligent forgetting
result = decay.apply_intelligent_forgetting(
    fitness_threshold=0.2,
    dry_run=True
)
```

### MemoryConsolidation

```python
consolidation = MemoryConsolidation(client)

# Run consolidation cycle
result = consolidation.run_consolidation_cycle()
# Returns: episodes_consolidated, new_semantic_facts, facts

# Get statistics
stats = consolidation.get_consolidation_statistics()
```

### Multi-Tenancy

```python
# Per-tenant isolation
tenant = TenantMemoryManager(client, "agent-001")
tenant.store_memory("...", memory_type="episodic")
results = tenant.search_memories("query")

# Hybrid architecture (shared + tenant-specific)
hybrid = HybridMemoryArchitecture(client, "agent-001")
knowledge = hybrid.retrieve_knowledge_with_overrides("query")
```

## Docker Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOMEMLIMIT` | Memory limit for Go runtime | 75-80% of container |
| `DISK_USE_WARNING_PERCENTAGE` | Disk warning threshold | 80 |
| `DISK_USE_READONLY_PERCENTAGE` | Disk readonly threshold | 90 |
| `OLLAMA_API_ENDPOINT` | Ollama API URL | http://host.docker.internal:11434 |
| `PROMETHEUS_MONITORING_ENABLED` | Enable Prometheus metrics | true |

### Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 8080 | HTTP | REST API |
| 50051 | gRPC | v4 client (required) |
| 2112 | HTTP | Prometheus metrics |

## Testing

```bash
# Run tests
pytest tests/ -v

# With embedded Weaviate (no Docker needed)
pytest tests/ -v --embedded
```

## Monitoring

```python
from weaviate_memory import MemoryMetrics

metrics = MemoryMetrics(client)

# Collection metrics
data = metrics.collect_metrics()

# Health check
issues = metrics.check_health()

# Full report
report = metrics.generate_health_report()
print(report)
```

## Best Practices

1. **Always close connections** - Use context managers or explicit close()
2. **Update recency scores regularly** - Run decay updates on schedule (hourly/daily)
3. **Consolidate memories** - Run consolidation cycles to extract patterns
4. **Monitor memory growth** - Set up alerts for collection sizes
5. **Use hybrid search** - Alpha=0.7 (70% vector, 30% keyword) works well
6. **Batch for bulk imports** - Use batch.fixed_size() with concurrent_requests=4
7. **Test with embedded** - Use EmbeddedOptions() for unit tests

## License

MIT License
