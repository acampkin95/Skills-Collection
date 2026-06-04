---
name: proxmox-admin
description: Proxmox VE administration — VM/LXC lifecycle, snapshots, storage, networking, and cluster management.
version: 2.0.0
reviewed: "2026-06-04"
---

# Proxmox VE & Ubuntu VM Administration Skill

## Quick Reference

| Domain | Jump to section |
|---|---|
| API auth & tokens | [§ Auth](#authentication) |
| VM lifecycle (qm) | [§ VMs](#vm-management-qm) |
| LXC containers (pct) | [§ Containers](#lxc-container-management-pct) |
| Storage management | [§ Storage](#storage-management) |
| Networking / SDN | [§ Networking](#networking--sdn) |
| Cluster & HA | [§ Cluster](#cluster--high-availability) |
| Backup & PBS | [§ Backup](#backup--restore) |
| Ubuntu VM optimisation | [§ Optimise](#ubuntu-vm-optimisation) |
| User & access control | [§ Users](#user--access-control-pveum) |
| Security hardening | [§ Security](#security-hardening) |
| Automation patterns | [§ Automation](#automation-patterns) |
| Troubleshooting | [§ Troubleshoot](#troubleshooting) |

Detailed reference files (load on demand):
- `references/api-endpoints.md` — full REST API endpoint tree
- `references/cli-cheatsheet.md` — complete qm/pct/pvesh/vzdump/pvecm/pveum commands
- `references/tuning-guide.md` — deep performance tuning, CPU pinning, NUMA, I/O

---

## Environment Setup

```bash
# Set once — reference in all commands below
export PVE_HOST="pve.example.com"   # or IP
export PVE_PORT="8006"
export PVE_NODE="pve"               # node name shown in web UI
export PVE_BASE="https://$PVE_HOST:$PVE_PORT/api2/json"

# API token (preferred — no CSRF needed, no expiry)
export PVE_TOKEN="root@pam!automation=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
# Header: Authorization: PVEAPIToken=USER@REALM!TOKENID=SECRET
```

---

## Authentication

### API Tokens (preferred for automation)

```bash
# Create API token via CLI on the PVE node
pveum user token add root@pam automation --privsep 0
# privsep 0 = inherits user permissions; privsep 1 = must explicitly grant ACLs

# Create scoped token with expiry
pveum user token add monitoring@pve readonly --expire 2026-12-31

# List tokens for a user
pveum user token list root@pam

# Remove token
pveum user token remove root@pam automation

# Use in curl — no CSRF header needed
curl -sk -H "Authorization: PVEAPIToken=$PVE_TOKEN" \
  "$PVE_BASE/nodes" | jq '.data[].node'
```

### Ticket Auth (interactive / short-lived scripts)

```bash
# Obtain ticket + CSRF token
RESPONSE=$(curl -sk -d "username=root@pam&password=YOUR_PASSWORD" \
  "$PVE_BASE/access/ticket")
TICKET=$(echo "$RESPONSE" | jq -r '.data.ticket')
CSRF=$(echo "$RESPONSE"   | jq -r '.data.CSRFPreventionToken')

# GET (ticket only)
curl -sk -b "PVEAuthCookie=$TICKET" "$PVE_BASE/nodes"

# POST/PUT/DELETE (needs CSRF header)
curl -sk -X POST \
  -b "PVEAuthCookie=$TICKET" \
  -H "CSRFPreventionToken: $CSRF" \
  -d "vmid=200&node=$PVE_NODE" \
  "$PVE_BASE/nodes/$PVE_NODE/qemu/200/status/start"
```

> Tickets expire after 2 hours. API tokens never expire unless `--expire` is set.

### API Viewer

Browse `https://$PVE_HOST:8006/pve-docs/api-viewer/` for interactive endpoint explorer.

---

## VM Management (qm)

The full qm command reference (every flag, every variant) lives in
`references/cli-cheatsheet.md`. The essentials:

### List & Status

```bash
qm list                  # all VMs on this node
qm status <vmid>         # running/stopped/paused
qm config <vmid>         # full config
pvesh get /cluster/resources --type vm --output-format json-pretty  # cluster-wide
```

### Create a minimal Ubuntu VM

```bash
qm create 200 \
  --name ubuntu-srv --ostype l26 \
  --cores 2 --memory 4096 \
  --bios ovmf --machine q35 \
  --efidisk0 local-lvm:0,efitype=4m,pre-enrolled-keys=0 \
  --scsihw virtio-scsi-single \
  --scsi0 local-lvm:32,iothread=1,ssd=1,discard=on \
  --ide2 local:iso/ubuntu-24.04-server.iso,media=cdrom \
  --boot order=ide2 \
  --net0 virtio,bridge=vmbr0,firewall=1 \
  --agent enabled=1,fstrim_cloned_disks=1 --onboot 1
qm start 200
```

### Lifecycle

```bash
qm start <vmid>      # power on
qm shutdown <vmid>   # graceful ACPI shutdown
qm stop <vmid>       # hard power off
qm reboot <vmid>     # graceful reboot
qm destroy <vmid> --purge   # delete VM + volumes + config
```

### Reconfigure

```bash
qm set <vmid> --cores 4 --memory 8192     # CPU / memory
qm set <vmid> --scsi1 local-lvm:20        # add disk
qm resize <vmid> scsi0 +20G               # grow disk
qm set <vmid> --net0 virtio,bridge=vmbr1  # change net
```

### Snapshots, Clones, Migration

```bash
qm snapshot <vmid> snap-name --description "Before upgrade"
qm rollback <vmid> snap-name
qm clone 100 200 --name new-vm --full --storage local-lvm

See [full-reference.md](references/full-reference.md) for complete details and advanced patterns.