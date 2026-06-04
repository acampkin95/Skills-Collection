---
name: engram-system-architecture
description: Use when understanding Engram Platform architecture, data flow, tech stack, or failure domains. Covers 4-subproject monorepo (AiMemory, AiCrawler, MCP, Platform), Weaviate vector DB, Redis caching, FastAPI backends, Next.js 15 frontend, Docker Compose orchestration, test baseline metrics, and documentation structure.
---

# Engram System Architecture

## Overview

Engram is a multi-layer AI memory and intelligence platform. 4 subprojects + shared library, orchestrated via Docker Compose.

```
┌─────────────────────────────────────────────────────────┐
│  Engram-Platform (Next.js 15, port 3002)                │
│  Dashboard: memory browser, crawler UI, graph viewer    │
│  Auth: Clerk v6 | State: Zustand v5 | Data: SWR v2     │
├──────────────┬──────────────┬───────────────────────────┤
│  Engram-MCP  │ Crawler API  │  Memory API               │
│  (port 3000) │ (port 11235) │  (port 8000)              │
│  stdio/HTTP  │ FastAPI      │  FastAPI + Admin           │
│  25 tools    │ OSINT+Crawl  │  CRUD+Search+RAG+Keys     │
├──────────────┴──────────────┴───────────────────────────┤
│  Weaviate (8080)  │  Redis x2 (6379)  │  ChromaDB       │
│  Vector storage   │  Cache + Keys +   │  Crawler store   │
│  Multi-tenant     │  Audit Streams    │                  │
├───────────────────┴───────────────────┴─────────────────┤
│  Nginx (80/443) — Reverse proxy, SSL, rate limiting     │
│  SSR cache, gzip, security headers                      │
└─────────────────────────────────────────────────────────┘
```

## Subprojects

| Subproject | Language | Port | Purpose |
|---|---|---|---|
| **Engram-AiMemory** | Python 3.11+ / TS | 8000 | 3-tier vector memory (Weaviate + Redis + MCP) |
| **Engram-AiCrawler** | Python 3.11 / React 18 | 11235 | OSINT web crawler (Crawl4AI + FastAPI) |
| **Engram-MCP** | TypeScript (Node 20+) | 3000 | MCP server — dual transport, OAuth 2.1 |
| **Engram-Platform** | Next.js 15 / React 19 | 3002 | Unified frontend dashboard with Clerk auth |
| **engram-shared** | Python | — | Shared library (logging, config, auth, http) |

## Data Flow

```
Crawler discovers → Memory API embeds + stores in Weaviate →
Redis caches hot data → MCP Server exposes tools to AI clients →
Platform frontend provides dashboard UI
```

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+) — Memory API + Crawler API
- **Weaviate 1.27** — Vector database with multi-tenancy
- **Redis 7** — Caching, API keys (hashes), audit log (Streams)
- **DeepInfra** — Embeddings (BAAI/bge-base-en-v1.5, 768-dim)

### Frontend
- **Next.js 15** App Router, React 19 Server Components
- **Clerk v6** — Auth (async auth(), OAuth, passkeys, magic links)
- **Zustand v5** + Jotai — State management
- **SWR v2** — Data fetching (dedupingInterval 10s, keepPreviousData)
- **Radix + shadcn/ui** — Component library
- **Tailwind CSS v4** — Styling (CSS-native)
- **ECharts + Recharts** — Charts and visualizations

### Design System
- **Primary**: Amber #F2A93B
- **Accent**: Violet #7C5CBF
- **Background**: Void #03020A
- **Text**: #f0eef8
- **Fonts**: Syne (display), IBM Plex Mono (mono), Instrument Serif (serif)
- **Theme**: Dark-mode-first

### MCP Server
- Dual transport: stdio (Claude Code/Desktop) + HTTP streaming
- OAuth 2.1 with PKCE + dynamic client registration
- Circuit breaker (5 failures/60s, 30s reset) + retry (3x exponential) + timeout (30s)
- 25 tools: memory CRUD, search, RAG, graph, matters, analytics, maintenance

## Test Baseline (2026-03-31)

| Subproject | Tests | Runner | Coverage |
|---|---|---|---|
| AiMemory | 985 pass | pytest | ~80% |
| AiCrawler | 2,393 pass | pytest | ~70% |
| MCP | 382 pass | node --test | ~90% |
| Platform | 1,081 pass | vitest | ~93% |
| **Total** | **4,841** | — | **~83% avg** |
| engram-test | 55 live API tests | Python script | — |

**SonarQube**: 59,860 LOC, maintainability A, 2.1% duplication.

## Documentation

12 engineering docs at `docs/system/` (8,200 lines, 282 KB):
01-System Architecture, 02-Infrastructure, 03-Data Flow, 04-Security,
05-Admin Guide, 06-Ops Runbook, 07-Developer Guide, 08-API Reference,
09-Data Models, 10-Deployment, 11-Troubleshooting, 12-Limitations.

## Failure Domains

| Domain | Components | Impact of Failure |
|---|---|---|
| **Weaviate** | Vector storage | All memory ops fail, search down |
| **memory-redis** | Cache, keys, audit | Degraded performance, no key mgmt |
| **Memory API** | FastAPI app | All memory/search/admin endpoints down |
| **Crawler API** | FastAPI + Crawl4AI | OSINT scans fail, existing data safe |
| **MCP Server** | MCP transport | AI client tools unavailable |
| **Platform** | Next.js frontend | Dashboard inaccessible, APIs still work |
| **Nginx** | Reverse proxy | All external access blocked |
