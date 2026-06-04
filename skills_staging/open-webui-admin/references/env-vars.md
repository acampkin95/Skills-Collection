# Open WebUI Environment Variables Reference

> Source: https://docs.openwebui.com/reference/env-configuration/  
> Current as of June 2026. Open WebUI updates rapidly — always verify against `/docs` on your instance.

## Variable Types

| Type | Behaviour |
|---|---|
| **ConfigVar** | Env var that *can* be overridden from Admin UI. DB value wins once set. |
| **PersistentConfig** | Saved to DB; env var only seeds fresh installs. |
| **Static** | Read once at startup; cannot be changed via UI. |

Set `ENABLE_PERSISTENT_CONFIG=false` to force env vars to always win (UI changes are session-only).

---

## General / App

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENV` | Static | `prod` | `dev` enables Swagger at `/docs` |
| `WEBUI_URL` | PersistentConfig | `http://localhost:3000` | Public-facing URL. Used for OAuth, search engine support |
| `WEBUI_NAME` | PersistentConfig | `Open WebUI` | Browser title / branding |
| `WEBUI_SECRET_KEY` | Static | random | JWT signing key. **Must be set** for multi-worker/multi-node |
| `DATA_DIR` | Static | `/app/backend/data` | Persistent data directory |
| `FRONTEND_BUILD_DIR` | Static | `../build` | Path to frontend assets |
| `STATIC_DIR` | Static | `./static` | Serving directory for static files |
| `CUSTOM_NAME` | ConfigVar | — | Overrides header branding |
| `WEBUI_FAVICON_URL` | ConfigVar | — | Custom favicon URL |

---

## Authentication

| Variable | Type | Default | Description |
|---|---|---|---|
| `WEBUI_AUTH` | Static | `true` | `false` disables all auth (dev/local only) |
| `ENABLE_SIGNUP` | PersistentConfig | `true` | Allow new registrations |
| `ENABLE_LOGIN_FORM` | PersistentConfig | `true` | Show email/password login UI |
| `DEFAULT_USER_ROLE` | PersistentConfig | `pending` | Role for new users: `pending`/`user`/`admin` |
| `USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS` | PersistentConfig | `false` | Allow users to access workspace models |
| `ENABLE_API_KEYS` | PersistentConfig | `true` | Master toggle for API key feature |
| `ENABLE_API_KEY_ENDPOINT_RESTRICTIONS` | PersistentConfig | `false` | Enable per-key endpoint whitelisting |
| `API_KEY_ALLOWED_ENDPOINTS` | PersistentConfig | — | Comma-separated allowed endpoint paths |
| `JWT_EXPIRES_IN` | PersistentConfig | `-1` | JWT expiry: `30m`, `1h`, `10d`, `-1` = never |
| `WEBUI_ADMIN_EMAIL` | Static | — | Bootstrap admin email (fresh install only) |
| `WEBUI_ADMIN_PASSWORD` | Static | — | Bootstrap admin password (fresh install only) |
| `WEBUI_ADMIN_NAME` | Static | `Admin` | Bootstrap admin display name |
| `ENABLE_PERSISTENT_CONFIG` | Static | `true` | `false` = env vars always win |

### LDAP

| Variable | Default | Description |
|---|---|---|
| `ENABLE_LDAP` | `false` | Enable LDAP authentication |
| `LDAP_SERVER_HOST` | — | LDAP server hostname |
| `LDAP_SERVER_PORT` | `389` | LDAP server port |
| `LDAP_USE_TLS` | `false` | Use StartTLS |
| `LDAP_CA_CERT_FILE` | — | Path to CA certificate |
| `LDAP_ATTRIBUTE_FOR_MAIL` | `mail` | LDAP attribute for email |
| `LDAP_ATTRIBUTE_FOR_USERNAME` | `uid` | LDAP attribute for username |
| `LDAP_APP_DN` | — | Bind DN for LDAP queries |
| `LDAP_APP_PASSWORD` | — | Bind password |
| `LDAP_SEARCH_BASE` | — | Base DN for user search |
| `LDAP_SEARCH_FILTER` | — | LDAP search filter |

### OAuth / SSO

| Variable | Default | Description |
|---|---|---|
| `ENABLE_OAUTH_SIGNUP` | `false` | Allow sign-up via OAuth |
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | `false` | Merge OAuth + local accounts on matching email |
| `GOOGLE_CLIENT_ID` | — | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | — | Google OAuth client secret |
| `MICROSOFT_CLIENT_ID` | — | Microsoft OAuth client ID |
| `MICROSOFT_CLIENT_SECRET` | — | Microsoft OAuth client secret |
| `GITHUB_CLIENT_ID` | — | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | — | GitHub OAuth client secret |
| `OAUTH_CLIENT_ID` | — | Generic OIDC client ID |
| `OAUTH_CLIENT_SECRET` | — | Generic OIDC client secret |
| `OPENID_PROVIDER_URL` | — | OIDC well-known config URL |
| `OAUTH_SCOPES` | `openid email profile` | Requested scopes |
| `OAUTH_PROVIDER_NAME` | `SSO` | Display name on login button |
| `OAUTH_USERNAME_CLAIM` | `name` | JWT claim for display name |
| `OAUTH_EMAIL_CLAIM` | `email` | JWT claim for email |
| `OAUTH_ROLES_CLAIM` | — | JWT claim for role mapping |
| `OAUTH_ADMIN_ROLES` | — | Claim values that grant admin role |
| `OAUTH_USER_ROLES` | — | Claim values that grant user role |
| `ENABLE_OAUTH_ROLE_MANAGEMENT` | `false` | Sync roles from OAuth claims |

---

## Model Backend Connections

