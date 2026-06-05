---
name: cloud-api-management
description: Cloud infrastructure and API management, for Cloudflare, Tailscale, S3 storage.
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
python3 scripts/tailscale_api.py dns nameservers
python3 scripts/tailscale_api.py dns nameservers --set "1.1.1.1,8.8.8.8"

# Toggle MagicDNS
python3 scripts/tailscale_api.py dns magicdns on
python3 scripts/tailscale_api.py dns magicdns off

# Get/set search paths
python3 scripts/tailscale_api.py dns searchpaths
python3 scripts/tailscale_api.py dns searchpaths --set "corp.example.com,internal.local"
```

### Auth Keys

```bash
# List all auth keys
python3 scripts/tailscale_api.py keys list

# Create auth key
python3 scripts/tailscale_api.py keys create --description "Server deployment"

# Create reusable ephemeral key with tags
python3 scripts/tailscale_api.py keys create --reusable --ephemeral --tags "tag:server,tag:prod" --expiry 604800

# Delete key
python3 scripts/tailscale_api.py keys delete KEY_ID
```

### ACL/Policy Management

```bash
# Get current ACL
python3 scripts/tailscale_api.py acl get

# Save ACL to file
python3 scripts/tailscale_api.py acl get --output acl-backup.json

# Set ACL from file
python3 scripts/tailscale_api.py acl set new-acl.json

# Validate ACL without applying
python3 scripts/tailscale_api.py acl validate proposed-acl.json
```

### Multi-Tailnet Usage

```bash
# Specify tailnet explicitly
python3 scripts/tailscale_api.py --tailnet example.com devices list
```

## Cloudflare Management

### DNS Operations

```bash
# List all DNS records
python3 scripts/cloudflare_api.py dns list

# Filter by type or name
python3 scripts/cloudflare_api.py dns list --type A --name api

# Create record
python3 scripts/cloudflare_api.py dns create -t A -n api -c 1.2.3.4 --proxied

# Update record
python3 scripts/cloudflare_api.py dns update RECORD_ID -t A -n api -c 5.6.7.8

# Delete record
python3 scripts/cloudflare_api.py dns delete RECORD_ID

# Export/import BIND format
python3 scripts/cloudflare_api.py dns export > zone.txt
python3 scripts/cloudflare_api.py dns import zone.txt
```

### Round Robin Load Balancing

```bash
# Create round-robin pool (multiple A records)
python3 scripts/cloudflare_api.py roundrobin create api --ips 1.1.1.1,2.2.2.2,3.3.3.3 --proxied

# Update pool (replaces all IPs)
python3 scripts/cloudflare_api.py rr update api --ips 4.4.4.4,5.5.5.5
```

### Dynamic DNS (DDNS)

```bash
# One-shot update (auto-detects public IP)
python3 scripts/cloudflare_api.py ddns home.example.com

# Specify IP manually
python3 scripts/cloudflare_api.py ddns home.example.com --ip 1.2.3.4

# IPv6
python3 scripts/cloudflare_api.py ddns home.example.com --type AAAA
```

### DDNS Daemon

```bash
# Add records to monitor
python3 scripts/ddns.py add home.example.com --zone-id ZONE_ID --proxied

# Run one-shot update
python3 scripts/ddns.py update

# Run as daemon (updates every 5 minutes)
python3 scripts/ddns.py daemon --interval 300

# Check current public IP
python3 scripts/ddns.py ip
```

### WAF & Firewall

```bash
# List firewall rules
python3 scripts/cloudflare_api.py waf rules

# Create firewall rule with expression
python3 scripts/cloudflare_api.py waf create \
  --expr '(ip.src eq 1.2.3.4)' \
  --action block \
  --desc "Block bad IP"

# Block IP/country/ASN
python3 scripts/cloudflare_api.py waf block --target ip --value 1.2.3.4
python3 scripts/cloudflare_api.py waf block --target country --value CN
python3 scripts/cloudflare_api.py waf block --target asn --value 12345

# Allow IP
python3 scripts/cloudflare_api.py waf allow --target ip --value 5.6.7.8

# Set security level
python3 scripts/cloudflare_api.py waf security high
python3 scripts/cloudflare_api.py waf security under_attack  # DDoS mode
```

### Cache Control

```bash
# Purge everything
python3 scripts/cloudflare_api.py cache purge --all

# Purge specific URLs
python3 scripts/cloudflare_api.py cache purge --urls "https://example.com/page1,https://example.com/page2"

# Purge by hostname
python3 scripts/cloudflare_api.py cache purge --hosts "api.example.com,www.example.com"

# Set cache level
python3 scripts/cloudflare_api.py cache level aggressive

# Set browser cache TTL
python3 scripts/cloudflare_api.py cache ttl 86400

