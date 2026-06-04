# Open WebUI API Endpoint Tree

> Source-verified against Open WebUI main branch, August 2025 + docs.openwebui.com (June 2026).  
> Auth column: A = requires Bearer token; AA = requires admin Bearer token.

---

## Primary Management APIs (`/api`)

### Authentication (`/api/auths`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auths/signin` | — | Sign in, returns JWT |
| POST | `/api/auths/signup` | — | Register (if ENABLE_SIGNUP=true) |
| GET | `/api/auths` | A | Get current user profile |
| POST | `/api/auths/update/password` | A | Change own password |
| POST | `/api/auths/update/profile` | A | Update own profile |
| GET | `/api/auths/api_key` | A | Get own API key |
| POST | `/api/auths/api_key` | A | Generate/rotate own API key |
| DELETE | `/api/auths/api_key` | A | Delete own API key |

### Users (`/api/users`) — Admin only

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/users` | AA | List all users |
| GET | `/api/users/:id` | AA | Get user by ID |
| POST | `/api/users/:id/update` | AA | Update user (role, name, email) |
| DELETE | `/api/users/:id` | AA | Delete user |
| GET | `/api/users/:id/api_key` | AA | Get a user's API key |
| POST | `/api/users/:id/api_key` | AA | Generate API key for user |

### Groups (`/api/groups`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/groups` | AA | List groups |
| POST | `/api/groups/create` | AA | Create group |
| GET | `/api/groups/:id` | AA | Get group |
| POST | `/api/groups/:id/update` | AA | Update group / permissions |
| DELETE | `/api/groups/:id/delete` | AA | Delete group |

### Models (`/api/models`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/models` | A | List all available models |
| POST | `/api/models/pull` | AA | Pull/download a model |
| POST | `/api/models/import` | AA | Import model config JSON |
| GET | `/api/models/base` | A | List base (non-custom) models |

### Chats (`/api/chats`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/chats` | A | List own chats |
| POST | `/api/chats/new` | A | Create new chat |
| GET | `/api/chats/all` | AA | List all users' chats (admin) |
| GET | `/api/chats/:id` | A | Get chat with full history |
| POST | `/api/chats/:id` | A | Update entire chat object |
| DELETE | `/api/chats/:id` | A | Delete chat |
| GET | `/api/chats/:id/messages` | A | List messages in chat |
| POST | `/api/chats/:id/messages` | A | Add message to chat |
| DELETE | `/api/chats/:id/messages/:msg_id` | A | Delete message |

### Chat Processing

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/chat/completions` | A | Unified chat completion (OpenAI-compatible) |
| POST | `/api/chat/completed` | A | Run outlet() filters on completed response |

### Prompts (`/api/prompts`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/prompts` | A | List prompt templates |
| POST | `/api/prompts/create` | A | Create prompt template |
| GET | `/api/prompts/:id` | A | Get prompt |
| POST | `/api/prompts/:id/update` | A | Update prompt |
| DELETE | `/api/prompts/:id/delete` | A | Delete prompt |

### Functions / Pipes (`/api/functions`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/functions` | AA | List functions |
| POST | `/api/functions/create` | AA | Create function |
| GET | `/api/functions/:id` | AA | Get function |
| POST | `/api/functions/:id/update` | AA | Update function |
| DELETE | `/api/functions/:id/delete` | AA | Delete function |
| POST | `/api/functions/:id/toggle` | AA | Enable/disable function |

### Tools (`/api/tools`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/tools` | A | List tools |
| POST | `/api/tools/create` | A | Create tool |
| POST | `/api/tools/:id/update` | A | Update tool |
| DELETE | `/api/tools/:id/delete` | A | Delete tool |

### Pipelines (`/api/pipelines`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/pipelines` | AA | List pipelines |
| POST | `/api/pipelines/install` | AA | Install pipeline from URL |
| DELETE | `/api/pipelines/:id/delete` | AA | Delete pipeline |

