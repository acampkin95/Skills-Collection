---
name: sftp-cli
description: "Transfers and deploys files to remote servers over SFTP and rsync with parallel and resumable transfers, SSH multiplexing, and bundled deployment scripts. Use when copying or deploying a build to a server with rsync, scp or sftp, speeding up a large transfer, resuming an interrupted upload, or running the sftp-deploy scripts."
metadata:
  interface: "cli"
version: "1.0.0"
reviewed: "2026-10-12"
---

# SFTP Deployment Skill

High-speed file transfer and deployment automation for your Tailscale infrastructure.

---

## Server Aliases

| Alias | IP | Purpose |
|-------|-----|---------|
| `prod-server` | <prod-ip> | Production server |
| `swarm-node-1` | <swarm-node-1-ip> | Swarm node 1 |
| `swarm-node-2` | <swarm-node-2-ip> | Swarm node 2 |

---

## Quick Deploy Patterns

### Next.js Build — Small Update (<100MB)
```bash
rsync -avz --delete .next/standalone/ prod-server:/opt/<project>/
ssh prod-server "pm2 restart <project>"
```

### Next.js Build — Large Update (>100MB)
```bash
tar czf - .next/standalone | ssh prod-server "tar xzf - -C /opt/<project>/"
ssh prod-server "pm2 restart <project>"
```

### Parallel Transfer — Huge Update (>500MB)
```bash
tar czf - .next/standalone | split -b 50M - /tmp/deploy-
parallel -j 8 scp {} prod-server:/tmp/ ::: /tmp/deploy-*
ssh prod-server "cat /tmp/deploy-* | tar xzf - -C /opt/<project>/ && rm /tmp/deploy-*"
ssh prod-server "pm2 restart <project>"
```

### Single File / Resumable
```bash
scp file.txt prod-server:/path/to/destination/
rsync -avz --partial --progress large-file.tar.gz prod-server:/destination/
```

---

## Deployment Scripts

Located in this skill folder — make executable first:
```bash
chmod +x sftp-deploy.sh sftp-deploy-wrapper.sh sftp-deploy-hooks.sh sftp-monitor.sh
```

| Script | Purpose |
|--------|---------|
| `sftp-deploy.sh` | Main deployment automation |
| `sftp-deploy-wrapper.sh` | Wrapper for deploy execution |
| `sftp-deploy-hooks.sh` | Pre/post deployment hooks |
| `sftp-monitor.sh` | Transfer monitoring and logging |

### Usage
```bash
./sftp-deploy.sh --source /local/path --target /remote/path
./sftp-monitor.sh
```

### Environment Variables
```bash
export SFTP_HOST="<prod-ip>"
export SFTP_USER="root"
# Optional overrides used by the bundled scripts (defaults are placeholders)
export SFTP_SERVER="prod-server"          # SSH alias for sftp-deploy.sh
export SFTP_REMOTE_PATH="/opt/your-project"
export SFTP_PROJECT="your-project"        # PM2 app name and directory name
export SFTP_REMOTE_HOST="prod-server"     # SSH alias used by the hooks and monitor
export SFTP_HEALTH_URL="http://<prod-ip>/"
```

---

## Transfer Optimization

### SSH Config for Multiplexing (~/.ssh/config)
```
Host prod-server
  HostName <prod-ip>
  User root
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
  Compression yes
  Cipher aes128-ctr
```

### rsync Best Practices
```bash
# Fast: no compression (Tailscale already encrypted)
rsync -avz --no-compress --delete src/ prod-server:/dest/

# Exclude build artifacts
rsync -avz --exclude='.git' --exclude='node_modules' src/ prod-server:/dest/

# Dry run first
rsync -avzn src/ prod-server:/dest/
```

---

## Reference Files

| File | Purpose |
|------|---------|
| `high-speed-sftp.md` | Comprehensive transfer optimization techniques |
| `sftp-quick-reference.md` | Full command reference and patterns |
