---
name: ovhcloud-dedicated
description: OVHcloud dedicated server remote administration via API — server lifecycle, IPMI/KVM console access, network configuration, firewall rules, OS reinstallation, boot modes, monitoring, bandwidth stats, IP management, reverse DNS, hardware RAID, and intervention history. Use this skill whenever the user mentions OVHcloud, OVH dedicated server, OVH API, OVH IPMI, OVH KVM, OVH server reboot, OVH rescue mode, OVH network config, OVH firewall, OVH reverse DNS, OVH bandwidth, OVH monitoring, OVH hardware specs, OVH OS install, OVH boot mode, OVH server tasks, OVH interventions, dedicated server API management, bare metal cloud OVH, or any task involving programmatic control of OVHcloud dedicated servers — even if they just say "check my server" or "reboot the dedi". Also trigger when the user wants to automate OVH infrastructure, script OVH server provisioning, manage multiple OVH servers, or troubleshoot OVH connectivity via IPMI/KVM/SoL.
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

```bash
# Test IPMI availability
python3 scripts/ovh_server.py ipmi SERVER_NAME --test

# Get KVM access URL (HTML5 web console)
python3 scripts/ovh_server.py ipmi SERVER_NAME --kvm-html

# Get KVM access URL (Java applet)
python3 scripts/ovh_server.py ipmi SERVER_NAME --kvm-java

# Get Serial-over-LAN (SoL) SSH access
python3 scripts/ovh_server.py ipmi SERVER_NAME --sol-ssh

# Get SoL web access
python3 scripts/ovh_server.py ipmi SERVER_NAME --sol-web

# Reset IPMI interface (if console is stuck/unresponsive)
python3 scripts/ovh_server.py ipmi SERVER_NAME --reset
```

The `--kvm-*` and `--sol-*` commands require your public IP to be whitelisted. The script auto-detects your IP via `ifconfig.ovh`, or you can pass `--ip YOUR_IP`. Access URLs have a TTL (default 15 minutes).

### OS Installation

```bash
# List available OS templates
python3 scripts/ovh_server.py os SERVER_NAME --list

# List available OVH templates (pre-configured)
python3 scripts/ovh_server.py os SERVER_NAME --list-ovh

# Install an OS (DESTRUCTIVE — wipes all data)
python3 scripts/ovh_server.py os SERVER_NAME --install TEMPLATE_NAME

# Install with SSH key and custom hostname
python3 scripts/ovh_server.py os SERVER_NAME --install debian12_64 \
  --hostname myserver.example.com \
  --ssh-key "ssh-ed25519 AAAA..."

# Check install task status
python3 scripts/ovh_server.py tasks SERVER_NAME
```

### Network & IP Management

```bash
# List all IPs assigned to server
python3 scripts/ovh_server.py ip SERVER_NAME --list

# Get IP details (reverse DNS, type, routed-to)
python3 scripts/ovh_server.py ip SERVER_NAME --detail IP_ADDRESS

# Set reverse DNS
python3 scripts/ovh_server.py ip SERVER_NAME --reverse IP_ADDRESS --value host.example.com

# Delete reverse DNS
python3 scripts/ovh_server.py ip SERVER_NAME --reverse IP_ADDRESS --delete

# Get network interfaces
python3 scripts/ovh_server.py network SERVER_NAME --interfaces

# Get bandwidth usage stats
python3 scripts/ovh_server.py network SERVER_NAME --bandwidth
python3 scripts/ovh_server.py network SERVER_NAME --bandwidth --period monthly

# Get traffic stats (download/upload in bytes)
python3 scripts/ovh_server.py network SERVER_NAME --traffic
```

### Firewall (OVH Network Firewall)

```bash
# List firewall rules on an IP
python3 scripts/ovh_server.py firewall IP_BLOCK --list

# Get specific rule detail
python3 scripts/ovh_server.py firewall IP_BLOCK --rule SEQUENCE_NUMBER

# Add firewall rule
python3 scripts/ovh_server.py firewall IP_BLOCK --add \
  --sequence 1 \
  --action permit \
  --protocol tcp \
  --dest-port 22 \
  --source "0.0.0.0/0"

# Remove firewall rule
python3 scripts/ovh_server.py firewall IP_BLOCK --remove SEQUENCE_NUMBER

# Enable/disable firewall on IP
python3 scripts/ovh_server.py firewall IP_BLOCK --enable
python3 scripts/ovh_server.py firewall IP_BLOCK --disable

# Enable/disable mitigation (anti-DDoS)
python3 scripts/ovh_server.py firewall IP_BLOCK --mitigation on
python3 scripts/ovh_server.py firewall IP_BLOCK --mitigation off
```

### Monitoring & Alerts

