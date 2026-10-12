---
name: open-webui-admin
description: "Administers a remote Open WebUI instance through its REST API: user and group management, model pull and import, connection configuration for Ollama and OpenAI-compatible providers, knowledge bases and RAG files, chats, API keys and environment variables. Use when managing Open WebUI users or roles, adding or configuring a model or connection, uploading knowledge base files, rotating API keys, or running curl commands against an Open WebUI server."
version: 2.0.0
reviewed: "2026-10-12"
risk: high
---

# Open WebUI Remote Administration Skill

## Quick Reference

| Task category | Where to find it |
|---|---|
| Authentication & API keys | [§ Auth](#authentication) |
| User management | [§ Users](#user-management) |
| Model management | [§ Models](#model-management) |
| Connection management (Ollama, OpenAI) | `references/api-tree.md`, sections "Ollama Connection Config" and "OpenAI Connection Config" |
| Knowledge base / RAG and files | `references/api-tree.md`, sections "File & RAG Management" (Files, Knowledge Bases, Retrieval) |
| Chat session management | `references/api-tree.md`, section "Chats" |
| System config & env vars | `references/env-vars.md` |
| Docker maintenance | Not bundled with this skill |
| Health, monitoring, backup | Not bundled with this skill |
| Scripted automation patterns | Not bundled with this skill (the helper script `scripts/owui_admin.py` is included but not documented here) |

**Confirmation required:** before creating or deleting users, changing roles or permissions, importing model or connection configuration, rotating or revoking API keys, or changing Docker containers or volumes, state the exact action and its effect on the live instance, and get the user's explicit confirmation.

---

## Prerequisites

```bash
# Required env vars — set once, reference everywhere
export OWUI_URL="https://your-webui.example.com"   # no trailing slash
export OWUI_API_KEY="<your-api-key>"        # Admin API key preferred
```

**Enable API keys** (first-time setup): set `ENABLE_API_KEYS=true` (default `False`; it replaces the deprecated `ENABLE_API_KEY`), or enable it in the admin settings. For non-admin users, also set `USER_PERMISSIONS_FEATURES_API_KEYS=true` or grant the "API Keys" permission through a group. Source: https://github.com/open-webui/docs/blob/main/docs/reference/env-configuration.mdx (checked 2026-10-12).  
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

# Import model configurations. The body must be {"models": [ ...model objects... ]}, so wrap the
# exported model objects in that shape in models-import.json before posting it.
curl -s -X POST "$OWUI_URL/api/models/import" \
  -H "Authorization: Bearer $OWUI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @models-import.json
```

Endpoint tree: `references/api-tree.md`. Environment variables: `references/env-vars.md`.