# Development mode (bypasses cache)
python3 scripts/cloudflare_api.py cache dev on
```

### Proxy Settings

```bash
# Configure minification
python3 scripts/cloudflare_api.py proxy minify --html on --css on --js on

# Image optimization
python3 scripts/cloudflare_api.py proxy polish lossy

# Rocket Loader
python3 scripts/cloudflare_api.py proxy rocket on

# Always Online
python3 scripts/cloudflare_api.py proxy always-online on
```

### SSL/TLS

```bash
# Get SSL settings
python3 scripts/cloudflare_api.py ssl get

# Set SSL mode
python3 scripts/cloudflare_api.py ssl mode strict

# Set minimum TLS version
python3 scripts/cloudflare_api.py ssl tls 1.2

# Force HTTPS
python3 scripts/cloudflare_api.py ssl force-https on

# Upload custom certificate
python3 scripts/cloudflare_api.py ssl upload --cert cert.pem --key key.pem

# Create Origin CA certificate
python3 scripts/cloudflare_api.py ssl origin-ca --hosts "*.example.com,example.com" --validity 5475
```

### Zone Management

```bash
# List all zones
python3 scripts/cloudflare_api.py zones list

# Get zone details
python3 scripts/cloudflare_api.py zones get

# Get all zone settings
python3 scripts/cloudflare_api.py zones settings

# Add new domain
python3 scripts/cloudflare_api.py zones create newdomain.com

# Update zone setting
python3 scripts/cloudflare_api.py zones set security_level high

# Multi-zone operations (specify zone ID)
python3 scripts/cloudflare_api.py --zone OTHER_ZONE_ID dns list
```

## Service Discovery

Register services and automatically manage their DNS mappings.

```bash
# Register a zone
python3 scripts/service_discovery.py zone add production \
  --zone-id abc123 --domain example.com

# Register a service
python3 scripts/service_discovery.py service add api-server \
  --zone production \
  --dns api \
  --targets "10.0.0.1:8080,10.0.0.2:8080" \
  --proxied \
  --health-check tcp

# Sync service DNS (creates/updates records based on health)
python3 scripts/service_discovery.py service sync api-server

# Check service health
python3 scripts/service_discovery.py service health api-server

# Discover all DNS in a zone
python3 scripts/service_discovery.py zone discover --zone-id abc123
```

## Certbot Integration

```bash
# Generate Cloudflare credentials for certbot
python3 scripts/service_discovery.py certbot credentials

# Manual challenge creation (for automation)
python3 scripts/service_discovery.py certbot challenge example.com --token xyz

# Cleanup challenge
python3 scripts/service_discovery.py certbot cleanup example.com

# Use with certbot
certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d example.com -d "*.example.com"
```

## Contabo Object Storage

```bash
# List buckets
python3 scripts/contabo_storage.py buckets

# List objects
python3 scripts/contabo_storage.py list --prefix backups/

# Upload/download
python3 scripts/contabo_storage.py upload file.tar.gz backups/file.tar.gz
python3 scripts/contabo_storage.py download backups/file.tar.gz file.tar.gz

# Delete
python3 scripts/contabo_storage.py delete backups/old-file.tar.gz

# Presigned URL
python3 scripts/contabo_storage.py presign backups/file.tar.gz --expiry 3600
```

## GitHub API

```bash
# List repos
python3 scripts/github_api.py repos list

# Create issue
python3 scripts/github_api.py issues create owner/repo --title "Bug" --body "Description"

# List PRs
python3 scripts/github_api.py prs list owner/repo

# Trigger workflow
python3 scripts/github_api.py actions trigger owner/repo --workflow deploy.yml
```

## Perplexity AI Search

```bash
# Simple query
python3 scripts/perplexity_search.py "What is the latest in AI?"

# With reasoning model
python3 scripts/perplexity_search.py "Explain transformers" --model sonar-reasoning

# Recent results only
python3 scripts/perplexity_search.py "Latest news" --recency day

# Interactive chat
python3 scripts/perplexity_search.py --interactive
```

## Common Firewall Expressions

```bash
# Block bots
(cf.client.bot)

# Block specific user agent
(http.user_agent contains "BadBot")

# Block by country
(ip.geoip.country eq "XX")

# Protect admin
(http.request.uri.path contains "/admin") and not (ip.src in {1.2.3.4})

# Rate limit API
(http.request.uri.path contains "/api/")
```

## Security Notes

1. **Never hardcode credentials** - Use environment variables
2. **Rotate keys regularly** - Especially after exposure
3. **Use minimal permissions** - Create scoped API tokens
4. **Monitor access** - Check Cloudflare/Tailscale audit logs
5. **Secure credentials file** - `chmod 600 ~/.config/cloud-api-keys.env`