### System (`/api`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/version` | — | Get Open WebUI version |
| GET | `/api/config` | — | Get public config (non-sensitive) |
| POST | `/api/config/update` | AA | Update system config |
| GET | `/api/health` | — | Health check (also at `/health`) |

### Ollama Connection Config (`/api/ollama`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/ollama/config` | AA | Get Ollama connection config |
| POST | `/api/ollama/config/update` | AA | Update Ollama connection URL(s) |
| GET | `/api/ollama/models` | A | List Ollama models |

### OpenAI Connection Config (`/api/openai`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/openai/config` | AA | Get OpenAI connections |
| POST | `/api/openai/config/update` | AA | Update OpenAI connections |
| GET | `/api/openai/models` | A | List OpenAI models |

---

## File & RAG Management (`/api/v1`)

### Files (`/api/v1/files`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/files/` | A | Upload file (multipart/form-data) |
| GET | `/api/v1/files/` | A | List uploaded files |
| GET | `/api/v1/files/:id` | A | Get file metadata |
| GET | `/api/v1/files/:id/content` | A | Download file content |
| GET | `/api/v1/files/:id/process/status` | A | Check processing status |
| DELETE | `/api/v1/files/:id` | A | Delete file |

**Query params for POST `/api/v1/files/`:**
- `process` (bool, default true) — extract content + compute embeddings
- `process_in_background` (bool, default true) — async processing

### Knowledge Bases (`/api/v1/knowledge`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/knowledge` | A | List knowledge bases |
| POST | `/api/v1/knowledge/create` | A | Create knowledge base |
| GET | `/api/v1/knowledge/:id` | A | Get KB with file list |
| POST | `/api/v1/knowledge/:id/update` | A | Update KB name/description |
| DELETE | `/api/v1/knowledge/:id/delete` | A | Delete KB |
| POST | `/api/v1/knowledge/:id/file/add` | A | Add file to KB |
| POST | `/api/v1/knowledge/:id/file/remove` | A | Remove file from KB |

### Retrieval (`/api/v1/retrieval`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/retrieval/process/web` | A | Ingest web URL into vector store |
| POST | `/api/v1/retrieval/query/collection` | A | Query a vector collection |
| POST | `/api/v1/retrieval/query/doc` | A | Query a specific document |

**Query params for POST `/api/v1/retrieval/process/web`:**
- `process` (bool, default true)
- `overwrite` (bool, default true) — replace existing vectors in collection

---

## OpenAI Compatibility Layer (`/v1`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/v1/models` | A | OpenAI-style model list |
| POST | `/v1/chat/completions` | A | OpenAI-compatible chat completion |

---

## Anthropic Compatibility Layer (`/api`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/message` | A | Anthropic Messages API (alias) |
| POST | `/api/v1/messages` | A | Anthropic Messages API |

Auth: `Authorization: Bearer KEY` or `x-api-key: KEY`.

---

## Ollama Native Passthrough (`/ollama`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/ollama/api/tags` | A | List Ollama models |
| POST | `/ollama/api/generate` | A | Native Ollama generate (streaming) |
| POST | `/ollama/api/chat` | A | Native Ollama chat |
| POST | `/ollama/api/embed` | A | Generate embeddings |
| POST | `/ollama/api/pull` | A | Pull model in Ollama |
| DELETE | `/ollama/api/delete` | A | Delete Ollama model |
| POST | `/ollama/v1/responses` | A | OpenAI Responses API via Ollama |

---

## Notes

1. **Version drift**: Open WebUI releases frequently. Always enable `ENV=dev` and inspect `/docs` for exact request schemas on your deployed version.
2. **Admin privilege**: Endpoints marked AA require a JWT or API key belonging to a user with `role: admin`.
3. **Outlet filters**: `outlet()` functions only run reliably via `/api/chat/completed` on stable releases. Do not rely on inline execution in production API integrations.
4. **MCP tools in completions**: Pass `"tool_ids": ["server:mcp:<server-id>"]` in `/api/chat/completions` body to invoke MCP tools server-side.
