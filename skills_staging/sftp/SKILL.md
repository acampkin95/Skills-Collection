---
name: sftp
description: High-speed SFTP/rsync file transfer and deployment automation for Tailscale-connected ACDev infrastructure (vmi02d, node01, node02). Use this skill when sftp, rsync transfer, deploy files, upload to server, scp files, file deployment, remote file copy, Tailscale transfer, vmi02d upload, parallel transfer, sftp-deploy.sh, deploy Next.js build, transfer optimization, multi-stream sftp, ssh multiplexing. Use this skill when deploying builds to production servers, bulk file transfers over Tailscale, automated deployment scripts.
---

# SFTP Deployment Skill

High-speed file transfer and deployment automation for ACDev Tailscale infrastructure.

---

## Server Aliases

| Alias | IP | Purpose |
|-------|-----|---------|
| `vmi02d` | 100.100.42.6 | Production server |
| `node01` | 100.118.170.115 | Swarm node 1 |
| `node02` | 100.86.129.15 | Swarm node 2 |

---

## Quick Deploy Patterns

### Next.js Build — Small Update (<100MB)
```bash
rsync -avz --delete .next/standalone/ vmi02d:/opt/<project>/
ssh vmi02d "pm2 restart <project>"
```

### Next.js Build — Large Update (>100MB)
```bash
tar czf - .next/standalone | ssh vmi02d "tar xzf - -C /opt/<project>/"
ssh vmi02d "pm2 restart <project>"
```

### Parallel Transfer — Huge Update (>500MB)
```bash
tar czf - .next/standalone | split -b 50M - /tmp/deploy-
parallel -j 8 scp {} vmi02d:/tmp/ ::: /tmp/deploy-*
ssh vmi02d "cat /tmp/deploy-* | tar xzf - -C /opt/<project>/ && rm /tmp/deploy-*"
ssh vmi02d "pm2 restart <project>"
```

### Single File / Resumable
```bash
scp file.txt vmi02d:/path/to/destination/
rsync -avz --partial --progress large-file.tar.gz vmi02d:/destination/
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
export SFTP_HOST="100.100.42.6"
export SFTP_USER="root"
```

---

## Transfer Optimization

### SSH Config for Multiplexing (~/.ssh/config)
```
Host vmi02d
  HostName 100.100.42.6
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
rsync -avz --no-compress --delete src/ vmi02d:/dest/

# Exclude build artifacts
rsync -avz --exclude='.git' --exclude='node_modules' src/ vmi02d:/dest/

# Dry run first
rsync -avzn src/ vmi02d:/dest/
```

---

## Reference Files

| File | Purpose |
|------|---------|
| `high-speed-sftp.md` | Comprehensive transfer optimization techniques |
| `sftp-quick-reference.md` | Full command reference and patterns |
