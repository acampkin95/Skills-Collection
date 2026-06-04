---
name: engram-maintenance-schedules
description: Use when running Engram maintenance operations — memory decay, consolidation, cleanup, confidence maintenance, cache flushing, embedding cache invalidation after model changes, running the live 56-test API validation suite, SonarQube scans, or checking unit test counts across all subprojects.
---

# Engram Maintenance & Quality

## Maintenance Jobs

The `MaintenanceScheduler` runs 9 background jobs automatically. All can also be triggered manually.

### Manual Triggers

```bash
API=http://100.78.187.5:8000
KEY=88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc

# Decay — reduce importance of old memories
curl -s -X POST -H "X-API-Key: $KEY" $API/memories/decay

# Consolidation — merge similar memories (requires LLM)
curl -s -X POST -H "X-API-Key: $KEY" $API/memories/consolidate

# Cleanup — remove expired memories
curl -s -X POST -H "X-API-Key: $KEY" $API/memories/cleanup

# Confidence — propagation + contradiction detection
curl -s -X POST -H "X-API-Key: $KEY" $API/memories/confidence-maintenance
```

### Decay Model

- Time-based exponential decay on importance scores
- `decay_factor` field tracks cumulative decay (0.0 to 2.0)
- Access boost: reading a memory increases decay_factor (can exceed 1.0)
- Half-life configurable via `DECAY_HALF_LIFE_DAYS` (default: 30)
- Minimum importance floor via `DECAY_MIN_IMPORTANCE` (default: 0.1)

### Consolidation

- Groups similar memories by semantic similarity
- Merges groups of 3+ into consolidated summaries
- Requires LLM access (DeepInfra chat model)
- Fails gracefully without LLM — no data loss
- Configurable: `CONSOLIDATION_MIN_GROUP_SIZE`, `CONSOLIDATION_HOURS_BACK`

---

## Cache Management

### Redis Key Patterns

| Pattern | TTL | Purpose |
|---|---|---|
| `emb:{sha256}` | 7 days | Embedding vector cache |
| `search:{hash}` | 1 hour | Search result cache |
| `mem:{id}` | 24 hours | Individual memory cache |
| `sess:{id}` | 4 hours | Session state |
| `stats:{key}` | 5 minutes | Aggregated stats |

### Cache Operations

```bash
# Check cache size
docker exec engram-memory-redis redis-cli DBSIZE

# Check memory usage
docker exec engram-memory-redis redis-cli INFO memory | grep used_memory_human

# Flush embedding cache (needed after model change)
docker exec engram-memory-redis redis-cli KEYS 'emb:*' | xargs docker exec -i engram-memory-redis redis-cli DEL

# Flush all search cache
docker exec engram-memory-redis redis-cli KEYS 'search:*' | xargs docker exec -i engram-memory-redis redis-cli DEL

# Flush everything (CAUTION: deletes API keys and audit log too)
docker exec engram-memory-redis redis-cli FLUSHALL
```

### Embedding Cache Flush

Required when:
- Changing `DEEPINFRA_EMBED_MODEL` or `EMBEDDING_MODEL`
- Changing `EMBEDDING_DIMENSIONS`
- Weaviate reports vector dimension mismatch

```bash
# 1. Update .env with new model
# 2. Flush embedding cache
docker exec engram-memory-redis redis-cli KEYS 'emb:*' | xargs docker exec -i engram-memory-redis redis-cli DEL
# 3. Restart memory-api
docker compose up -d --force-recreate memory-api
```

---

## Testing

### engram-test Skill (Live API Validation)

55-test Python suite at `~/.claude/skills/engram/engram-hooks-tests/scripts/test-memory-api.py`

```bash
# Run full suite
bash ~/.claude/skills/engram/engram-hooks-tests/scripts/test-memory-api.sh

# Or with custom target
ENGRAM_API_URL=http://100.78.187.5:8000 \
ENGRAM_API_KEY=<key> \
python3 ~/.claude/skills/engram/engram-hooks-tests/scripts/test-memory-api.py
```

**Categories**: Health (5), CRUD (10), Search/RAG (6), Graph (6), Tenants (4), Keys (6), Audit (5), Maintenance (4), Export (3), Auth (4), Cleanup (2)

### Unit Tests

```bash
# AiMemory (985 tests)
cd Engram-AiMemory && JWT_SECRET=test make test

# Platform (1081 tests)
cd Engram-Platform/frontend && npx vitest run

# MCP (382 tests)
cd Engram-MCP && npm run test

# AiCrawler (2393 tests)
cd Engram-AiCrawler/01_devroot && pytest tests/ -v
```

---

## SonarQube

**Server**: http://100.114.241.115:9000 (alex-home-pc)
**Project**: engram-platform
**Config**: `sonar-project.properties` in repo root

```bash
# Run scan (from repo root)
sonar-scanner

# Or with explicit token
SONAR_TOKEN=squ_43ba6c39b43398a08e63ae1aad871d1bf365645c sonar-scanner

# View results
open http://100.114.241.115:9000/dashboard?id=engram-platform
```

**Latest metrics** (2026-03-31): 59,860 LOC, maintainability A, 2.1% duplication, 44.7% coverage (sonar-measured).

---

## Quality Gate Script

```bash
# Run full quality gate
bash scripts/quality-gate.sh

# Includes: lint, type check, tests, build verification
```
