# Engram Skills Changelog

## 2026-03-25

### Added: engram-weaviate-memory skill
- **SKILL.md** (494 lines) - Main reference covering:
  - 3-tier memory architecture (MemoryProject/General/Global)
  - Weaviate v1.27 connection config (Docker, Python client v4.x)
  - Vector index configuration (HNSW with ef=256, cosine distance)
  - 39-property memory collection schema
  - 5 embedding providers (nomic default, openai, deepinfra, ollama, local)
  - Memory API CRUD endpoints with search modes (vector, hybrid)
  - Query patterns: hybrid, vector+filters, temporal, multi-tier, multi-tenant, batch
  - Memory decay (exponential, half-life=7d) and fitness scoring
  - Episodic-to-semantic consolidation pipeline
  - Investigation 4-stage worker pipeline overview
  - Rate limiting, health checks, troubleshooting
- **engram-weaviate-schema.md** (255 lines) - Full collection schemas:
  - Memory tier properties (39 fields with types and index config)
  - Entity collection (9 properties for knowledge graph)
  - Relation collection (8 properties for semantic relationships)
  - Investigation collections (Matter, Evidence, Timeline, Report)
  - Schema creation and validation patterns
- **engram-memory-api.md** (310 lines) - Complete API reference:
  - All REST endpoints with request/response examples
  - Authentication (JWT + API key)
  - Search modes and composite scoring formula
  - RAG context and synthesis endpoints
  - Rate limits per endpoint
  - Error response codes
  - Internal WeaviateMemoryClient methods
  - Configuration class reference
- **engram-investigation-pipeline.md** (307 lines) - Investigation module:
  - OSINT crawler with Redis dedup and robots.txt compliance
  - 4-stage worker pipeline (Entity, Timeline, Contradiction, Report)
  - Regex NER + LLM fallback patterns
  - MinIO S3 integration for evidence storage
  - API endpoints for investigation management

### Research sources
- Engram-AiMemory codebase: client.py, config.py, api.py, memory.py, crawler.py, workers.py
- Existing weaviate skill (generic patterns)
- Existing engram sub-skills (automation, docker, architecture, server admin, maintenance)
- Weaviate v1.27+ documentation
- Docker compose configuration (9-service stack)

## 2026-03-22

### Existing skills (pre-existing)
- engram-automation-scripts (SKILL.md) - CI/CD, deployment, quality gates
- engram-docker-services (SKILL.md) - Container management, resource limits
- engram-system-architecture (SKILL.md) - Service topology, data flows
- engram-server-administration (SKILL.md) - SSH, systemd, security
- engram-maintenance-schedules (SKILL.md) - Cron, backups, health checks
