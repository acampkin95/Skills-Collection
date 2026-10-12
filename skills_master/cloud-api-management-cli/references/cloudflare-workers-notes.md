# Cloudflare Workers notes (2025 announcements)

Moved verbatim from SKILL.md on 2026-10-12. These notes describe 2025 announcements and were not re-verified against current Cloudflare documentation.

## 2025 Cloudflare Workers Updates

### New REST API (Beta)

Cloudflare introduced a simplified REST API for Workers management:

**Key improvements:**
- **Workers as standalone resources** - Create workers and establish identity before uploading code
- **Immutable Versions** - Code snapshots with specific configurations
- **Explicit Deployments** - Traffic direction is now an explicit action
- **Dual addressing** - Address by UUID (immutable) or name (mutable)

**New API structure:**
```json
{
  "name": "my-worker",
  "main_module": "index.js",
  "compatibility_date": "2025-01-01"
}
```

### Node.js Compatibility Expansion

Workers now support hundreds of Node.js APIs natively:
- `node:http` - HTTP client/server support
- `node:fs` - Virtual file system
- `node:net`, `node:tls` - Socket/TLS support

Enable via compatibility flags in `wrangler.toml`:
```toml
compatibility_flags = ["nodejs_compat"]
```

### Containers Coming June 2025

Workers will function as:
- **API Gateway** - Routing, authentication, caching, rate-limiting
- **Service Mesh** - Private connections with programmable routing
- **Orchestrator** - Custom scheduling, scaling, health checking
