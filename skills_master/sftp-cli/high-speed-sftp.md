# High-Speed SFTP Transfer Skill

Expert skill for optimized file transfers to/from Tailscale-connected servers using multi-stream SFTP, parallel rsync, and performance-tuned SSH connections.

## Server Configuration

**Primary Server:** `<prod-ip>` (prod-server via Tailscale)

### Optimizations Applied

#### SSH/SFTP Settings
- **MaxSessions:** 50 concurrent sessions
- **MaxStartups:** 50:30:100 (high connection limit)
- **ClientAliveInterval:** 60s (prevents timeouts)
- **Compression:** Enabled for better throughput
- **UseDNS:** Disabled for faster connections
- **SFTP Subsystem:** internal-sftp (optimized)

#### Security
- **Tailscale-only access:** UFW restricted to 100.64.0.0/10
- **No rate limiting:** SSH configured for maximum throughput
- **Connection keepalive:** Prevents drops during large transfers

#### Client-side Multiplexing
- **ControlMaster:** Reuses SSH connections
- **ControlPersist:** 10-minute connection pooling
- **ServerAliveInterval:** 60s keepalive

## Usage Patterns

### 1. Multi-Stream SFTP (Parallel Transfers)

**For multiple small files (fastest):**
```bash
# Use GNU Parallel with SFTP
find /path/to/files -type f | parallel -j 10 'scp -C {} root@<prod-ip>:/target/path/'

# Alternative: Use rsync with parallel
parallel -j 10 rsync -avz --progress ::: file1 file2 file3 root@<prod-ip>:/target/
```

### 2. Optimized rsync (Best for large files/directories)

**Single large file:**
```bash
# With compression and progress
rsync -avz --progress --partial /local/file root@<prod-ip>:/remote/path/

# Without compression (for already compressed files)
rsync -av --progress --no-compress /local/file.tar.gz root@<prod-ip>:/remote/

# With bandwidth limit (optional)
rsync -avz --progress --bwlimit=50M /local/file root@<prod-ip>:/remote/
```

**Directory sync with parallel:**
```bash
# Parallel rsync for directory tree (fastest for many files)
rsync -av --progress /source/ root@<prod-ip>:/dest/ \
  --rsync-path='rsync --partial-dir=.rsync-partial'

# With parallel file processing
find /source -type f -print0 | parallel -0 -j 10 \
  rsync -avz --relative --progress {} root@<prod-ip>:/dest/
```

### 3. SSH Connection Multiplexing

**Establish master connection once:**
```bash
# Start master connection (runs in background)
ssh -MNf root@<prod-ip>

# All subsequent commands reuse this connection (instant, no auth)
scp file1 root@<prod-ip>:/path/
scp file2 root@<prod-ip>:/path/
ssh root@<prod-ip> "ls -la /path"

# Close master connection when done
ssh -O exit root@<prod-ip>
```

### 4. Archive and Stream (Large deployments)

**Stream tar archive directly:**
```bash
# No local archive file needed - streams directly
tar czf - /source/directory | ssh root@<prod-ip> "tar xzf - -C /destination/"

# With progress using pv
tar czf - /source/directory | pv | ssh root@<prod-ip> "tar xzf - -C /dest/"

# Parallel compression (faster for large data)
tar cf - /source | pigz | pv | ssh root@<prod-ip> "pigz -d | tar xf - -C /dest/"
```

### 5. Split Large Files (Most reliable for huge files)

**For files >1GB:**
```bash
# Split into 100MB chunks
split -b 100M largefile.tar.gz largefile-part-

# Transfer chunks in parallel
parallel -j 5 scp -C {} root@<prod-ip>:/tmp/ ::: largefile-part-*

# Reassemble on server
ssh root@<prod-ip> "cat /tmp/largefile-part-* > /path/largefile.tar.gz && rm /tmp/largefile-part-*"
```

## Performance Monitoring

### Check Transfer Speed
```bash
# Use iperf3 over SSH to test max throughput
ssh root@<prod-ip> "iperf3 -s" &
iperf3 -c <prod-ip>

# Monitor active transfers
ssh root@<prod-ip> "watch -n 1 'ss -ti | grep ssh'"
```

### Health Check
```bash
# Run server-side health check
ssh root@<prod-ip> "/usr/local/bin/sftp-health-check"
```

### Monitor Connection Pool
```bash
# Check multiplexed connections
ls -la ~/.ssh/control-*

# Show active SSH sessions
ssh root@<prod-ip> "netstat -tn | grep :22"
```

## Deployment Workflows