```bash
# Get monitoring status
python3 scripts/ovh_server.py monitoring SERVER_NAME --status

# Enable/disable OVH monitoring
python3 scripts/ovh_server.py monitoring SERVER_NAME --enable
python3 scripts/ovh_server.py monitoring SERVER_NAME --disable

# List monitoring alerts/notifications
python3 scripts/ovh_server.py monitoring SERVER_NAME --alerts
```

### Tasks & Interventions

```bash
# List active/recent tasks (reboots, installs, etc.)
python3 scripts/ovh_server.py tasks SERVER_NAME

# Get specific task details
python3 scripts/ovh_server.py tasks SERVER_NAME --id TASK_ID

# List datacenter interventions (physical hardware work)
python3 scripts/ovh_server.py interventions SERVER_NAME

# Cancel a pending task
python3 scripts/ovh_server.py tasks SERVER_NAME --cancel TASK_ID
```

### Secondary DNS

```bash
# List secondary DNS zones
python3 scripts/ovh_server.py dns SERVER_NAME --list

# Add secondary DNS
python3 scripts/ovh_server.py dns SERVER_NAME --add DOMAIN --ip DNS_SERVER_IP

# Remove secondary DNS
python3 scripts/ovh_server.py dns SERVER_NAME --remove DOMAIN
```

### Server Configuration

```bash
# Update display name
python3 scripts/ovh_server.py config SERVER_NAME --display-name "Production Web 01"

# Enable/disable monitoring
python3 scripts/ovh_server.py config SERVER_NAME --monitoring true

# Set rescue email
python3 scripts/ovh_server.py config SERVER_NAME --rescue-mail admin@example.com

# Get full server properties (JSON dump)
python3 scripts/ovh_server.py config SERVER_NAME --dump
```

## Common Workflows

### Emergency Server Recovery

When a server is unresponsive and SSH is down:

1. **Test IPMI**: `ovh_server.py ipmi SERVER --test`
2. **Try KVM console**: `ovh_server.py ipmi SERVER --kvm-html`
3. **If KVM fails, reset IPMI**: `ovh_server.py ipmi SERVER --reset`
4. **If OS is broken, enable rescue**: `ovh_server.py rescue SERVER --enable`
5. **Hard reboot into rescue**: `ovh_server.py reboot SERVER --hard`
6. **Access via rescue SSH** (credentials sent to account email)
7. **Fix issues, then disable rescue**: `ovh_server.py rescue SERVER --disable`
8. **Reboot back to normal**: `ovh_server.py reboot SERVER`

### Lock Down a New Server

1. List IPs: `ovh_server.py ip SERVER --list`
2. Enable firewall: `ovh_server.py firewall IP_BLOCK --enable`
3. Allow SSH from your IP only:
   ```bash
   ovh_server.py firewall IP_BLOCK --add --sequence 0 --action permit \
     --protocol tcp --dest-port 22 --source "YOUR_IP/32"
   ```
4. Allow HTTP/HTTPS:
   ```bash
   ovh_server.py firewall IP_BLOCK --add --sequence 1 --action permit \
     --protocol tcp --dest-port 80 --source "0.0.0.0/0"
   ovh_server.py firewall IP_BLOCK --add --sequence 2 --action permit \
     --protocol tcp --dest-port 443 --source "0.0.0.0/0"
   ```
5. Block everything else (implicit deny at end of chain)
6. Set reverse DNS: `ovh_server.py ip SERVER --reverse IP --value server.example.com`

### Reinstall OS

1. List templates: `ovh_server.py os SERVER --list`
2. Install: `ovh_server.py os SERVER --install debian12_64 --ssh-key "ssh-ed25519 ..."`
3. Monitor task: `ovh_server.py tasks SERVER`
4. Wait for completion (typically 10-20 minutes)

## API Endpoints Reference

For the full list of OVH API endpoints used by this skill, read `references/api_endpoints.md`.

## Security Notes

1. **Never hardcode credentials** — use `~/.config/ovh.conf` or environment variables
2. **Restrict token scopes** — only grant the API paths you actually need
3. **Rotate consumer keys** after any suspected exposure
4. **Protect config file**: `chmod 600 ~/.config/ovh.conf`
5. **IPMI access is IP-whitelisted** — URLs expire after their TTL
6. **OS install is destructive** — always confirm before executing
7. **Hard reboot risks data loss** — prefer soft reboot when possible

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| `403 Forbidden` | Consumer key lacks required scope — regenerate with correct ACL |
| `404 Not Found` | Wrong `serviceName` — run `list` to get exact server names |
| IPMI/KVM blank screen | Reset IPMI via `--reset`, wait 5 min, retry |
| SoL shows no output | Configure GRUB serial console (see `references/sol_setup.md`) |
| Install task stuck | Check `tasks` — may need support ticket if stuck >1hr |
| Firewall rules not applying | Ensure firewall is `--enable`d on the IP block |
| Wrong endpoint region | Check `ovh.conf` endpoint matches your account (eu/us/ca) |
