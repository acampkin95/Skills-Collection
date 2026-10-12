# SFTP Quick Reference Card

Ultra-fast file transfer commands for Tailscale network.

## Server Aliases
```bash
vmi02d        # 100.100.42.6 - Production server
node01        # 100.118.170.115 - Swarm node 1
node02        # 100.86.129.15 - Swarm node 2
```

## Common Commands

### Deploy Next.js Build (Fastest Methods)

**Small update (<100MB):**
```bash
rsync -avz --delete .next/standalone/ vmi02d:/opt/wattlewool/
ssh vmi02d "pm2 restart wattlewool"
```

**Large update (>100MB):**
```bash
tar czf - .next/standalone | ssh vmi02d "tar xzf - -C /opt/wattlewool/"
ssh vmi02d "pm2 restart wattlewool"
```

**Huge update (>500MB) - Parallel:**
```bash
tar czf - .next/standalone | split -b 50M - /tmp/deploy-
parallel -j 8 scp {} vmi02d:/tmp/ ::: /tmp/deploy-*
ssh vmi02d "cat /tmp/deploy-* | tar xzf - -C /opt/wattlewool/ && rm /tmp/deploy-*"
ssh vmi02d "pm2 restart wattlewool"
```

### Single File Transfers

**Quick copy:**
```bash
scp file.txt vmi02d:/path/to/destination/
```

**With progress:**
```bash
rsync -avz --progress file.tar.gz vmi02d:/destination/
```

**Resume interrupted:**
```bash
rsync -avz --partial --progress file.tar.gz vmi02d:/destination/
```

### Directory Sync

**Sync directory (delta only):**
```bash
rsync -avz --delete src/ vmi02d:/dest/
```

**Initial large sync:**
```bash
rsync -avz --progress --stats src/ vmi02d:/dest/
```

**Many small files (parallel):**
```bash
parallel -j 10 rsync -avz {} vmi02d:/dest/ ::: src/*
```

### Archive Streaming (No Local Copy)

**Compress and stream:**
```bash
tar czf - directory/ | ssh vmi02d "tar xzf - -C /destination/"
```

**With progress:**
```bash
tar czf - directory/ | pv | ssh vmi02d "tar xzf - -C /dest/"
```

**Parallel compression:**
```bash
tar cf - directory/ | pigz -p 4 | ssh vmi02d "pigz -d | tar xf - -C /dest/"
```

## Performance Tips

### Speed Up Connections
```bash
# Establish persistent connection (once)
ssh -MNf vmi02d

# All future commands instant (reuses connection)
scp file1 vmi02d:/path/
scp file2 vmi02d:/path/
ssh vmi02d "ls -la"

# Close when done
ssh -O exit vmi02d
```

### Large File Strategy
```bash
# Split large file
split -b 100M largefile.tar.gz part-

# Upload in parallel
parallel -j 8 scp {} vmi02d:/tmp/ ::: part-*

# Reassemble on server
ssh vmi02d "cat /tmp/part-* > /path/largefile.tar.gz && rm /tmp/part-*"
```

### Already Compressed Files
```bash
# Skip compression for .tar.gz, .zip, etc
rsync -av --no-compress file.tar.gz vmi02d:/path/
```

## Health Checks

**Server SFTP status:**
```bash
ssh vmi02d /usr/local/bin/sftp-health-check
```

**Active connections:**
```bash
ssh vmi02d "ss -tn state established '( dport = :22 or sport = :22 )'"
```

**Test bandwidth:**
```bash
# Terminal 1:
ssh vmi02d "iperf3 -s"

# Terminal 2:
iperf3 -c vmi02d
```

## Emergency Recovery

**Resume broken transfer:**
```bash
rsync -avz --partial --append-verify /src vmi02d:/dest
```

**Verify transferred files:**
```bash
# Generate checksums
find /src -type f -exec md5sum {} \; > checksums.txt

# Upload and verify
scp checksums.txt vmi02d:/tmp/
ssh vmi02d "cd /dest && md5sum -c /tmp/checksums.txt"
```

**Long transfer in background:**
```bash
# Start in screen
screen -S upload
rsync -avz --progress /large/dir vmi02d:/dest/
# Detach: Ctrl-A, D

# Check progress later
screen -r upload
```

## One-Liners

```bash
# Deploy and restart
rsync -avz .next/standalone/ vmi02d:/opt/wattlewool/ && ssh vmi02d pm2 restart wattlewool

# Backup remote to local
ssh vmi02d "tar czf - /important/data" > backup-$(date +%Y%m%d).tar.gz

# Copy between servers
ssh node01 "tar czf - /data" | ssh vmi02d "tar xzf - -C /backup"

# Upload multiple files
parallel scp {} vmi02d:/dest/ ::: *.log

# Sync with exclusions
rsync -avz --exclude='*.log' --exclude='node_modules' src/ vmi02d:/dest/
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
