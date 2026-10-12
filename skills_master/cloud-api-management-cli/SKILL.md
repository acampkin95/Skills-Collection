---
name: cloud-api-management-cli
description: Manages Cloudflare DNS, firewall, cache, and SSL settings, Tailscale devices, auth keys, DNS, and ACLs, Contabo S3-compatible object storage, GitHub repositories and workflows, and Perplexity search from the command line with bundled Python scripts. Use when listing or changing DNS records, purging the Cloudflare cache, blocking an IP, managing Tailscale devices or auth keys, uploading or downloading Contabo buckets, triggering a GitHub workflow, or running a Perplexity search.
metadata:
  interface: "cli"
risk: high
version: "1.0.0"
---

# Cloud API Management Skill

Command-line management for Cloudflare, Tailscale, Contabo object storage, GitHub, and Perplexity search, using the scripts in `scripts/`.

**Confirmation required:** before running any command that deletes, purges, blocks, authorizes, or changes DNS records, firewall rules, SSL settings, Tailscale devices, auth keys, or ACLs, uploads or deletes storage objects, or runs a deploy or scale action, state the exact command and target and get explicit user confirmation.

## Workers and 2025 Platform Notes

Read `references/cloudflare-workers-notes.md` only when the user asks about the 2025 Cloudflare Workers announcements. Those notes were not re-verified on 2026-10-12.

## Quick Reference

| Script | Purpose |
|--------|---------|
| `cloudflare_api.py` | Cloudflare DNS, firewall, cache, SSL, zones, Workers, analytics, page rules |
| `tailscale_api.py` | Tailscale devices, DNS, auth keys, ACLs, tailnet info |
| `contabo_storage.py` | S3-compatible object storage operations |
| `github_api.py` | GitHub repos, issues, PRs, releases, actions |
| `perplexity_search.py` | AI-powered search queries |
| `cloud-orchestrator.py` | Multi-service `deploy`, `status`, `logs`, and `scale`; read its `--help` before use (deploy and scale change live services) |

Not bundled: `service_discovery.py` and `ddns.py`. Earlier versions referenced them; their examples are kept in references (see Cloudflare and Service Discovery sections).

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

The commands below match `python3 scripts/cloudflare_api.py --help` in this bundle. Add `--json` for raw output and `--zone ZONE_ID` to target another zone. Earlier examples for round-robin pools, DDNS, WAF expressions, proxy settings, SSL modes, zone creation, and DNS import or export are kept in `references/cloudflare-unimplemented-commands.md`. This script does not implement them.

### DNS

```bash
# List DNS records (no filter flags)
python3 scripts/cloudflare_api.py dns list

# Create a record (--ttl 1 means automatic)
python3 scripts/cloudflare_api.py dns create --type A --name api --content 1.2.3.4 --ttl 1 --proxied

# Update a record: needs the record ID plus type, name, and content
python3 scripts/cloudflare_api.py dns update --id RECORD_ID --type A --name api --content 5.6.7.8

# Delete a record
python3 scripts/cloudflare_api.py dns delete --id RECORD_ID
```

### Firewall (IP rules)

```bash
python3 scripts/cloudflare_api.py firewall list
python3 scripts/cloudflare_api.py firewall access
python3 scripts/cloudflare_api.py firewall block --ip 1.2.3.4 --notes "Repeated failed logins"
python3 scripts/cloudflare_api.py firewall allow --ip 5.6.7.8 --notes "Office gateway"
```

### Cache

```bash
python3 scripts/cloudflare_api.py cache purge --all
python3 scripts/cloudflare_api.py cache purge --urls "https://example.com/page1,https://example.com/page2"
python3 scripts/cloudflare_api.py cache purge --tags "product-123,catalog"
```

### Zones, SSL, Page Rules, Workers, Analytics

```bash
python3 scripts/cloudflare_api.py zones list
python3 scripts/cloudflare_api.py zones get
python3 scripts/cloudflare_api.py zones settings
python3 scripts/cloudflare_api.py ssl settings
python3 scripts/cloudflare_api.py ssl certs
python3 scripts/cloudflare_api.py pagerules list
python3 scripts/cloudflare_api.py workers list
python3 scripts/cloudflare_api.py workers routes
python3 scripts/cloudflare_api.py workers get --name my-worker
python3 scripts/cloudflare_api.py analytics --since -60
```

`analytics --since` takes minutes ago as a negative number (help text: "Minutes ago (negative)"), so `-60` covers about the last hour.

## Service Discovery and Certbot

Not bundled with this skill. Earlier versions documented `service_discovery.py` commands for DNS mapping, health checks, and certbot DNS challenges. Those examples are kept verbatim in `references/service-discovery-and-certbot.md` for reference only; they cannot run with the scripts in this skill.

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
