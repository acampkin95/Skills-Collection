---
name: engram-weaviate-memory
description: Use when working with Engram's 3-tier vector memory system — adding/searching memories, RAG queries, knowledge graph operations, API key management, audit log queries, or maintenance (decay, consolidation, cleanup). Covers Weaviate multi-tenancy, Redis caching, embedding model config, REST endpoints, and authentication.
---

# Engram Memory System

## 3-Tier Architecture

| Tier | Scope | Use Case | Tenant Isolation |
|---|---|---|---|
| **Tier 1** (Project) | Per-project | Code insights, decisions, patterns | Yes |
| **Tier 2** (General) | Cross-project, per-user | Preferences, workflows | Yes |
| **Tier 3** (Global) | Shared | Best practices, docs, knowledge | Yes |

All tiers stored in Weaviate with multi-tenancy. Cached in Redis.

## Embedding

- **Model**: BAAI/bge-base-en-v1.5
- **Provider**: DeepInfra API
- **Dimensions**: 768
- **Cache**: Redis `emb:{sha256}` with 7-day TTL

**CRITICAL**: Changing the model requires re-embedding all data AND flushing the cache:
```bash
docker exec engram-memory-redis redis-cli KEYS 'emb:*' | xargs docker exec -i engram-memory-redis redis-cli DEL
```

## Memory Model (key fields)

| Field | Type | Range | Description |
|---|---|---|---|
| content | str | — | Memory text content |
| tier | int | 1-3 | Memory tier |
| memory_type | enum | fact/insight/code/conversation/document/preference/error_solution/workflow | Type classification |
| importance | float | 0.0-1.0 | Importance score |
| confidence | float | 0.0-1.0 | Confidence score |
| decay_factor | float | 0.0-2.0 | Decay (can exceed 1.0 via access boost) |
| recency_score | float | 0.0-1.0 | Time-based recency |
| tags | list[str] | — | Categorization tags |
| tenant_id | str | — | Tenant isolation key |
| project_id | str | — | Project scope (tier 1) |
| user_id | str | — | User scope (tier 2) |

## API Endpoints

### Memory CRUD
| Method | Path | Description |
|---|---|---|
| POST | /memories | Add single memory |
| POST | /memories/batch | Add up to 100 memories |
| GET | /memories/{id}?tier=N | Get by ID |
| GET | /memories/list?limit=N&offset=N | List paginated |
| DELETE | /memories/{id}?tier=N | Delete by ID |
| DELETE | /memories/bulk | Bulk delete by criteria |

### Search & Retrieval
| Method | Path | Description |
|---|---|---|
| POST | /memories/search | Semantic search (query, limit, tier, tags) |
| POST | /memories/rag | RAG query with synthesis prompt |
| POST | /memories/context | Build context from relevant memories |

### Knowledge Graph
| Method | Path | Description |
|---|---|---|
| POST | /graph/entities | Add entity |
| GET | /graph/entities | List entities |
| GET | /graph/entities/by-name?name=X | Get by name |
| DELETE | /graph/entities/{id} | Delete entity |
| POST | /graph/relations | Add relation (needs entity IDs) |
| POST | /graph/query | Query graph (entity_id + depth) |

### Admin (Key Management + Audit)
| Method | Path | Description |
|---|---|---|
| GET | /admin/keys | List all API keys (masked) |
| POST | /admin/keys | Create key (returns full key once) |
| PATCH | /admin/keys/{id} | Update name/status |
| DELETE | /admin/keys/{id} | Revoke key (soft-delete) |
| GET | /admin/audit-log | Query audit log (filterable) |
| GET | /admin/audit-log/summary?hours=N | Summary stats |

### Maintenance
| Method | Path | Description |
|---|---|---|
| POST | /memories/decay | Apply time-based decay |
| POST | /memories/consolidate | Merge similar (needs LLM) |
| POST | /memories/cleanup | Remove expired |
| POST | /memories/confidence-maintenance | Propagation + contradiction |

### Export
| Method | Path | Description |
|---|---|---|
| GET | /memories/export?format=json&tier=N | JSON export |
| GET | /memories/export?format=csv&tier=N | CSV export |
| GET | /memories/export?format=markdown&tier=N | Markdown export |

## Authentication

Dual model:
1. **API Key**: `X-API-Key` header → SHA-256 hashed, checked in Redis then env fallback
2. **JWT Bearer**: `Authorization: Bearer <token>` → HS256 signed, 24h expiry

API keys managed via KeyManager (Redis hashes at `engram:api_keys:{id}`).

## Audit Logging

Redis Streams at `engram:audit_log` (MAXLEN ~10000). Each request logs:
timestamp, key_id, key_name, identity, method, path, status_code, ip, latency_ms, tenant_id.

## Redis Key Patterns

| Pattern | TTL | Purpose |
|---|---|---|
| `emb:{sha256}` | 7 days | Embedding cache |
| `search:{hash}` | 1 hour | Search result cache |
| `mem:{id}` | 24 hours | Memory object cache |
| `sess:{id}` | 4 hours | Session state |
| `stats:{key}` | 5 minutes | Aggregated stats |
| `engram:api_keys:{id}` | Permanent | API key metadata |
| `engram:api_keys:index` | Permanent | Key ID set |
| `engram:audit_log` | Auto-pruned | Audit stream (max 10K) |

## See Also

- `engram-memory-api.md` — Detailed API examples
- `engram-weaviate-schema.md` — Weaviate collection schema
- `engram-investigation-pipeline.md` — Matter/evidence pipeline
