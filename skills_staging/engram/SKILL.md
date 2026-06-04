---
name: engram
description: Master router for Engram Platform — architecture, Docker, memory, MCP, server admin, maintenance, deployment, and validation workflows.
version: 2.0.0
reviewed: "2026-06-04"
---

# Engram Platform — Master Router

Use the narrowest Engram skill that matches the task.

## Router

| User need | Route to |
| --- | --- |
| System architecture, data flow, failure domains | `engram-system-architecture` |
| Docker services, containers, volumes, networking | `engram-docker-services` |
| Memories, search, RAG, graph, API keys, maintenance | `engram-weaviate-memory` |
| Generic Weaviate vector DB patterns | `weaviate` |
| MCP server or client integration | `engram-mcp-integration` |
| Production host, SSH, backups, SSL, SFTP | `engram-server-administration` |
| Decay, consolidation, cleanup, validation schedules | `engram-maintenance-schedules` |
| Live API tests or memory hook tests | `engram-hooks-tests` |
| Deploy updates, rebuild services, rotate certs | `engram-deploy` |
| Automation scripts, CI/CD, quality gates | See [deployment-and-scripts.md](references/deployment-and-scripts.md) |

## Quick Reference

- **Production host:** acdev-devnode (100.78.187.5) — Tailscale only
- **Memory API:** http://100.78.187.5:8000
- **Platform:** port 3002 (dev), 80/443 (Docker)
- **Monorepo:** /Users/alex/Projects/Dev/LIVE/Production/09_EngramPlatform
- **Docker path:** /opt/engram/Engram-Platform

## Key Scripts

| Script | Purpose |
|--------|---------|
| `deploy-unified.sh` | Interactive deployment orchestrator |
| `quality-gate.sh` | Full platform QA gate (lint, test, bundle) |
| `smoke-test.sh` | E2E health checks |
| `validate-env.sh` | Environment configuration validation |
| `release-smoke-test.sh` | Release verification |
| `verify-health.sh` | Quick container health |
| `deploy-full.sh` | Full AI Memory stack deploy |
| `healthcheck.sh` | Deep 10-dimension system health |

See [deployment-and-scripts.md](references/deployment-and-scripts.md) for full script documentation, CI/CD pipeline, health endpoints, and troubleshooting.
