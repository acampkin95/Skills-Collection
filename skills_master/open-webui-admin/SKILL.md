---
name: open-webui-admin
description: OpenWebUI administration, — user management, model configuration, knowledge bases.
version: 2.0.0
reviewed: "2026-06-04"
---

# Open WebUI Remote Administration Skill

## Quick Reference

| Task category | Jump to section |
|---|---|
| Authentication & API keys | [§ Auth](#authentication) |
| User management | [§ Users](#user-management) |
| Model management | [§ Models](#model-management) |
| Connection management | [§ Connections](#connection-management) |
| Knowledge base / RAG | [§ RAG](#knowledge-base--rag) |
| Chat session management | [§ Chats](#chat-session-management) |
| System config & env vars | [§ Config](#system-configuration) |
| Docker maintenance | [§ Docker](#docker-maintenance) |
| Health, monitoring, backup | [§ Ops](#operations--maintenance) |
| Scripted automation patterns | [§ Automation](#automation-patterns) |

---

## Prerequisites

```bash
# Required env vars — set once, reference everywhere
export OWUI_URL="https://your-webui.example.com"   # no trailing slash
export OWUI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"        # Admin API key preferred
```

**Enable API keys** (first-time setup): Admin Panel → Settings → General → Enable API Keys.  
**Swagger docs**: Set `ENV=dev` in your Docker environment, then browse `$OWUI_URL/docs`.

---

## Authentication

Open WebUI accepts two credential types on all authenticated endpoints:

```bash
# Bearer token (API key — preferred for automation)
-H "Authorization: Bearer $OWUI_API_KEY"

# Alternative header (if reverse proxy consumes Authorization)
-H "x-api-key: $OWUI_API_KEY"

# JWT (web session token — short-lived, suitable for scripting against own account)
-H "Authorization: Bearer $JWT_TOKEN"
```

### Obtain an API Key

```bash
# Via UI: Settings → Account → Generate New API Key

# Via API (admin fetching another user's key — Open WebUI ≥ Mar 2025)
curl -s "$OWUI_URL/api/users/$USER_ID/api_key" \
  -H "Authorization: Bearer $OWUI_API_KEY"
```

### API Key Endpoint Restrictions

Scope API keys to least-privilege routes via Admin Panel → Settings → General → API Key Endpoint Restrictions. Example allowlist for a monitoring bot: `/api/models`, `/api/chat/completions`.

---

## User Management

> All user-management endpoints require an admin Bearer token.

```bash
# List all users
curl -s "$OWUI_URL/api/users" \
  -H "Authorization: Bearer $OWUI_API_KEY" | jq .

# Get specific user
curl -s "$OWUI_URL/api/users/$USER_ID" \
  -H "Authorization: Bearer $OWUI_API_KEY"

# Update user role  (role: "admin" | "user" | "pending")
curl -s -X POST "$OWUI_URL/api/users/$USER_ID/update" \
  -H "Authorization: Bearer $OWUI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "name": "Alice Smith"}'

# Delete a user
curl -s -X DELETE "$OWUI_URL/api/users/$USER_ID" \
  -H "Authorization: Bearer $OWUI_API_KEY"
```

### Group / Permission Management

```bash
# List groups
curl -s "$OWUI_URL/api/groups" \
  -H "Authorization: Bearer $OWUI_API_KEY"

# Grant API-key generation permission to default user role
# Admin Panel → Users → Groups → Default Permissions → Enable API Keys
# Or via API — update the group permissions object:
curl -s -X POST "$OWUI_URL/api/groups/$GROUP_ID/update" \
  -H "Authorization: Bearer $OWUI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"permissions": {"api_key": true}}'
```

### Headless Admin Account Creation

Bootstrap a fresh instance without a browser using Docker environment variables:

```yaml
# docker-compose.yml
environment:
  - WEBUI_ADMIN_EMAIL=admin@example.com
  - WEBUI_ADMIN_PASSWORD=ChangeMe123!
  - WEBUI_ADMIN_NAME=Admin
```

Account is created on first startup only when the database is empty. Sign-up is auto-disabled afterwards.

---

## Model Management

```bash
# List all models (Ollama + OpenAI + custom function models)
curl -s "$OWUI_URL/api/models" \
  -H "Authorization: Bearer $OWUI_API_KEY" | jq '.[].id'

# OpenAI-compatible model list
curl -s "$OWUI_URL/v1/models" \
  -H "Authorization: Bearer $OWUI_API_KEY"

# Pull an Ollama model (triggers download on the connected Ollama instance)
curl -s -X POST "$OWUI_URL/api/models/pull" \
  -H "Authorization: Bearer $OWUI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "llama3.2:3b"}'

# List Ollama tags directly via proxy
curl -s "$OWUI_URL/ollama/api/tags" \
  -H "Authorization: Bearer $OWUI_API_KEY"

# Export model configurations (admin)
# Admin Panel → Settings → Models → Export JSON
# Via API — GET all models then save JSON:
curl -s "$OWUI_URL/api/models" \
  -H "Authorization: Bearer $OWUI_API_KEY" > models-backup-$(date +%Y%m%d).json

# Import model configurations
curl -s -X POST "$OWUI_URL/api/models/import" \
  -H "Authorization: Bearer $OWUI_API_KEY" \

See [full-reference.md](references/full-reference.md) for complete details and advanced patterns.