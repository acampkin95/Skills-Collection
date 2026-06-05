# Proxmox Maintenance Routine — Full Reference

Periodic audit procedure for hv01 (vd-syd-dc-hv01) and all resident VMs/LXCs.
Run approximately monthly or after any major infra change.

---

## 1. SSH Access Pattern

```bash
# All access via Tailscale — never public IP
# Primary identity key
~/.ssh/vd-masterkey

# Direct SSH (explicit key required — SSH config wildcard 'Host 100.*' has no IdentityFile)
ssh -i ~/.ssh/vd-masterkey root@100.118.114.56   # hv01
ssh -i ~/.ssh/vd-masterkey root@100.111.195.74   # proxy01
ssh -i ~/.ssh/vd-masterkey root@100.125.96.56    # docker01
ssh -i ~/.ssh/vd-masterkey root@100.109.96.107   # db01
ssh -i ~/.ssh/vd-masterkey root@100.90.175.111   # ops01
ssh -i ~/.ssh/vd-masterkey root@100.118.164.120  # ai01
ssh -i ~/.ssh/vd-masterkey root@100.107.75.57    # web01
```

**GOTCHA — web01 / LXC SSH via hv01 LAN:** Attempting to jump via hv01
to a LXC's LAN IP (`ssh root@10.10.0.20` from inside hv01) times out —
LXC networking blocks inbound SSH from the hypervisor host in this config.
Always use the Tailscale IP directly.

**GOTCHA — LXC without vd-masterkey:** If direct SSH returns
`Permission denied (publickey)`, push the key via pct exec first:

```bash
# On macOS, get the public key
cat ~/.ssh/vd-masterkey.pub
# Then push it to the LXC from hv01
pct exec <vmid> -- bash -c "mkdir -p /root/.ssh && chmod 700 /root/.ssh && \
  echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAIuKhvtdpwQHUw1O0oRaWppXrJKYqTI0i3bG4q5qApr vd-masterkey-2026-04-13' \
  >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys"
# Verify
ssh -i ~/.ssh/vd-masterkey root@<tailscale-ip>
```

---

## 2. HV01 Hypervisor Audit

```bash
# SSH in
ssh -i ~/.ssh/vd-masterkey root@100.118.114.56

# PVE version
pveversion -v

# Running guests
qm list && pct list

# Failed systemd units
systemctl --failed

# Storage summary
pvesm status

# Disk usage overview
df -h

# Old kernel count (prune if > 2 old kernels)
ls /boot/vmlinuz-* | wc -l
dpkg -l | grep linux-image
# Remove old: apt purge linux-image-<old-version>-pve
```

### ZFS Pool Health

```bash
# Status — look for ONLINE/DEGRADED/FAULTED
zpool status data

# Capacity — alert if USE% > 70%
zpool list data

# Per-dataset breakdown
zfs list -t filesystem -o name,used,avail,refer,compressratio | sort -k2 -rh

# ARC stats
cat /proc/spl/kstat/zfs/arcstats | grep -E "^(size|c_max|hits|misses) "
# c_max should be ~16GB (17179869184) for a 64GB host

# Compression setting
zfs get compression data

# Scrub schedule
cat /etc/cron.d/zfs-scrub
# Expected: 0 3 * * 0 root /sbin/zpool scrub data
```

**ZFS tuning applied (2026-06-05):**
- ARC cap: `/etc/modprobe.d/zfs-arc.conf` → `options zfs zfs_arc_max=17179869184`
- Apply without reboot: `echo 17179869184 > /sys/module/zfs/parameters/zfs_arc_max`
- Compression enabled: `zfs set compression=lz4 data`

### Backup Inventory

```bash
# List all vzdump backups (each backup = .vma.zst + .log + .notes)
ls -lh /var/lib/vz/dump/ | grep vzdump | sort

# Count per VMID
ls /var/lib/vz/dump/vzdump-*.vma.zst 2>/dev/null | \
  sed 's/.*vzdump-[^-]*-\([0-9]*\)-.*/\1/' | sort | uniq -c | sort -rn
```

**GOTCHA — pvesm prune-backups is broken on PVE 9.1.9:** Both documented
forms (`pvesm prune-backups --prune-backups 'keep-last=2' --storage local`
and `pvesm prune-backups local --prune-backups 'keep-last=2'`) return
`Unknown option: prune-backups`. Use manual deletion instead:

