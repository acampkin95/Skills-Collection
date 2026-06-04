# Engram Weaviate Schema Reference

Complete collection schemas for the Engram AI Memory system.

## Memory Tier Collections

All three tier collections (MemoryProject, MemoryGeneral, MemoryGlobal) share identical schema:

### Vector Index Config

```python
vectorizer_config=Configure.Vectorizer.none()  # Custom embeddings
vector_index_config=Configure.VectorIndex.hnsw(
    ef=256,
    ef_construction=128,
    max_connections=64,
    distance_metric=VectorDistances.COSINE
)
```

### Properties (39 total)

```python
from weaviate.classes.config import Property, DataType

MEMORY_PROPERTIES = [
    # Core content
    Property(name="content", data_type=DataType.TEXT),
    Property(name="summary", data_type=DataType.TEXT),
    Property(name="memory_type", data_type=DataType.TEXT),       # FACT, EVENT, RELATIONSHIP, CONTEXT
    Property(name="source", data_type=DataType.TEXT),

    # Filterable identifiers
    Property(name="project_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="user_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="tenant_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="session_id", data_type=DataType.TEXT, index_filterable=True),

    # Scoring
    Property(name="importance", data_type=DataType.NUMBER),      # 0.0 - 1.0
    Property(name="confidence", data_type=DataType.NUMBER),      # 0.0 - 1.0
    Property(name="tags", data_type=DataType.TEXT_ARRAY),
    Property(name="metadata", data_type=DataType.OBJECT),

    # Timestamps (filterable for date range queries)
    Property(name="created_at", data_type=DataType.DATE, index_filterable=True),
    Property(name="updated_at", data_type=DataType.DATE, index_filterable=True),
    Property(name="expires_at", data_type=DataType.DATE, index_filterable=True),

    # Relations
    Property(name="related_memory_ids", data_type=DataType.TEXT_ARRAY),
    Property(name="parent_memory_id", data_type=DataType.TEXT),

    # Embedding metadata
    Property(name="embedding_model", data_type=DataType.TEXT),
    Property(name="embedding_dimension", data_type=DataType.INT),

    # Access tracking
    Property(name="access_count", data_type=DataType.INT),
    Property(name="decay_factor", data_type=DataType.NUMBER),

    # Deduplication
    Property(name="canonical_id", data_type=DataType.TEXT),
    Property(name="is_canonical", data_type=DataType.BOOLEAN),

    # Provenance & integrity
    Property(name="confidence_factors", data_type=DataType.OBJECT),
    Property(name="provenance", data_type=DataType.OBJECT),
    Property(name="modification_history", data_type=DataType.TEXT_ARRAY),

    # Contradiction handling
    Property(name="contradictions", data_type=DataType.TEXT_ARRAY),
    Property(name="contradictions_resolved", data_type=DataType.BOOLEAN),
    Property(name="is_deprecated", data_type=DataType.BOOLEAN),

    # Temporal reasoning
    Property(name="temporal_bounds", data_type=DataType.OBJECT),
    Property(name="is_event", data_type=DataType.BOOLEAN),

    # Causal chains
    Property(name="cause_ids", data_type=DataType.TEXT_ARRAY),
    Property(name="effect_ids", data_type=DataType.TEXT_ARRAY),
]
```

### Collection Constants

```python
TIER1_COLLECTION = "MemoryProject"    # Project-scoped, 90-day TTL
TIER2_COLLECTION = "MemoryGeneral"    # Cross-project, 365-day TTL
TIER3_COLLECTION = "MemoryGlobal"     # System-wide, 730-day TTL

TIER_COLLECTIONS = {
    MemoryTier.PROJECT: TIER1_COLLECTION,
    MemoryTier.GENERAL: TIER2_COLLECTION,
    MemoryTier.GLOBAL: TIER3_COLLECTION,
}
```

---

## Entity Collection (Knowledge Graph)

```python
ENTITY_PROPERTIES = [
    Property(name="name", data_type=DataType.TEXT),
    Property(name="entity_type", data_type=DataType.TEXT),          # PERSON, ORGANIZATION, LOCATION
    Property(name="description", data_type=DataType.TEXT),
    Property(name="project_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="tenant_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="aliases", data_type=DataType.TEXT_ARRAY),
    Property(name="metadata", data_type=DataType.OBJECT),
    Property(name="created_at", data_type=DataType.DATE),
    Property(name="updated_at", data_type=DataType.DATE),
]
```

---

## Relation Collection (Knowledge Graph)

