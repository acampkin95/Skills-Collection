# Server Infrastructure Guide

Ubuntu, Nginx, and PostgreSQL fundamentals for Next.js deployment. Covers installation, configuration, security, and best practices.

---

## Ubuntu Server Setup

### Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Set timezone
sudo timedatectl set-timezone Australia/Perth

# Create deploy user
sudo adduser deploy
sudo usermod -aG sudo deploy

# Setup SSH key authentication
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
# Add your public key to /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

### Security Hardening

```bash
# Disable root login and password auth
sudo nano /etc/ssh/sshd_config
# Set:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

sudo systemctl restart sshd

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### Install Node.js

```bash
# Using NodeSource (recommended)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Verify
node --version
npm --version

# Install PM2 globally
sudo npm install -g pm2
```

---

## Nginx Configuration

### Installation

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
```

### Basic Next.js Proxy Configuration

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name myapp.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name myapp.example.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/myapp.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.example.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/json application/xml;
    
    # Static files caching
    location /_next/static {
        proxy_pass http://localhost:3000;
        proxy_cache_valid 60m;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    
    location /static {
        proxy_pass http://localhost:3000;
        proxy_cache_valid 60m;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
    
    # Proxy to Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d myapp.example.com

# Auto-renewal (add to crontab)
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

### Load Balancing Multiple Instances

```nginx
upstream nextjs_backend {
    least_conn;
    server 127.0.0.1:3000 weight=1;
    server 127.0.0.1:3001 weight=1;
    server 127.0.0.1:3002 weight=1;
    keepalive 32;
}

server {
    # ... SSL config ...
    
    location / {
        proxy_pass http://nextjs_backend;
        # ... proxy settings ...
    }
}
```

---

## PostgreSQL Setup

### Installation

```bash
# Install PostgreSQL 16
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable postgresql

# Verify
psql --version
```

### Initial Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create application database and user
CREATE DATABASE myapp_production;
CREATE USER myapp_user WITH ENCRYPTED PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE myapp_production TO myapp_user;
ALTER DATABASE myapp_production OWNER TO myapp_user;

# Grant schema privileges
\c myapp_production
GRANT ALL ON SCHEMA public TO myapp_user;

\q
```

### PostgreSQL Configuration

```bash
# Edit main config
sudo nano /etc/postgresql/16/main/postgresql.conf
```

```ini
# /etc/postgresql/16/main/postgresql.conf

# Connections
listen_addresses = 'localhost'          # Or '*' for remote
max_connections = 100

# Memory (adjust based on available RAM)
shared_buffers = 256MB                  # 25% of RAM
effective_cache_size = 768MB            # 75% of RAM
maintenance_work_mem = 64MB
work_mem = 4MB

# Write Ahead Log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 1GB
min_wal_size = 80MB

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'ddl'                   # Log DDL statements
log_min_duration_statement = 1000       # Log slow queries (>1s)
```

### Client Authentication

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

```
# /etc/postgresql/16/main/pg_hba.conf

# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# Remote connections (if needed)
host    myapp_production    myapp_user    10.0.0.0/8            scram-sha-256
```

```bash
# Apply changes
sudo systemctl restart postgresql
```

### Connection String

```bash
# For Next.js .env
DATABASE_URL="postgresql://myapp_user:strong_password_here@localhost:5432/myapp_production?schema=public"
```

### Backup Configuration

```bash
# Create backup script
sudo nano /opt/scripts/backup-postgres.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE="myapp_production"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U postgres -Fc $DATABASE > "$BACKUP_DIR/${DATABASE}_${TIMESTAMP}.dump"

# Keep last 7 days
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete

# Optional: Upload to S3
# aws s3 cp "$BACKUP_DIR/${DATABASE}_${TIMESTAMP}.dump" s3://my-backups/postgres/
```

```bash
# Make executable and schedule
sudo chmod +x /opt/scripts/backup-postgres.sh
sudo crontab -e
# Add: 0 2 * * * /opt/scripts/backup-postgres.sh
```

---

## PM2 Process Management

### Ecosystem Configuration

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'myapp',
      script: 'node_modules/next/dist/bin/next',
      args: 'start',
      cwd: '/var/www/myapp',
      instances: 'max',           // Use all CPU cores
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      env_file: '/var/www/myapp/.env.production',
      error_file: '/var/log/pm2/myapp-error.log',
      out_file: '/var/log/pm2/myapp-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      max_memory_restart: '500M',
      restart_delay: 4000,
      wait_ready: true,
      listen_timeout: 10000,
    },
  ],
}
```

### PM2 Commands

```bash
# Start application
pm2 start ecosystem.config.js

# View status
pm2 status
pm2 monit

# View logs
pm2 logs myapp
pm2 logs myapp --lines 100

# Restart
pm2 restart myapp
pm2 reload myapp  # Zero-downtime reload

# Stop
pm2 stop myapp
pm2 delete myapp

# Save process list (persist across reboots)
pm2 save
pm2 startup  # Generate startup script
```

---

## Deployment Workflow

### Directory Structure

```
/var/www/myapp/
├── current/              # Symlink to current release
├── releases/
│   ├── 20240101120000/   # Release directories
│   └── 20240102120000/
├── shared/
│   ├── .env.production   # Shared env file
│   └── uploads/          # Persistent uploads
└── ecosystem.config.js
```

### Deploy Script

```bash
#!/bin/bash
# /opt/scripts/deploy.sh

set -e

APP_DIR="/var/www/myapp"
REPO_URL="git@github.com:user/myapp.git"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
RELEASE_DIR="$APP_DIR/releases/$TIMESTAMP"

echo "=== Starting deployment ==="

# Clone repository
git clone --depth 1 $REPO_URL $RELEASE_DIR

# Link shared files
ln -sf $APP_DIR/shared/.env.production $RELEASE_DIR/.env.production
ln -sf $APP_DIR/shared/uploads $RELEASE_DIR/public/uploads

# Install dependencies
cd $RELEASE_DIR
npm ci --production

# Build
npm run build

# Update symlink
ln -sfn $RELEASE_DIR $APP_DIR/current

# Reload PM2
pm2 reload myapp --update-env

# Cleanup old releases (keep last 5)
cd $APP_DIR/releases
ls -t | tail -n +6 | xargs -r rm -rf

echo "=== Deployment complete ==="
```

### Rollback Script

```bash
#!/bin/bash
# /opt/scripts/rollback.sh

APP_DIR="/var/www/myapp"
RELEASES_DIR="$APP_DIR/releases"

# Get previous release
PREVIOUS=$(ls -t $RELEASES_DIR | sed -n '2p')

if [ -z "$PREVIOUS" ]; then
    echo "No previous release found"
    exit 1
fi

echo "Rolling back to $PREVIOUS"

# Update symlink
ln -sfn "$RELEASES_DIR/$PREVIOUS" "$APP_DIR/current"

# Reload PM2
pm2 reload myapp --update-env

echo "Rollback complete"
```

---

## Monitoring

### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Disk usage
df -h

# Memory usage
free -h

# Process monitoring
htop

# Network monitoring
sudo nethogs
```

### PostgreSQL Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Index usage
SELECT relname, indexrelname, idx_scan, idx_tup_read
FROM pg_catalog.pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Log Monitoring

```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# PM2 logs
pm2 logs

# System logs
sudo journalctl -f
```

---

## Security Best Practices

### Regular Updates

```bash
# Schedule automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades
```

### PostgreSQL Security

```bash
# Restrict network access in pg_hba.conf
# Use strong passwords
# Regular backups with encryption

# Encrypt backups
pg_dump -U postgres myapp | gpg -c > backup.dump.gpg
```

### Application Security

```bash
# Environment variables
# - Never commit .env files
# - Use secrets manager for production
# - Rotate credentials regularly

# File permissions
chmod 600 .env.production
chown deploy:deploy .env.production
```

### Nginx Security Headers

```nginx
# Additional security headers
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Troubleshooting

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -50 /var/log/nginx/error.log

# Check if running
sudo systemctl status nginx

# Restart
sudo systemctl restart nginx
```

### PostgreSQL Issues

```bash
# Check status
sudo systemctl status postgresql

# Check logs
sudo tail -50 /var/log/postgresql/postgresql-16-main.log

# Connection test
psql -U myapp_user -d myapp_production -h localhost

# Check connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

### Application Issues

```bash
# Check PM2 status
pm2 status
pm2 logs myapp --err --lines 50

# Check if port is in use
sudo lsof -i :3000

# Check memory usage
pm2 monit

# Restart application
pm2 restart myapp
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 502 Bad Gateway | App not running | `pm2 restart myapp` |
| 504 Gateway Timeout | App too slow | Check DB queries, increase timeout |
| Connection refused | Wrong port/host | Check DATABASE_URL |
| Permission denied | File permissions | `chown -R deploy:deploy /var/www/myapp` |
| ENOSPC | Disk full | `df -h`, clean up old releases |