```bash
# Manual prune — keep last 2 per VMID, delete oldest
# Identify excess (example: VMID 104 has 4 backups, delete 2 oldest)
ls -lt /var/lib/vz/dump/vzdump-*-104-*.vma.zst

# Delete a backup set (3 files: .vma.zst, .log, .notes)
rm /var/lib/vz/dump/vzdump-qemu-104-2026_05_15-02_00_44.vma.zst
rm /var/lib/vz/dump/vzdump-qemu-104-2026_05_15-02_00_44.log
rm /var/lib/vz/dump/vzdump-qemu-104-2026_05_15-02_00_44.notes

# Recover orphan .log/.notes with no matching .vma.zst
for f in /var/lib/vz/dump/*.log; do
  base="${f%.log}"
  [ -f "${base}.vma.zst" ] || echo "ORPHAN: $f"
done
```

### Notification Verification

```bash
# Check mail-to-root endpoint has a recipient set
pvesh get /cluster/notifications/endpoints/sendmail/mail-to-root
# Look for "mailto" field — must be non-empty

# Fix if missing
pvesh set /cluster/notifications/endpoints/sendmail/mail-to-root \
  --mailto acampkinpersonnal@gmail.com

# Test notification
pvesh create /cluster/notifications/targets/mail-to-root/test
```

**GOTCHA:** The PVE notification endpoint (`mail-to-root`) and the postfix
relay are independent layers. hv01 postfix already relays via mailcow SASL
on port 587. Silent failures (`no recipients provided for the mail`) are
caused by the endpoint having no `mailto` configured — not a relay issue.

### Logrotate Check

```bash
# Dry-run to catch errors
logrotate -d /etc/logrotate.conf 2>&1 | grep -iE "error|warn|no such"

# Force run to clear any failed state
logrotate -f /etc/logrotate.conf

# If logrotate.service shows as failed, reset after a clean run
systemctl reset-failed logrotate.service
```

**GOTCHA — journald-only hosts:** hv01 uses systemd-journald only (no
rsyslog/syslog daemon). Files like `/var/log/syslog`, `/var/log/auth.log`,
`/var/log/daemon.log` do not exist. Logrotate will error unless `missingok`
is set:

```bash
# Check which syslog daemon is running
systemctl is-active rsyslog syslog 2>/dev/null || echo "journald-only"

# Fix — add missingok to the relevant config
sed -i 's/^{$/{\n\tmissingok/' /etc/logrotate.d/system-logs
# Verify
head -5 /etc/logrotate.d/system-logs
```

---

## 3. Guest Audit Loop

Run on each VM/LXC via their Tailscale IP or via `pct exec`:

```bash
# For QEMU VMs — direct SSH
ssh -i ~/.ssh/vd-masterkey root@<tailscale-ip> "
  echo '=== HOSTNAME ===' && hostname
  echo '=== DISK ===' && df -h | grep -v tmpfs
  echo '=== MEMORY ===' && free -h
  echo '=== FAILED SERVICES ===' && systemctl --failed --no-pager
  echo '=== UPDATES ===' && apt list --upgradable 2>/dev/null | head -10
"

# For LXC containers — via pct exec on hv01
pct exec <vmid> -- bash -c "
  echo '=== HOSTNAME ===' && hostname
  echo '=== DISK ===' && df -h | grep -v tmpfs
  echo '=== FAILED SERVICES ===' && systemctl --failed --no-pager
"
```

---

## 4. Docker Audit (docker01 and ai01)

```bash
# Running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# PORT BINDING SECURITY — look for 0.0.0.0 bindings on dev/staging ports
docker ps --format "{{.Names}}: {{.Ports}}" | grep "0.0.0.0"
# Any staging/dev port bound to 0.0.0.0 bypasses UFW — must bind to 127.0.0.1
```

**GOTCHA — Docker bypasses UFW:** Docker directly modifies iptables,
bypassing UFW rules. A port bound to `0.0.0.0` is exposed to all interfaces
regardless of UFW `DENY` rules. Always bind internal/staging ports to
`127.0.0.1` in compose files.

```bash
# Fix in docker-compose (example: summarychrono staging)
# File: /opt/summarychrono/docker-compose.staging.yml
# Change: "5433:5432" → "127.0.0.1:5433:5432"
# Change: "6380:6379" → "127.0.0.1:6380:6379"
# Then recreate
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

```bash
# Image audit — flag any using 'latest' tag
docker ps --format "{{.Image}}" | grep ":latest"
docker images --format "{{.Repository}}:{{.Tag}}" | grep ":latest"

# Dangling volumes — inspect before deleting
docker volume ls -f dangling=true
# Inspect content before removing
docker run --rm -v <vol-name>:/data alpine ls -la /data/
docker volume rm <vol-name>  # only if confirmed empty/safe

# Dangling images
docker image prune -f

# Build cache
docker builder prune -f
```

**ops01 monitoring stack — image pinning:**

```bash
# File: /opt/monitoring/docker-compose.yml
# All images must be pinned — no 'latest'
# Current pinned versions (2026-06-05):
#   prom/prometheus:v3.4.0
#   grafana/grafana:11.6.1
#   grafana/loki:3.5.0
#   grafana/promtail:3.5.0
#   prom/node-exporter:v1.9.1