### Next.js Standalone Build
```bash
# Method 1: Direct rsync (best for initial deploy)
rsync -avz --progress \
  --exclude='.git' --exclude='node_modules' \
  .next/standalone/ root@<prod-ip>:/opt/<project>/

# Method 2: Tar stream (best for updates)
tar czf - .next/standalone | \
  ssh root@<prod-ip> "tar xzf - -C /opt/<project>/"

# Method 3: Parallel chunks (best for large builds >500MB)
tar czf - .next/standalone | split -b 50M - standalone-part-
parallel -j 8 scp {} root@<prod-ip>:/tmp/ ::: standalone-part-*
ssh root@<prod-ip> "cat /tmp/standalone-part-* | tar xzf - -C /opt/<project>/ && rm /tmp/standalone-part-*"
```

### Database Backups
```bash
# Backup PostgreSQL directly to server
pg_dump -Fc <project> | ssh root@<prod-ip> "cat > /backup/<project>-$(date +%Y%m%d).dump"

# Restore from server
ssh root@<prod-ip> "cat /backup/latest.dump" | pg_restore -d <project>
```

## Troubleshooting

### Connection Timeouts
```bash
# Increase timeout values in ~/.ssh/config
Host <prod-ip>
    ServerAliveInterval 30
    ServerAliveCountMax 20
    TCPKeepAlive yes
```

### Slow Transfers
```bash
# Disable compression for already-compressed files
rsync -av --no-compress file.tar.gz root@<prod-ip>:/path/

# Use different cipher (faster but less secure - OK for Tailscale)
scp -c aes128-gcm@openssh.com file root@<prod-ip>:/path/
```

### Connection Drops
```bash
# Use screen/tmux for long transfers
screen -S transfer
rsync -avz --progress --partial /large/dir root@<prod-ip>:/dest/
# Detach: Ctrl-A, D
# Reattach: screen -r transfer
```

### Verify Transfer Integrity
```bash
# Generate checksums locally
find /source -type f -exec md5sum {} \; > /tmp/local-checksums.txt

# Upload and verify
scp /tmp/local-checksums.txt root@<prod-ip>:/tmp/
ssh root@<prod-ip> "cd /dest && md5sum -c /tmp/local-checksums.txt"
```

## Quick Reference

### Fast Commands for Common Tasks

```bash
# Transfer directory (medium size)
rsync -avz --progress /src/ root@<prod-ip>:/dest/

# Transfer large file (>1GB)
tar czf - /file | ssh root@<prod-ip> "tar xzf - -C /dest/"

# Transfer many small files
parallel -j 10 scp -C {} root@<prod-ip>:/dest/ ::: /src/*

# Transfer with resume capability
rsync -avz --partial --progress /src root@<prod-ip>:/dest/

# Check server health
ssh root@<prod-ip> /usr/local/bin/sftp-health-check

# Test connection speed
iperf3 -c <prod-ip>
```

## Configuration Files

### Server: `/etc/ssh/sshd_config.d/99-optimized-sftp.conf`
- 50 max sessions
- Compression enabled
- Connection keepalive
- Optimized for Tailscale

### Client: `~/.ssh/config`
```
Host <prod-ip>
    ServerAliveInterval 60
    ServerAliveCountMax 10
    Compression yes
    ControlMaster auto
    ControlPath ~/.ssh/control-%C
    ControlPersist 10m
    IPQoS throughput
```

## Security Notes

- SSH access restricted to Tailscale network (100.64.0.0/10)
- No public internet access to SSH
- All transfers encrypted via SSH
- Connection multiplexing prevents auth fatigue
- No rate limiting for maximum throughput

## Performance Expectations

- **Small files (<10MB):** ~50MB/s per stream
- **Large files (>100MB):** ~100-200MB/s with compression
- **Many files:** Linear scaling with parallel streams
- **Max concurrent connections:** 50 sessions
- **Connection establishment:** <100ms via multiplexing

## When to Use What

| Use Case | Recommended Method | Why |
|----------|-------------------|-----|
| Single large file (>1GB) | `tar \| ssh \| tar` | Stream, no disk I/O |
| Directory tree | `rsync -avz` | Delta sync, resume |
| Many small files | `parallel + scp` | Parallel streams |
| Resume interrupted | `rsync --partial` | Checkpointing |
| Unreliable network | Split + parallel | Chunk resilience |
| Already compressed | `rsync --no-compress` | No re-compression |

---

**Created:** 2026-01-19
**Server:** <prod-ip> (prod-server)
**Network:** Tailscale private network
**Status:** Active and optimized
