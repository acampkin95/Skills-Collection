---
name: ovhcloud-dedicated
description: OVHcloud dedicated server admin via API — lifecycle, IPMI/KVM, network, firewall, OS install, monitoring, bandwidth, and hardware RAID.
version: 2.0.0
reviewed: "2026-06-04"
---
# OVHcloud Dedicated Server Management Skill

Comprehensive remote administration of OVHcloud dedicated servers via the REST API. Covers the full server lifecycle from provisioning through daily operations to incident response.

## Prerequisites

### Python SDK

```bash
pip install ovh --break-system-packages
```

### Credential Setup

Create `~/.config/ovh.conf` (or set environment variables):

```ini
[default]
; OVH API endpoint — use the one matching your account region
; ovh-eu | ovh-us | ovh-ca | kimsufi-eu | soyoustart-eu
endpoint=ovh-eu

[ovh-eu]
application_key=YOUR_AK
application_secret=YOUR_AS
consumer_key=YOUR_CK
```

**Environment variable alternative** (takes precedence over config file):

```bash
export OVH_ENDPOINT=ovh-eu
export OVH_APPLICATION_KEY=YOUR_AK
export OVH_APPLICATION_SECRET=YOUR_AS
export OVH_CONSUMER_KEY=YOUR_CK
```

**Generating credentials:**

1. Visit `https://eu.api.ovh.com/createToken/` (swap `eu` for your region)
2. Set access rules for the endpoints you need (see `references/api_endpoints.md` for the full list)
3. Recommended minimum scopes for this skill:
   - `GET /dedicated/server/*`
   - `PUT /dedicated/server/*`
   - `POST /dedicated/server/*`
   - `DELETE /dedicated/server/*`
   - `GET /ip/*`
   - `PUT /ip/*`
   - `POST /ip/*`
   - `DELETE /ip/*`

## Quick Reference

| Script | Purpose |
|--------|---------|
| `scripts/ovh_server.py` | All-in-one dedicated server management CLI |

Run `python3 scripts/ovh_server.py --help` for full command list.

## Core Operations

### Server Discovery & Info

```bash
# List all dedicated servers on the account
python3 scripts/ovh_server.py list

# Get full server details (hardware, OS, status, IPs, datacenter)
python3 scripts/ovh_server.py info SERVER_NAME

# Get hardware specifications (CPU, RAM, disks)
python3 scripts/ovh_server.py hardware SERVER_NAME

# Get current service status and expiry
python3 scripts/ovh_server.py service SERVER_NAME
```

### Power & Boot Management

```bash
# Soft reboot (graceful OS restart)
python3 scripts/ovh_server.py reboot SERVER_NAME

# Hard reboot (forced power cycle via IPMI)
python3 scripts/ovh_server.py reboot SERVER_NAME --hard

# Boot into rescue mode (netboot)
python3 scripts/ovh_server.py rescue SERVER_NAME --enable
python3 scripts/ovh_server.py rescue SERVER_NAME --disable

# Change boot mode (set boot ID)
python3 scripts/ovh_server.py boot SERVER_NAME --list
python3 scripts/ovh_server.py boot SERVER_NAME --set BOOT_ID

# Get current boot configuration
python3 scripts/ovh_server.py boot SERVER_NAME --current
```

### IPMI / KVM Console Access


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.