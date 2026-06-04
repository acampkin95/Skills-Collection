---
name: engram-mcp-integration
description: Use when installing or configuring the Engram MCP server — connecting Claude Code, Claude Desktop, HTTP clients, or Docker to the Memory API. Covers all 27 MCP tools, environment variables, OAuth 2.1, circuit breaker resilience, automatic memory hooks, troubleshooting ECONNREFUSED/401/timeout errors, and current production config.
---

# Engram MCP Server — Client-Agnostic Installation Guide

Connect any MCP-compatible client to the Engram Memory API for AI-native memory operations.

---

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Node.js | 20+ | MCP server runtime |
| Memory API | Running | Backend (Weaviate + Redis + FastAPI) |
| API Key | Valid | Authentication via `X-API-Key` header |

---

## Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `ENGRAM_API_URL` | `http://localhost:8000` | Yes | Memory API base URL |
| `ENGRAM_API_KEY` | — | Yes | API key for authentication |
| `MCP_TRANSPORT` | `stdio` | No | Transport: `stdio` or `http` |
| `MCP_SERVER_PORT` | `3000` | No | HTTP transport port |
| `MCP_AUTH_TOKEN` | — | No | Bearer token for HTTP transport |
| `MCP_LOG_LEVEL` | `info` | No | Logging: debug, info, warn, error |

**Legacy fallbacks** (still supported):
- `MEMORY_API_URL` → falls back from `ENGRAM_API_URL`
- `AI_MEMORY_API_KEY` → falls back from `ENGRAM_API_KEY`

---

## Installation Methods

### 1. Claude Code (CLI)

```bash
# Add with environment variables
claude mcp add --scope user --transport stdio engram-memory \
  -e ENGRAM_API_URL=http://100.78.187.5:8000 \
  -e ENGRAM_API_KEY=<your-api-key> \
  -- node /path/to/Engram-MCP/dist/index.js --transport stdio

# Verify
claude mcp list  # Should show engram-memory as connected

# Remove
claude mcp remove engram-memory
```

**Scope options:**
- `--scope user` — available in all projects (stored in `~/.claude.json`)
- `--scope local` — current project only
- `--scope project` — shared via `.mcp.json` (committed to git)

