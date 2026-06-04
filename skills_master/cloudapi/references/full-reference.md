---
name: cloud-api-management
description: Cloud infrastructure and API management for Cloudflare, Tailscale, S3 storage, and GitHub automation. Use this skill when Cloudflare DNS, Cloudflare Workers, Workers REST API, Tailscale networking, Tailscale ACLs, S3-compatible storage, GitHub API, GitHub Actions automation, Contabo Object Storage, firewall rules, CDN configuration, DNS zones, Tailscale devices. Use this skill when managing DNS zones and records, configuring CDN and firewall rules, setting up Tailscale networking and access control, implementing object storage solutions, automating GitHub repository workflows, managing cloud infrastructure APIs, and integrating third-party cloud services.
---
# Cloud API Management Skill

Comprehensive cloud infrastructure management with secure credential handling.

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

## Quick Reference

| Script | Purpose |
|--------|---------|
| `cloudflare_api.py` | Full Cloudflare management (DNS, WAF, cache, SSL, workers) |
| `tailscale_api.py` | Tailscale management (devices, DNS, keys, ACLs, routes) |
| `service_discovery.py` | Service-to-DNS mapping, health checks, certbot integration |
| `ddns.py` | Dynamic DNS daemon for automatic IP updates |
| `contabo_storage.py` | S3-compatible object storage operations |
| `github_api.py` | GitHub repos, issues, PRs, releases, actions |
| `perplexity_search.py` | AI-powered search queries |

## Credential Setup

Create `~/.config/cloud-api-keys.env` and source it before use. See `references/credentials_setup.md` for details.

```bash
source ~/.config/cloud-api-keys.env
```

## Tailscale Management

### Device Operations

```bash
# List all devices
python3 scripts/tailscale_api.py devices list

# List with verbose details
python3 scripts/tailscale_api.py devices list -v

# List as JSON
python3 scripts/tailscale_api.py devices list --json

# Get specific device
python3 scripts/tailscale_api.py devices get DEVICE_ID

# Delete device
python3 scripts/tailscale_api.py devices delete DEVICE_ID

# Authorize/deauthorize device
python3 scripts/tailscale_api.py devices authorize DEVICE_ID
python3 scripts/tailscale_api.py devices authorize DEVICE_ID --disable

# Set device tags
python3 scripts/tailscale_api.py devices tags DEVICE_ID --tags "server,production"

# Manage device routes
python3 scripts/tailscale_api.py devices routes DEVICE_ID
python3 scripts/tailscale_api.py devices routes DEVICE_ID --enable "10.0.0.0/24,192.168.1.0/24"
```

### DNS Operations

```bash
# Get/set nameservers

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.