# OUTSTANDING: GF_SECURITY_ADMIN_PASSWORD=changeme — change default Grafana password
```

### Docker Cleanup Cron (ai01)

```bash
# Weekly cleanup — /etc/cron.d/docker-cleanup on ai01
cat /etc/cron.d/docker-cleanup
# Expected: 0 4 * * 6 root docker image prune -af && docker builder prune -f
```

---

## 5. rclone Bisync Audit (ai01)

```bash
ssh -i ~/.ssh/vd-masterkey root@100.118.164.120

# Check timer is active
systemctl status rclone-bisync.timer rclone-bisync.service

# Verify all 3 remote paths exist (must exist before first sync)
rclone lsd FilenRemote:/WebUI/
# Expected: Notes, Files, Skills directories
```

**GOTCHA — missing remote paths:** If the Filen remote directory doesn't
exist, bisync fails silently or errors. Fix:

```bash
rclone mkdir FilenRemote:/WebUI/Notes/
rclone mkdir FilenRemote:/WebUI/Files/
rclone mkdir FilenRemote:/WebUI/Skills/

# After creating, run --resync to initialise bidirectional state
rclone bisync /root/WebUI/Notes FilenRemote:/WebUI/Notes --resync --resilient
rclone bisync /root/WebUI/Files FilenRemote:/WebUI/Files --resync --resilient
rclone bisync /root/WebUI/Skills FilenRemote:/WebUI/Skills --resync --resilient

# Then start the timer
systemctl start rclone-bisync.timer
```

**GOTCHA — multiple ExecStart paths:** The service unit has 3 ExecStart
lines (one per path). ALL paths must have their remote initialized before
the timer first fires, or the service will fail.

---

## 6. Backup Schedule Verification

```bash
# On hv01 — list scheduled backup jobs
pvesh get /cluster/backup --output-format json-pretty | \
  jq '.[] | {vmid, schedule, storage, starttime, "keep-last": .["keep-last"]}'

# Check ai01 (VM 110) backup schedule — must not conflict with other VMs
# ai01 was moved to 01:00 (others run 02:00–05:00) to avoid QEMU agent timeout
# ai01 must have: --agent enabled=1,type=virtio
qm config 110 | grep agent
```

---

## 7. Post-Remediation Verification Checklist

After completing remediation actions, verify each item:

```bash
# ZFS pool capacity < 70%
zpool list data | awk 'NR>1 {print "CAP:", $5}'

# No failed systemd units on hv01
systemctl --failed --no-pager | grep -c "^0 loaded" && echo "CLEAN" || echo "HAS FAILURES"

# Backup count per VMID (should be ≤ 2)
ls /var/lib/vz/dump/vzdump-*.vma.zst 2>/dev/null | \
  sed 's/.*vzdump-[^-]*-\([0-9]*\)-.*/\1/' | sort | uniq -c

# Notification endpoint has recipient
pvesh get /cluster/notifications/endpoints/sendmail/mail-to-root | grep mailto

# Logrotate clean
logrotate -d /etc/logrotate.conf 2>&1 | grep -i error | head -5

# No 0.0.0.0 staging port bindings on docker01
ssh -i ~/.ssh/vd-masterkey root@100.125.96.56 \
  "docker ps --format '{{.Names}}: {{.Ports}}' | grep '0\.0\.0\.0'"

# Monitoring images pinned on ops01
ssh -i ~/.ssh/vd-masterkey root@100.90.175.111 \
  "grep 'image:' /opt/monitoring/docker-compose.yml"

# rclone bisync timer healthy on ai01
ssh -i ~/.ssh/vd-masterkey root@100.118.164.120 \
  "systemctl is-active rclone-bisync.timer"
```

---

## 8. Infra Node Quick Reference

| Node | Tailscale IP | Role | Key Services |
|------|-------------|------|--------------|
| hv01 | 100.118.114.56 | PVE 9.1.9 hypervisor | ZFS `data` pool, vzdump backups |
| proxy01 | 100.111.195.74 | CT 101 | Traefik v3 + Redis |
| web01 | 100.107.75.57 | CT 102 | Nginx + PHP-FPM |
| docker01 | 100.125.96.56 | CT 103 | Mailcow, BetterAuth, summarychrono |
| db01 | 100.109.96.107 | VM 104 | PostgreSQL 16 |
| ops01 | 100.90.175.111 | VM 107 | Prometheus, Grafana, Loki |
| ai01 | 100.118.164.120 | VM 110 | OpenWebUI, rclone bisync, Qdrant |

**SSH identity for all nodes:** `~/.ssh/vd-masterkey`
(always pass `-i ~/.ssh/vd-masterkey` — SSH config wildcard `Host 100.*` has no IdentityFile set)
