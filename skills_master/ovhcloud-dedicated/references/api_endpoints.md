# OVHcloud API Endpoints Reference — Dedicated Servers

Complete list of API paths used by this skill. Use these when generating API tokens at `https://{region}.api.ovh.com/createToken/`.

## Table of Contents

1. [Server Discovery & Info](#server-discovery--info)
2. [Power & Boot](#power--boot)
3. [IPMI / KVM](#ipmi--kvm)
4. [OS Installation](#os-installation)
5. [Network & IP](#network--ip)
6. [Firewall](#firewall)
7. [Monitoring](#monitoring)
8. [Tasks & Interventions](#tasks--interventions)
9. [Secondary DNS](#secondary-dns)
10. [Token Scope Templates](#token-scope-templates)

---

## Server Discovery & Info

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dedicated/server` | List all servers |
| GET | `/dedicated/server/{serviceName}` | Server details |
| PUT | `/dedicated/server/{serviceName}` | Update server properties |
| GET | `/dedicated/server/{serviceName}/specifications/hardware` | Hardware specs |
| GET | `/dedicated/server/{serviceName}/specifications/network` | Network specs |
| GET | `/dedicated/server/{serviceName}/serviceInfos` | Billing/service info |

## Power & Boot

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/dedicated/server/{serviceName}/reboot` | Reboot server |
| GET | `/dedicated/server/{serviceName}/boot` | List boot options |
| GET | `/dedicated/server/{serviceName}/boot/{bootId}` | Boot option details |
| PUT | `/dedicated/server/{serviceName}` | Set bootId (via body) |

**Boot types**: `harddisk`, `rescue`, `ipxeCustomerScript`, `network`

## IPMI / KVM

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dedicated/server/{serviceName}/features/ipmi` | IPMI availability & status |
| POST | `/dedicated/server/{serviceName}/features/ipmi/access` | Request IPMI access session |
| GET | `/dedicated/server/{serviceName}/features/ipmi/access` | Get IPMI access URL/key |
| POST | `/dedicated/server/{serviceName}/features/ipmi/resetInterface` | Reset IPMI BMC |
| POST | `/dedicated/server/{serviceName}/features/ipmi/resetSessions` | Kill active sessions |
| GET | `/dedicated/server/{serviceName}/features/ipmi/test` | Test IPMI connectivity |

**Access types for POST `/access`**:
- `kvmipHtml5URL` — HTML5 KVM console (recommended)
- `kvmipJnlp` — Java KVM applet
- `serialOverLanURL` — SoL web console
- `serialOverLanSshKey` — SoL via SSH

**Parameters**:
- `ipToAllow` (string) — Your public IP to whitelist
- `ttl` (int) — Session TTL in minutes (default 15)
- `type` (string) — One of the access types above

## OS Installation

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dedicated/server/{serviceName}/install/compatibleTemplates` | List compatible OS templates |
| GET | `/dedicated/server/{serviceName}/install/compatibleTemplatePartitionSchemes` | Partition schemes |
| POST | `/dedicated/server/{serviceName}/install/start` | Start OS installation |
| GET | `/dedicated/server/{serviceName}/install/status` | Installation progress |
| GET | `/dedicated/server/{serviceName}/install/templateCapabilities` | Template capabilities |

**Install body**:
```json
{
  "templateName": "debian12_64",
  "details": {
    "customHostname": "server.example.com",
    "sshKeyName": "my-key",
    "language": "en",
    "softRaidDevices": 2
  }
}
```

## Network & IP

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dedicated/server/{serviceName}/ips` | List server IPs |
| GET | `/dedicated/server/{serviceName}/networkInterfaceController` | List NICs |
| GET | `/dedicated/server/{serviceName}/networkInterfaceController/{mac}` | NIC details |
| GET | `/dedicated/server/{serviceName}/statistics/chart` | Traffic/bandwidth charts |
| GET | `/ip/{ip}` | IP block details |
| GET | `/ip/{ip}/reverse` | List reverse DNS entries |
| GET | `/ip/{ip}/reverse/{ipReverse}` | Get reverse DNS |
| POST | `/ip/{ip}/reverse` | Create reverse DNS |
| DELETE | `/ip/{ip}/reverse/{ipReverse}` | Delete reverse DNS |

**Note**: IP blocks in URL paths must be URL-encoded (`/` → `%2F`). Example: `42.42.42.42%2F32`

**Statistics chart params**:
- `period`: `daily`, `monthly`, `weekly`, `yearly`
- `type`: `traffic:download`, `traffic:upload`, `cpu`, `memory`, etc.

## Firewall

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/ip/{ip}/firewall` | List firewalled IPs |
| POST | `/ip/{ip}/firewall` | Enable firewall on IP |
| DELETE | `/ip/{ip}/firewall/{ipOnFirewall}` | Disable firewall |
| GET | `/ip/{ip}/firewall/{ipOnFirewall}` | Firewall status |
| GET | `/ip/{ip}/firewall/{ipOnFirewall}/rule` | List rules |
| GET | `/ip/{ip}/firewall/{ipOnFirewall}/rule/{sequence}` | Rule details |
| POST | `/ip/{ip}/firewall/{ipOnFirewall}/rule` | Create rule |
| DELETE | `/ip/{ip}/firewall/{ipOnFirewall}/rule/{sequence}` | Delete rule |
| GET | `/ip/{ip}/mitigation` | List mitigation status |
| POST | `/ip/{ip}/mitigation` | Enable anti-DDoS |
| DELETE | `/ip/{ip}/mitigation/{ipOnMitigation}` | Disable anti-DDoS |
| GET | `/ip/{ip}/mitigation/{ipOnMitigation}` | Mitigation details |

**Firewall rule body**:
```json
{
  "sequence": 0,
  "action": "permit",
  "protocol": "tcp",
  "destinationPort": "22",
  "source": "203.0.113.0/24",
  "sourcePort": null,
  "tcpOption": null,
  "fragments": false
}
```

**Actions**: `permit`, `deny`
**Protocols**: `tcp`, `udp`, `icmp`, `ipv4`, `ipv6`
**Sequence**: 0-19 (lower = higher priority, implicit deny after last rule)

## Monitoring

| Method | Path | Purpose |
|--------|------|---------|
| PUT | `/dedicated/server/{serviceName}` | Enable/disable via `monitoring` field |
| GET | `/dedicated/server/{serviceName}/serviceMonitoring` | List monitored services |
| GET | `/dedicated/server/{serviceName}/serviceMonitoring/{monitoringId}` | Service details |
| POST | `/dedicated/server/{serviceName}/serviceMonitoring` | Add monitoring |
| DELETE | `/dedicated/server/{serviceName}/serviceMonitoring/{monitoringId}` | Remove monitoring |

## Tasks & Interventions

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dedicated/server/{serviceName}/task` | List all tasks |
| GET | `/dedicated/server/{serviceName}/task/{taskId}` | Task details |
| POST | `/dedicated/server/{serviceName}/task/{taskId}/cancel` | Cancel task |
| GET | `/dedicated/server/{serviceName}/intervention` | List interventions |
| GET | `/dedicated/server/{serviceName}/intervention/{interventionId}` | Intervention details |

**Task statuses**: `doing`, `done`, `error`, `cancelled`, `todo`, `init`

## Secondary DNS

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dedicated/server/{serviceName}/secondaryDnsDomains` | List zones |
| GET | `/dedicated/server/{serviceName}/secondaryDnsDomains/{domain}` | Zone details |
| POST | `/dedicated/server/{serviceName}/secondaryDnsDomains` | Add zone |
| PUT | `/dedicated/server/{serviceName}/secondaryDnsDomains/{domain}` | Update zone |
| DELETE | `/dedicated/server/{serviceName}/secondaryDnsDomains/{domain}` | Remove zone |

---

## Token Scope Templates

### Full Admin (read/write everything)

```
GET    /dedicated/server/*
PUT    /dedicated/server/*
POST   /dedicated/server/*
DELETE /dedicated/server/*
GET    /ip/*
PUT    /ip/*
POST   /ip/*
DELETE /ip/*
```

### Read-Only Monitoring

```
GET /dedicated/server/*
GET /ip/*
```

### IPMI/KVM Access Only

```
GET  /dedicated/server/*/features/ipmi
GET  /dedicated/server/*/features/ipmi/access
POST /dedicated/server/*/features/ipmi/access
POST /dedicated/server/*/features/ipmi/resetInterface
```

### Firewall Management Only

```
GET    /ip/*/firewall/*
POST   /ip/*/firewall/*
DELETE /ip/*/firewall/*
GET    /ip/*/mitigation/*
POST   /ip/*/mitigation/*
DELETE /ip/*/mitigation/*
```

---

## API Regions

| Endpoint ID | Base URL | Region |
|-------------|----------|--------|
| `ovh-eu` | `https://eu.api.ovh.com/1.0` | Europe |
| `ovh-us` | `https://api.us.ovhcloud.com/1.0` | USA |
| `ovh-ca` | `https://ca.api.ovh.com/1.0` | Canada |
| `kimsufi-eu` | `https://eu.api.kimsufi.com/1.0` | Kimsufi EU |
| `soyoustart-eu` | `https://eu.api.soyoustart.com/1.0` | So You Start EU |
| `kimsufi-ca` | `https://ca.api.kimsufi.com/1.0` | Kimsufi CA |
| `soyoustart-ca` | `https://ca.api.soyoustart.com/1.0` | So You Start CA |

Token creation URLs follow the pattern: `https://{base}/createToken/`
API console: `https://{base}/console/`
