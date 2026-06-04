# SFTP Skill

High-speed SFTP transfer utilities and deployment automation for Tailscale-connected servers.

## Quick Start

1. Read `high-speed-sftp.md` for transfer optimization techniques
2. Review `sftp-quick-reference.md` for common commands
3. Use deployment scripts for automated workflows

## Files

| File | Purpose |
|------|---------|
| `high-speed-sftp.md` | Comprehensive guide to optimized SFTP transfers |
| `sftp-quick-reference.md` | Quick command reference and patterns |
| `sftp-deploy.sh` | Main deployment automation script |
| `sftp-deploy-wrapper.sh` | Wrapper for deploy script execution |
| `sftp-deploy-hooks.sh` | Pre/post deployment hooks |
| `sftp-monitor.sh` | Transfer monitoring and logging |

## Key Features

- **Multi-stream transfers**: Parallel SFTP connections for speed
- **Optimized rsync**: Best practices for large file transfers
- **SSH multiplexing**: Connection pooling to reduce overhead
- **Tailscale integration**: Secure transfers over Tailscale mesh network
- **Deployment automation**: Scripts for repeatable deployments
- **Transfer monitoring**: Progress tracking and logging

## Installation

```bash
# Make scripts executable
chmod +x sftp-deploy.sh sftp-deploy-wrapper.sh sftp-deploy-hooks.sh sftp-monitor.sh

# Configure your target server
export SFTP_HOST="100.100.42.6"
export SFTP_USER="root"
```

## Common Tasks

### Upload files with optimization
```bash
./sftp-deploy.sh --source /local/path --target /remote/path
```

### Monitor active transfers
```bash
./sftp-monitor.sh
```

See individual files for detailed usage instructions.
