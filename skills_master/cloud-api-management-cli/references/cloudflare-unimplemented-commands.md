# Cloudflare command examples from an earlier version

Moved verbatim from SKILL.md on 2026-10-12. The bundled `scripts/cloudflare_api.py` does not implement most of the commands below. Its command tree, checked with `--help` on 2026-10-12, is: dns (list, create, update, delete), zones (list, get, settings), cache (purge), firewall (list, access, block, allow), workers (list, routes, get), analytics, pagerules (list), and ssl (settings, certs). Do not run these examples against the bundled script. Use them only after adding the feature, or with a different tool that provides it.

## Cloudflare Management (earlier version, not implemented)

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