### 2. Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "engram-memory": {
      "command": "node",
      "args": [
        "/absolute/path/to/Engram-MCP/dist/index.js",
        "--transport", "stdio"
      ],
      "env": {
        "ENGRAM_API_URL": "http://100.78.187.5:8000",
        "ENGRAM_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

Restart Claude Desktop after editing.

### 3. HTTP Transport (Any Client)

Start the MCP server in HTTP mode:

```bash
ENGRAM_API_URL=http://100.78.187.5:8000 \
ENGRAM_API_KEY=<your-api-key> \
MCP_TRANSPORT=http \
MCP_SERVER_PORT=3000 \
MCP_AUTH_TOKEN=<bearer-token> \
node /path/to/Engram-MCP/dist/index.js
```

**Endpoints:**
- `POST http://localhost:3000/mcp` — MCP JSON-RPC over HTTP
- `GET http://localhost:3000/health` — Health check
- `GET http://localhost:3000/.well-known/oauth-authorization-server` — OAuth discovery

**Client connection:**
```bash
# Any MCP client supporting HTTP transport
claude mcp add --transport http engram-memory http://localhost:3000/mcp
```

### 4. Docker (Remote Deployment)

Using Docker Compose (from `Engram-Platform/docker-compose.yml`):

```bash
# Start MCP server alongside other services
docker compose up -d mcp-server

# Or standalone
docker run -d \
  --name engram-mcp \
  -e ENGRAM_API_URL=http://memory-api:8000 \
  -e ENGRAM_API_KEY=<your-key> \
  -e MCP_TRANSPORT=http \
  -p 3000:3000 \
  engram-mcp-server
```

### 5. npx One-Liner

```bash
# Direct execution (if published to npm)
ENGRAM_API_URL=http://100.78.187.5:8000 \
ENGRAM_API_KEY=<your-key> \
npx @engram/mcp --transport stdio
```

### 6. Project-Level `.mcp.json`

Create `.mcp.json` in your project root (shared via git):

```json
{
  "mcpServers": {
    "engram-memory": {
      "type": "stdio",
      "command": "node",
      "args": ["/path/to/Engram-MCP/dist/index.js", "--transport", "stdio"],
      "env": {
        "ENGRAM_API_URL": "http://100.78.187.5:8000",
        "ENGRAM_API_KEY": "<your-api-key>"
      }
    }
  }
}
```

---

## Available MCP Tools (27 tools)

### Memory Operations

| Tool | Description |
|---|---|
| `add_memory` | Store a memory (tier 1/2/3, any type) |
| `search_memory` | Semantic search across memories |
| `list_memories` | List memories with pagination |
| `get_memory` | Retrieve a specific memory by ID |
| `delete_memory` | Delete a memory by ID |
| `batch_add_memories` | Add up to 100 memories at once |
| `bulk_delete_memories` | Delete memories by criteria |
| `build_context` | Assemble prompt context from relevant memories |
| `rag_query` | Retrieval-augmented generation query |
| `export_memories` | Export as JSON, CSV, or Markdown |

### Knowledge Graph

| Tool | Description |
|---|---|
| `add_entity` | Add a node (person, project, concept, tool) |
| `add_relation` | Add a relationship between entities |
| `query_graph` | Traverse graph from an entity (1-3 hops) |
| `get_kg_stats` | Knowledge graph statistics |

### Investigation & Evidence

| Tool | Description |
|---|---|
| `create_matter` | Create an investigation with isolated tenant |
| `ingest_document` | Ingest documents into a matter (web, PDF, text) |
| `search_matter` | Semantic search within a matter's evidence |

### Maintenance & Analytics

| Tool | Description |
|---|---|
| `health_check` | Check Memory API, Weaviate, Redis status |
| `consolidate_memories` | Merge related memories (requires LLM) |
| `cleanup_expired` | Remove expired memories |
| `trigger_confidence_maintenance` | Run confidence propagation |
| `get_analytics` | Memory system analytics |
| `get_memory_growth` | Growth trends |
| `get_search_stats` | Search performance stats |
| `get_activity_timeline` | Activity timeline for a memory or tenant |
| `get_system_metrics` | System resource metrics |
| `manage_tenant` | Create, list, or delete tenants |

---

## Verification

After installation, test the connection:

```bash
# In Claude Code, run /mcp to check status
# Then test with a natural language request:
# "Search my memories for deployment workflows"
# "Add a memory: the API uses port 8000"
# "Check engram health"
```

**Direct API verification:**

```bash
# Health check
curl -s http://100.78.187.5:8000/health
# Expected: {"status":"healthy","weaviate":true,"redis":true,"initialized":true}

# Test with API key
curl -s -H "X-API-Key: <your-key>" http://100.78.187.5:8000/stats
# Expected: {"total_memories":N,"tier1_count":...}
```

---

## Resilience Features

The MCP client includes built-in resilience:

| Feature | Config | Default |
|---|---|---|
| **Circuit Breaker** | Trips after 5 failures in 60s | 30s reset |
| **Retry** | Exponential backoff | 3 attempts, 1s base |
| **Timeout** | Per-request | 30s |
| **Connection Pool** | TCP keep-alive | 50 max sockets |

---

## Troubleshooting

### Unauthorized (401)

```
MCP error -32603: Unauthorized
```

**Causes:**
1. `ENGRAM_API_KEY` not set or wrong value
2. MCP server not rebuilt after `config.ts` change
3. API key revoked via `/admin/keys`

**Fix:**
```bash
# Verify key works directly
curl -s -H "X-API-Key: <your-key>" http://100.78.187.5:8000/health

# Rebuild MCP if config changed
cd Engram-MCP && npm run build

# Re-add to Claude Code
claude mcp remove engram-memory
claude mcp add --scope user --transport stdio engram-memory \
  -e ENGRAM_API_URL=http://100.78.187.5:8000 \
  -e ENGRAM_API_KEY=<your-key> \
  -- node /path/to/Engram-MCP/dist/index.js --transport stdio

# Restart Claude Code
```

### Connection Refused

```
ECONNREFUSED 100.78.187.5:8000
```

**Causes:** Memory API not running, wrong URL, Tailscale not connected.

**Fix:**
```bash
# Check Tailscale
tailscale status | grep acdev

# Check Memory API
ssh root@100.78.187.5 "docker ps | grep memory-api"

# Restart if needed
ssh root@100.78.187.5 "cd /opt/engram/Engram-Platform && docker compose up -d memory-api"
```

### Timeout

**Causes:** Slow embeddings, Weaviate overloaded, network latency.

**Fix:** Increase timeout via `MCP_TIMEOUT=60000` env var in Claude Code settings.

---

## Automatic Memory Hooks

The MCP server registers two hooks that fire around every tool call (source: `src/hooks/memory-hooks.ts`).

### Pre-tool Recall

Fires before every tool **except** read-only tools (`search_memory`, `get_memory`, `list_memories`, `rag_query`, `build_context`, `get_analytics`, `get_system_metrics`, `health_check`, `get_search_stats`, `get_kg_stats`).

Query is built from the **first matching semantic field** in args — `content`, `query`, `text`, `description`, `topic`, `entity_name`, `name`, `subject`, `url` — rather than raw JSON. Falls back to `toolName + scalar args` if no semantic field found.

Results with score ≥ 0.6 are logged at DEBUG level.

### Post-tool Store

Fires only for write tools: `add_memory`, `batch_add_memories`, `consolidate_memories`, `cleanup_expired`, `add_entity`, `add_relation`, `create_matter`, `ingest_document`.

Stored content uses input args (intent) over result text (noise). For `add_relation`, synthesises a human-readable triple: `from -[rel]-> to`.

Importance scores:

| Tool | Importance |
|------|-----------|
| `ingest_document` | 0.8 |
| `add_entity`, `add_relation`, `create_matter` | 0.7 |
| `add_memory`, `batch_add_memories` | 0.6 |
| `consolidate_memories` | 0.5 |
| `cleanup_expired` | 0.3 |

All auto-hook memories use `memory_type: "fact"` and tags `["auto-hook", toolName]`.

---

## Current Production Config

```
ENGRAM_API_URL=http://100.78.187.5:8000
Host: acdev-devnode (Tailscale)
Transport: stdio
Server: Engram-MCP/dist/index.js
Package: @engram/mcp v1.1.0
```
