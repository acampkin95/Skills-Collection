# Service discovery and certbot examples from an earlier version

Moved verbatim from SKILL.md on 2026-10-12. `scripts/service_discovery.py` is not bundled with this skill, so the service and zone commands below cannot run as written. The certbot command is standard certbot usage and does not depend on the bundled scripts.

## Service Discovery (script not bundled)

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
