# SFTP Quick Reference Card

Ultra-fast file transfer commands for Tailscale network.

## Server Aliases
```bash
prod-server        # <prod-ip> - Production server
swarm-node-1        # <swarm-node-1-ip> - Swarm node 1
swarm-node-2        # <swarm-node-2-ip> - Swarm node 2
```

## Common Commands

### Deploy Next.js Build (Fastest Methods)

**Small update (<100MB):**
```bash
rsync -avz --delete .next/standalone/ prod-server:/opt/<project>/
ssh prod-server "pm2 restart <project>"
```

**Large update (>100MB):**
```bash
tar czf - .next/standalone | ssh prod-server "tar xzf - -C /opt/<project>/"
ssh prod-server "pm2 restart <project>"
```

**Huge update (>500MB) - Parallel:**
```bash
tar czf - .next/standalone | split -b 50M - /tmp/deploy-
parallel -j 8 scp {} prod-server:/tmp/ ::: /tmp/deploy-*
ssh prod-server "cat /tmp/deploy-* | tar xzf - -C /opt/<project>/ && rm /tmp/deploy-*"
ssh prod-server "pm2 restart <project>"
```

### Single File Transfers

**Quick copy:**
```bash
scp file.txt prod-server:/path/to/destination/
```

**With progress:**
```bash
rsync -avz --progress file.tar.gz prod-server:/destination/
```

**Resume interrupted:**
```bash
rsync -avz --partial --progress file.tar.gz prod-server:/destination/
```

### Directory Sync

**Sync directory (delta only):**
```bash
rsync -avz --delete src/ prod-server:/dest/
```

**Initial large sync:**
```bash
rsync -avz --progress --stats src/ prod-server:/dest/
```

**Many small files (parallel):**
```bash
parallel -j 10 rsync -avz {} prod-server:/dest/ ::: src/*
```

### Archive Streaming (No Local Copy)

**Compress and stream:**
```bash
tar czf - directory/ | ssh prod-server "tar xzf - -C /destination/"
```

**With progress:**
```bash
tar czf - directory/ | pv | ssh prod-server "tar xzf - -C /dest/"
```

**Parallel compression:**
```bash
tar cf - directory/ | pigz -p 4 | ssh prod-server "pigz -d | tar xf - -C /dest/"
```

## Performance Tips

### Speed Up Connections
```bash
# Establish persistent connection (once)
ssh -MNf prod-server

# All future commands instant (reuses connection)
scp file1 prod-server:/path/
scp file2 prod-server:/path/
ssh prod-server "ls -la"

# Close when done
ssh -O exit prod-server
```

### Large File Strategy
```bash
# Split large file
split -b 100M largefile.tar.gz part-

# Upload in parallel
parallel -j 8 scp {} prod-server:/tmp/ ::: part-*

# Reassemble on server
ssh prod-server "cat /tmp/part-* > /path/largefile.tar.gz && rm /tmp/part-*"
```

### Already Compressed Files
```bash
# Skip compression for .tar.gz, .zip, etc
rsync -av --no-compress file.tar.gz prod-server:/path/
```

## Health Checks

**Server SFTP status:**
```bash
ssh prod-server /usr/local/bin/sftp-health-check
```

**Active connections:**
```bash
ssh prod-server "ss -tn state established '( dport = :22 or sport = :22 )'"
```

**Test bandwidth:**
```bash
# Terminal 1:
ssh prod-server "iperf3 -s"

# Terminal 2:
iperf3 -c prod-server
```

## Emergency Recovery

**Resume broken transfer:**
```bash
rsync -avz --partial --append-verify /src prod-server:/dest
```

**Verify transferred files:**
```bash
# Generate checksums
find /src -type f -exec md5sum {} \; > checksums.txt

# Upload and verify
scp checksums.txt prod-server:/tmp/
ssh prod-server "cd /dest && md5sum -c /tmp/checksums.txt"
```

**Long transfer in background:**
```bash
# Start in screen
screen -S upload
rsync -avz --progress /large/dir prod-server:/dest/
# Detach: Ctrl-A, D

# Check progress later
screen -r upload
```

## One-Liners

```bash
# Deploy and restart
rsync -avz .next/standalone/ prod-server:/opt/<project>/ && ssh prod-server pm2 restart <project>

# Backup remote to local
ssh prod-server "tar czf - /important/data" > backup-$(date +%Y%m%d).tar.gz

# Copy between servers
ssh swarm-node-1 "tar czf - /data" | ssh prod-server "tar xzf - -C /backup"

# Upload multiple files
parallel scp {} prod-server:/dest/ ::: *.log

# Sync with exclusions
rsync -avz --exclude='*.log' --exclude='node_modules' src/ prod-server:/dest/
```

## Configuration Locations

- **Skill docs:** `~/.claude/skills/high-speed-sftp.md`
- **SSH config:** `~/.ssh/config`
- **Server config:** `/etc/ssh/sshd_config.d/99-optimized-sftp.conf`
- **Health check:** `/usr/local/bin/sftp-health-check`

## Performance Specs

- **Max sessions:** 50 concurrent
- **Keepalive:** 60s interval, 10 retries
- **Compression:** Enabled (gzip)
- **Connection reuse:** 10 minute persistence
- **Bandwidth:** Unlimited (no rate limiting)
- **Network:** Tailscale-only (100.64.0.0/10)

---
Quick reference for high-speed SFTP operations. See full docs: `~/.claude/skills/high-speed-sftp.md`
