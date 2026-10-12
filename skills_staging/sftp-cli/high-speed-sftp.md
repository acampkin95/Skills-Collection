# High-Speed SFTP Transfer Skill

Expert skill for optimized file transfers to/from Tailscale-connected servers using multi-stream SFTP, parallel rsync, and performance-tuned SSH connections.

## Server Configuration

**Primary Server:** `100.100.42.6` (vmi02d via Tailscale)

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
find /path/to/files -type f | parallel -j 10 'scp -C {} root@100.100.42.6:/target/path/'

# Alternative: Use rsync with parallel
parallel -j 10 rsync -avz --progress ::: file1 file2 file3 root@100.100.42.6:/target/
```

### 2. Optimized rsync (Best for large files/directories)

**Single large file:**
```bash
# With compression and progress
rsync -avz --progress --partial /local/file root@100.100.42.6:/remote/path/

# Without compression (for already compressed files)
rsync -av --progress --no-compress /local/file.tar.gz root@100.100.42.6:/remote/

# With bandwidth limit (optional)
rsync -avz --progress --bwlimit=50M /local/file root@100.100.42.6:/remote/
```

**Directory sync with parallel:**
```bash
# Parallel rsync for directory tree (fastest for many files)
rsync -av --progress /source/ root@100.100.42.6:/dest/ \
  --rsync-path='rsync --partial-dir=.rsync-partial'

# With parallel file processing
find /source -type f -print0 | parallel -0 -j 10 \
  rsync -avz --relative --progress {} root@100.100.42.6:/dest/
```

### 3. SSH Connection Multiplexing

**Establish master connection once:**
```bash
# Start master connection (runs in background)
ssh -MNf root@100.100.42.6

# All subsequent commands reuse this connection (instant, no auth)
scp file1 root@100.100.42.6:/path/
scp file2 root@100.100.42.6:/path/
ssh root@100.100.42.6 "ls -la /path"

# Close master connection when done
ssh -O exit root@100.100.42.6
```

### 4. Archive and Stream (Large deployments)

**Stream tar archive directly:**
```bash
# No local archive file needed - streams directly
tar czf - /source/directory | ssh root@100.100.42.6 "tar xzf - -C /destination/"

# With progress using pv
tar czf - /source/directory | pv | ssh root@100.100.42.6 "tar xzf - -C /dest/"

# Parallel compression (faster for large data)
tar cf - /source | pigz | pv | ssh root@100.100.42.6 "pigz -d | tar xf - -C /dest/"
```

### 5. Split Large Files (Most reliable for huge files)

**For files >1GB:**
```bash
# Split into 100MB chunks
split -b 100M largefile.tar.gz largefile-part-

# Transfer chunks in parallel
parallel -j 5 scp -C {} root@100.100.42.6:/tmp/ ::: largefile-part-*

# Reassemble on server
ssh root@100.100.42.6 "cat /tmp/largefile-part-* > /path/largefile.tar.gz && rm /tmp/largefile-part-*"
```

## Performance Monitoring

### Check Transfer Speed
```bash
# Use iperf3 over SSH to test max throughput
ssh root@100.100.42.6 "iperf3 -s" &
iperf3 -c 100.100.42.6

# Monitor active transfers
ssh root@100.100.42.6 "watch -n 1 'ss -ti | grep ssh'"
```

### Health Check
```bash
# Run server-side health check
ssh root@100.100.42.6 "/usr/local/bin/sftp-health-check"
```

### Monitor Connection Pool
```bash
# Check multiplexed connections
ls -la ~/.ssh/control-*

# Show active SSH sessions
ssh root@100.100.42.6 "netstat -tn | grep :22"
```

## Deployment Workflows

### Next.js Standalone Build
```bash
# Method 1: Direct rsync (best for initial deploy)
rsync -avz --progress \
  --exclude='.git' --exclude='node_modules' \
  .next/standalone/ root@100.100.42.6:/opt/wattlewool/

# Method 2: Tar stream (best for updates)
tar czf - .next/standalone | \
  ssh root@100.100.42.6 "tar xzf - -C /opt/wattlewool/"

# Method 3: Parallel chunks (best for large builds >500MB)
tar czf - .next/standalone | split -b 50M - standalone-part-
parallel -j 8 scp {} root@100.100.42.6:/tmp/ ::: standalone-part-*
ssh root@100.100.42.6 "cat /tmp/standalone-part-* | tar xzf - -C /opt/wattlewool/ && rm /tmp/standalone-part-*"
```

### Database Backups
```bash
# Backup PostgreSQL directly to server
pg_dump -Fc wattlewool | ssh root@100.100.42.6 "cat > /backup/wattlewool-$(date +%Y%m%d).dump"

# Restore from server
ssh root@100.100.42.6 "cat /backup/latest.dump" | pg_restore -d wattlewool
```

## Troubleshooting

### Connection Timeouts
```bash
# Increase timeout values in ~/.ssh/config
Host 100.100.42.6
    ServerAliveInterval 30
    ServerAliveCountMax 20
    TCPKeepAlive yes
```

### Slow Transfers
```bash
# Disable compression for already-compressed files
rsync -av --no-compress file.tar.gz root@100.100.42.6:/path/

# Use different cipher (faster but less secure - OK for Tailscale)
scp -c aes128-gcm@openssh.com file root@100.100.42.6:/path/
```

### Connection Drops
```bash
# Use screen/tmux for long transfers
screen -S transfer
rsync -avz --progress --partial /large/dir root@100.100.42.6:/dest/
# Detach: Ctrl-A, D
# Reattach: screen -r transfer
```

### Verify Transfer Integrity
```bash
# Generate checksums locally
find /source -type f -exec md5sum {} \; > /tmp/local-checksums.txt

# Upload and verify
scp /tmp/local-checksums.txt root@100.100.42.6:/tmp/
ssh root@100.100.42.6 "cd /dest && md5sum -c /tmp/local-checksums.txt"
```

## Quick Reference

### Fast Commands for Common Tasks

```bash
# Transfer directory (medium size)
rsync -avz --progress /src/ root@100.100.42.6:/dest/

# Transfer large file (>1GB)
tar czf - /file | ssh root@100.100.42.6 "tar xzf - -C /dest/"

# Transfer many small files
parallel -j 10 scp -C {} root@100.100.42.6:/dest/ ::: /src/*

# Transfer with resume capability
rsync -avz --partial --progress /src root@100.100.42.6:/dest/

# Check server health
ssh root@100.100.42.6 /usr/local/bin/sftp-health-check

# Test connection speed
iperf3 -c 100.100.42.6
```

## Configuration Files

### Server: `/etc/ssh/sshd_config.d/99-optimized-sftp.conf`
- 50 max sessions
- Compression enabled
- Connection keepalive
- Optimized for Tailscale

### Client: `~/.ssh/config`
```
Host 100.100.42.6
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
**Server:** 100.100.42.6 (vmi02d)
**Network:** Tailscale private network
**Status:** Active and optimized