```python
RELATION_PROPERTIES = [
    Property(name="source_entity_id", data_type=DataType.TEXT),
    Property(name="target_entity_id", data_type=DataType.TEXT),
    Property(name="relation_type", data_type=DataType.TEXT),       # WORKS_FOR, KNOWS, LOCATED_IN, etc.
    Property(name="weight", data_type=DataType.NUMBER),            # 0.0 - 1.0
    Property(name="project_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="tenant_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="context", data_type=DataType.TEXT),
    Property(name="created_at", data_type=DataType.DATE),
]
```

---

## Investigation Collections

### InvestigationMatter

```python
MATTER_PROPERTIES = [
    Property(name="matter_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="title", data_type=DataType.TEXT),
    Property(name="description", data_type=DataType.TEXT),
    Property(name="status", data_type=DataType.TEXT),              # ACTIVE, COMPLETED, ARCHIVED
    Property(name="created_at", data_type=DataType.DATE, index_filterable=True),
    Property(name="updated_at", data_type=DataType.DATE),
]
```

### EvidenceDocument

```python
EVIDENCE_PROPERTIES = [
    Property(name="url", data_type=DataType.TEXT),
    Property(name="content", data_type=DataType.TEXT),
    Property(name="markdown", data_type=DataType.TEXT),
    Property(name="title", data_type=DataType.TEXT),
    Property(name="matter_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="source_type", data_type=DataType.TEXT),         # WEB, PDF, EMAIL, etc.
    Property(name="crawl_depth", data_type=DataType.INT),
    Property(name="created_at", data_type=DataType.DATE, index_filterable=True),
]
```

### TimelineEvent

```python
TIMELINE_PROPERTIES = [
    Property(name="event_date", data_type=DataType.DATE, index_filterable=True),
    Property(name="description", data_type=DataType.TEXT),
    Property(name="source_chunk_id", data_type=DataType.TEXT),
    Property(name="matter_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="confidence", data_type=DataType.NUMBER),        # 0.0 - 1.0
    Property(name="source_url", data_type=DataType.TEXT),
    Property(name="is_contradicted", data_type=DataType.BOOLEAN),
]
```

### IntelligenceReport

```python
REPORT_PROPERTIES = [
    Property(name="report_type", data_type=DataType.TEXT),         # SUMMARY, TIMELINE, ENTITY_MAP
    Property(name="content", data_type=DataType.TEXT),
    Property(name="matter_id", data_type=DataType.TEXT, index_filterable=True),
    Property(name="created_at", data_type=DataType.DATE, index_filterable=True),
    Property(name="metadata", data_type=DataType.OBJECT),
]
```

---

## Schema Creation Pattern

```python
def create_all_collections(client):
    """Create all Engram collections. Run once on deployment."""
    for name in [TIER1_COLLECTION, TIER2_COLLECTION, TIER3_COLLECTION]:
        if not client.collections.exists(name):
            client.collections.create(
                name=name,
                vectorizer_config=Configure.Vectorizer.none(),
                vector_index_config=Configure.VectorIndex.hnsw(
                    ef=256, ef_construction=128,
                    max_connections=64,
                    distance_metric=VectorDistances.COSINE
                ),
                properties=MEMORY_PROPERTIES
            )

    if not client.collections.exists("Entity"):
        client.collections.create(
            name="Entity",
            vectorizer_config=Configure.Vectorizer.none(),
            vector_index_config=Configure.VectorIndex.hnsw(
                ef=256, ef_construction=128,
                max_connections=64,
                distance_metric=VectorDistances.COSINE
            ),
            properties=ENTITY_PROPERTIES
        )

    if not client.collections.exists("Relation"):
        client.collections.create(
            name="Relation",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=RELATION_PROPERTIES
        )
```

## Schema Validation

```bash
# List all collections
curl -s http://localhost:8080/v1/schema | jq '.classes[].class'

# Expected output:
# "MemoryProject"
# "MemoryGeneral"
# "MemoryGlobal"
# "Entity"
# "Relation"
# "InvestigationMatter"     (if investigation module deployed)
# "EvidenceDocument"        (if investigation module deployed)
# "TimelineEvent"           (if investigation module deployed)
# "IntelligenceReport"      (if investigation module deployed)

# Check specific collection
curl -s http://localhost:8080/v1/schema/MemoryProject | jq '.properties[].name'

# Count objects in collection
curl -s http://localhost:8080/v1/objects?class=MemoryProject&limit=0 | jq '.totalResults'
```