| Variable | Type | Default | Description |
|---|---|---|---|
| `OLLAMA_BASE_URL` | PersistentConfig | `http://ollama:11434` | Ollama server URL (semicolon-separated for multiple) |
| `ENABLE_OLLAMA_API` | PersistentConfig | `true` | Enable Ollama integration |
| `OPENAI_API_BASE_URL` | PersistentConfig | `https://api.openai.com/v1` | OpenAI-compatible base URL (semicolon-separated) |
| `OPENAI_API_KEY` | PersistentConfig | — | OpenAI API key (semicolon-separated to match URLs) |
| `ENABLE_OPENAI_API` | PersistentConfig | `true` | Enable OpenAI integration |
| `DEFAULT_MODELS` | PersistentConfig | — | Comma-separated default model IDs |
| `CUSTOM_API_KEY_HEADER` | Static | `x-api-key` | Alt header name when Authorization is consumed by proxy |

---

## RAG / Knowledge Base

| Variable | Default | Description |
|---|---|---|
| `ENABLE_RAG_WEB_SEARCH` | `false` | Enable web search in RAG |
| `RAG_EMBEDDING_ENGINE` | `default` | Embedding backend: `default`, `openai`, `ollama` |
| `RAG_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `RAG_OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | OpenAI base for embeddings |
| `RAG_OPENAI_API_KEY` | — | API key for OpenAI embeddings |
| `RAG_OLLAMA_BASE_URL` | — | Ollama base for embeddings |
| `RAG_TOP_K` | `5` | Number of RAG results to retrieve |
| `RAG_RELEVANCE_THRESHOLD` | `0.0` | Minimum similarity score filter |
| `CHUNK_SIZE` | `1500` | Document chunk size for indexing |
| `CHUNK_OVERLAP` | `100` | Chunk overlap for context continuity |
| `VECTOR_DB` | `chroma` | Vector DB backend: `chroma`, `qdrant`, `milvus`, `opensearch`, `pgvector` |
| `CHROMA_HTTP_HOST` | — | External Chroma host (default = embedded) |
| `CHROMA_HTTP_PORT` | `8000` | External Chroma port |
| `QDRANT_URL` | — | Qdrant server URL |
| `QDRANT_API_KEY` | — | Qdrant API key |
| `PGVECTOR_DB_URL` | — | PostgreSQL+pgvector URL |
| `ENABLE_GOOGLE_DRIVE_INTEGRATION` | `false` | Google Drive file picker |
| `ENABLE_ONEDRIVE_INTEGRATION` | `false` | OneDrive file picker |

---

## Audio (STT / TTS)

| Variable | Default | Description |
|---|---|---|
| `AUDIO_STT_ENGINE` | — | STT engine: `openai`, `deepgram`, `azure` |
| `AUDIO_STT_OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | STT API base |
| `AUDIO_STT_OPENAI_API_KEY` | — | STT API key |
| `AUDIO_STT_MODEL` | `whisper-1` | STT model |
| `AUDIO_TTS_ENGINE` | — | TTS engine: `openai`, `elevenlabs`, `azure`, `mistral` |
| `AUDIO_TTS_OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | TTS API base |
| `AUDIO_TTS_OPENAI_API_KEY` | — | TTS API key |
| `AUDIO_TTS_MODEL` | `tts-1` | TTS model |
| `AUDIO_TTS_VOICE` | `alloy` | TTS voice |
| `WHISPER_MODEL` | `base` | Local Whisper model size |
| `WHISPER_COMPUTE_TYPE` | `float32` | Compute type (`float16` for older GPU) |

---

## Image Generation

| Variable | Default | Description |
|---|---|---|
| `ENABLE_IMAGE_GENERATION` | `false` | Enable image generation feature |
| `IMAGE_GENERATION_ENGINE` | `openai` | Engine: `openai`, `comfyui`, `automatic1111`, `gemini` |
| `IMAGES_OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | Image API base |
| `IMAGES_OPENAI_API_KEY` | — | Image API key |
| `IMAGE_GENERATION_MODEL` | `dall-e-3` | Image model |
| `COMFYUI_BASE_URL` | — | ComfyUI server URL |
| `AUTOMATIC1111_BASE_URL` | — | Automatic1111 server URL |

---

## Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL URL. If unset, SQLite at `$DATA_DIR/webui.db` |
| `DATABASE_POOL_SIZE` | `0` | SQLAlchemy pool size (0 = NullPool) |
| `DATABASE_POOL_TIMEOUT` | `30` | Pool connection timeout (seconds) |
| `DATABASE_POOL_RECYCLE` | `3600` | Connection recycle interval |

---

## Logging

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Python log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `AUDIT_LOG_LEVEL` | `none` | `read`, `write`, or `none` |
| `AUDIT_LOGS_FILE_PATH` | — | Path to write audit log JSON |

---

## Networking / Proxy

| Variable | Default | Description |
|---|---|---|
| `UVICORN_WORKERS` | `1` | Number of Uvicorn worker processes |
| `PORT` | `8080` | Internal listen port |
| `HOST` | `0.0.0.0` | Bind address |
| `PROXY_MODE` | — | Set to `true` behind reverse proxy |
| `FORWARDED_ALLOW_IPS` | — | Trusted proxy IPs for X-Forwarded-For |

---

## Security Notes

1. Always set `WEBUI_SECRET_KEY` explicitly — do not rely on the random default in multi-node or persistent deployments.
2. Use Docker/Kubernetes secrets for `WEBUI_ADMIN_PASSWORD`, `OPENAI_API_KEY`, etc. — never in plain text `.env` files committed to version control.
3. After bootstrap, change admin password in the UI immediately.
4. Enable `API_KEY_ALLOWED_ENDPOINTS` for service accounts with limited scope.
5. Set `JWT_EXPIRES_IN` to a reasonable value (e.g. `10d`) in production.
