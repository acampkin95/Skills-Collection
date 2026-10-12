#!/bin/bash
###############################################################################
# High-Speed SFTP Deployment Script
# Optimized deployment with parallel transfers, health checks, and rollback
#
# Usage: ./sftp-deploy.sh [options]
#
# Options:
#   -m, --method <rsync|tar|parallel>  Deployment method (default: auto)
#   -s, --server <alias>                Server alias (default: vmi02d)
#   -p, --path <path>                   Remote path (default: /opt/wattlewool)
#   -b, --build                         Run build before deploy
#   -r, --restart <service>             Restart service after deploy
#   -c, --check                         Run health check after deploy
#   -d, --dry-run                       Show what would be done
#   -v, --verbose                       Verbose output
#   -h, --help                          Show this help
#
# Examples:
#   ./sftp-deploy.sh --build --restart wattlewool --check
#   ./sftp-deploy.sh --method parallel --server vmi02d
#   ./sftp-deploy.sh --dry-run --verbose
#
###############################################################################

set -o pipefail  # Fail on pipe errors

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
SERVER="vmi02d"
REMOTE_PATH="/opt/wattlewool"
LOCAL_PATH=".next/standalone"
DEPLOY_METHOD="auto"
RUN_BUILD=false
RESTART_SERVICE=""
RUN_HEALTH_CHECK=false
DRY_RUN=false
VERBOSE=false
BACKUP_ENABLED=true
PARALLEL_JOBS=8
CHUNK_SIZE="50M"

# Deployment metadata
DEPLOY_ID="deploy-$(date +%Y%m%d-%H%M%S)"
DEPLOY_LOG="/tmp/${DEPLOY_ID}.log"
BACKUP_PATH="${REMOTE_PATH}.backup-${DEPLOY_ID}"

###############################################################################
# Helper Functions
###############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)  echo -e "${BLUE}[INFO]${NC} $message" | tee -a "$DEPLOY_LOG" ;;
        SUCCESS) echo -e "${GREEN}[✓]${NC} $message" | tee -a "$DEPLOY_LOG" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $message" | tee -a "$DEPLOY_LOG" ;;
        ERROR) echo -e "${RED}[✗]${NC} $message" | tee -a "$DEPLOY_LOG" ;;
        DEBUG) [[ $VERBOSE == true ]] && echo -e "${CYAN}[DEBUG]${NC} $message" | tee -a "$DEPLOY_LOG" ;;
    esac

    # Always log to file with timestamp
    echo "[$timestamp] [$level] $message" >> "$DEPLOY_LOG"
}

show_help() {
    sed -n '2,/^$/p' "$0" | sed 's/^# //'
    exit 0
}

check_dependencies() {
    log INFO "Checking dependencies..."
    local missing_deps=()

    for cmd in ssh scp rsync tar parallel pv; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log ERROR "Missing dependencies: ${missing_deps[*]}"
        log INFO "Install with: brew install ${missing_deps[*]}"
        return 1
    fi

    log SUCCESS "All dependencies available"
    return 0
}

check_ssh_connection() {
    log INFO "Testing SSH connection to $SERVER..."

    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$SERVER" "echo 'Connection test'" &>/dev/null; then
        log ERROR "Cannot connect to $SERVER"
        log INFO "Try: ssh $SERVER"
        return 1
    fi

    log SUCCESS "SSH connection OK"
    return 0
}

check_disk_space() {
    log INFO "Checking remote disk space..."

    local usage=$(ssh "$SERVER" "df -h $REMOTE_PATH | tail -1 | awk '{print \$5}' | sed 's/%//'")
    log DEBUG "Disk usage: ${usage}%"

    if [ "$usage" -gt 90 ]; then
        log WARN "Disk space critical: ${usage}% used"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && return 1
    elif [ "$usage" -gt 80 ]; then
        log WARN "Disk space low: ${usage}% used"
    else
        log SUCCESS "Disk space OK: ${usage}% used"
    fi

    return 0
}

check_build_exists() {
    if [ ! -d "$LOCAL_PATH" ]; then
        log ERROR "Build directory not found: $LOCAL_PATH"
        log INFO "Run build with: npm run build"
        return 1
    fi

    local build_size=$(du -sh "$LOCAL_PATH" | cut -f1)
    log SUCCESS "Build found: $build_size"
    return 0
}

run_build() {
    log INFO "Running build..."

    if [ ! -f "package.json" ]; then
        log ERROR "package.json not found. Not in project root?"
        return 1
    fi

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would run: npm run build"
        return 0
    fi

    if npm run build 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "Build completed"
        return 0
    else
        log ERROR "Build failed"
        return 1
    fi
}

create_backup() {
    if ! $BACKUP_ENABLED; then
        log INFO "Backup disabled"
        return 0
    fi

    log INFO "Creating backup..."

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would create backup: $BACKUP_PATH"
        return 0
    fi

    # Check if remote path exists
    if ! ssh "$SERVER" "[ -d $REMOTE_PATH ]" 2>/dev/null; then
        log WARN "Remote path doesn't exist, skipping backup"
        return 0
    fi

    # Create backup
    if ssh "$SERVER" "cp -al $REMOTE_PATH $BACKUP_PATH" 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "Backup created: $BACKUP_PATH"

        # Cleanup old backups (keep last 5)
        ssh "$SERVER" "ls -dt ${REMOTE_PATH}.backup-* 2>/dev/null | tail -n +6 | xargs rm -rf" 2>/dev/null || true
        return 0
    else
        log ERROR "Backup failed"
        return 1
    fi
}

detect_deploy_method() {
    local size=$(du -sm "$LOCAL_PATH" | cut -f1)
    log DEBUG "Build size: ${size}MB"

    if [ "$size" -lt 100 ]; then
        echo "rsync"
    elif [ "$size" -lt 500 ]; then
        echo "tar"
    else
        echo "parallel"
    fi
}

deploy_rsync() {
    log INFO "Deploying with rsync (delta sync)..."

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would run: rsync -avz --delete $LOCAL_PATH/ $SERVER:$REMOTE_PATH/"
        return 0
    fi

    # Establish multiplexed connection
    ssh -MNf "$SERVER" 2>/dev/null || true

    local rsync_opts=(
        -avz
        --delete
        --progress
        --stats
        --human-readable
        --partial
        --partial-dir=.rsync-partial
        --compress-level=6
    )

    if $VERBOSE; then
        rsync_opts+=(--verbose)
    else
        rsync_opts+=(--quiet)
    fi

    if rsync "${rsync_opts[@]}" "$LOCAL_PATH/" "$SERVER:$REMOTE_PATH/" 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "Rsync deployment completed"
        return 0
    else
        log ERROR "Rsync deployment failed"
        return 1
    fi
}

deploy_tar() {
    log INFO "Deploying with tar stream..."

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would stream tar to $SERVER:$REMOTE_PATH/"
        return 0
    fi

    # Establish multiplexed connection
    ssh -MNf "$SERVER" 2>/dev/null || true

    # Check if pv is available for progress
    if command -v pv &> /dev/null && $VERBOSE; then
        local tar_size=$(du -sb "$LOCAL_PATH" | cut -f1)
        if tar czf - "$LOCAL_PATH" 2>/dev/null | pv -s "$tar_size" | \
           ssh "$SERVER" "tar xzf - -C $REMOTE_PATH --strip-components=1" 2>&1 | tee -a "$DEPLOY_LOG"; then
            log SUCCESS "Tar stream deployment completed"
            return 0
        fi
    else
        if tar czf - "$LOCAL_PATH" 2>/dev/null | \
           ssh "$SERVER" "tar xzf - -C $REMOTE_PATH --strip-components=1" 2>&1 | tee -a "$DEPLOY_LOG"; then
            log SUCCESS "Tar stream deployment completed"
            return 0
        fi
    fi

    log ERROR "Tar stream deployment failed"
    return 1
}

deploy_parallel() {
    log INFO "Deploying with parallel chunks (fastest for large builds)..."

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would deploy in parallel chunks"
        return 0
    fi

    # Create temporary directory for chunks
    local temp_dir="/tmp/${DEPLOY_ID}"
    mkdir -p "$temp_dir"

    log INFO "Creating compressed archive..."
    tar czf - "$LOCAL_PATH" 2>/dev/null | split -b "$CHUNK_SIZE" - "${temp_dir}/chunk-"

    local chunk_count=$(ls -1 "${temp_dir}"/chunk-* | wc -l)
    log INFO "Split into $chunk_count chunks of $CHUNK_SIZE each"

    log INFO "Uploading chunks in parallel ($PARALLEL_JOBS jobs)..."
    if ls "${temp_dir}"/chunk-* | parallel -j "$PARALLEL_JOBS" --bar scp {} "$SERVER:/tmp/" 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "All chunks uploaded"
    else
        log ERROR "Chunk upload failed"
        rm -rf "$temp_dir"
        return 1
    fi

    log INFO "Reassembling and extracting on server..."
    if ssh "$SERVER" "cat /tmp/chunk-* | tar xzf - -C $REMOTE_PATH --strip-components=1 && rm /tmp/chunk-*" 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "Parallel deployment completed"
        rm -rf "$temp_dir"
        return 0
    else
        log ERROR "Server extraction failed"
        rm -rf "$temp_dir"
        return 1
    fi
}

restart_service() {
    if [ -z "$RESTART_SERVICE" ]; then
        return 0
    fi

    log INFO "Restarting service: $RESTART_SERVICE..."

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would restart: pm2 restart $RESTART_SERVICE"
        return 0
    fi

    if ssh "$SERVER" "pm2 restart $RESTART_SERVICE" 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "Service restarted: $RESTART_SERVICE"
        sleep 3  # Give service time to start
        return 0
    else
        log ERROR "Service restart failed: $RESTART_SERVICE"
        return 1
    fi
}

run_health_check() {
    if ! $RUN_HEALTH_CHECK; then
        return 0
    fi

    log INFO "Running health checks..."

    # Check if service is running
    if [ -n "$RESTART_SERVICE" ]; then
        if ssh "$SERVER" "pm2 describe $RESTART_SERVICE | grep -q 'status.*online'" 2>/dev/null; then
            log SUCCESS "Service is online: $RESTART_SERVICE"
        else
            log ERROR "Service is not online: $RESTART_SERVICE"
            return 1
        fi
    fi

    # Check HTTP endpoint
    if [ "$SERVER" == "vmi02d" ]; then
        local url="http://100.100.42.6/"
        log INFO "Checking HTTP endpoint: $url"

        if curl -s -f -m 10 "$url" | grep -q "Demo"; then
            log SUCCESS "HTTP check passed"
        else
            log WARN "HTTP check failed (may be expected)"
        fi
    fi

    # Check SFTP health
    if ssh "$SERVER" "/usr/local/bin/sftp-health-check 2>/dev/null | grep -q 'SSH daemon is running'"; then
        log SUCCESS "SFTP health check passed"
    else
        log WARN "SFTP health check unavailable"
    fi

    return 0
}

rollback() {
    log WARN "Rolling back to backup: $BACKUP_PATH"

    if $DRY_RUN; then
        log INFO "[DRY-RUN] Would rollback to: $BACKUP_PATH"
        return 0
    fi

    if ! ssh "$SERVER" "[ -d $BACKUP_PATH ]" 2>/dev/null; then
        log ERROR "Backup not found: $BACKUP_PATH"
        return 1
    fi

    if ssh "$SERVER" "rm -rf ${REMOTE_PATH}.failed && mv $REMOTE_PATH ${REMOTE_PATH}.failed && mv $BACKUP_PATH $REMOTE_PATH" 2>&1 | tee -a "$DEPLOY_LOG"; then
        log SUCCESS "Rollback completed"

        # Restart service if configured
        if [ -n "$RESTART_SERVICE" ]; then
            ssh "$SERVER" "pm2 restart $RESTART_SERVICE" 2>&1 | tee -a "$DEPLOY_LOG"
        fi

        return 0
    else
        log ERROR "Rollback failed! Manual intervention required"
        return 1
    fi
}

generate_report() {
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))

    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║       Deployment Report                ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "Deployment ID: $DEPLOY_ID"
    echo "Server: $SERVER"
    echo "Remote Path: $REMOTE_PATH"
    echo "Method: $DEPLOY_METHOD"
    echo "Duration: ${minutes}m ${seconds}s"
    echo ""

    if [ -f "$DEPLOY_LOG" ]; then
        local errors=$(grep -c '\[ERROR\]' "$DEPLOY_LOG" || echo 0)
        local warnings=$(grep -c '\[WARN\]' "$DEPLOY_LOG" || echo 0)

        echo "Errors: $errors"
        echo "Warnings: $warnings"
        echo ""
        echo "Full log: $DEPLOY_LOG"
    fi
    echo ""
}

###############################################################################
# Parse Command Line Arguments
###############################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--method)
            DEPLOY_METHOD="$2"
            shift 2
            ;;
        -s|--server)
            SERVER="$2"
            shift 2
            ;;
        -p|--path)
            REMOTE_PATH="$2"
            shift 2
            ;;
        -b|--build)
            RUN_BUILD=true
            shift
            ;;
        -r|--restart)
            RESTART_SERVICE="$2"
            shift 2
            ;;
        -c|--check)
            RUN_HEALTH_CHECK=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            log ERROR "Unknown option: $1"
            show_help
            ;;
    esac
done

###############################################################################
# Main Deployment Flow
###############################################################################

main() {
    local start_time=$(date +%s)

    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║   High-Speed SFTP Deployment           ║"
    echo "╚════════════════════════════════════════╝"
    echo ""

    log INFO "Starting deployment: $DEPLOY_ID"
    log INFO "Log file: $DEPLOY_LOG"

    # Pre-deployment checks
    check_dependencies || exit 1
    check_ssh_connection || exit 1
    check_disk_space || exit 1

    # Build if requested
    if $RUN_BUILD; then
        run_build || exit 1
    fi

    check_build_exists || exit 1

    # Auto-detect method if set to auto
    if [ "$DEPLOY_METHOD" == "auto" ]; then
        DEPLOY_METHOD=$(detect_deploy_method)
        log INFO "Auto-detected deployment method: $DEPLOY_METHOD"
    fi

    # Create backup
    create_backup || {
        log WARN "Backup failed, continuing anyway"
    }

    # Deploy
    local deploy_success=false
    case $DEPLOY_METHOD in
        rsync)
            deploy_rsync && deploy_success=true
            ;;
        tar)
            deploy_tar && deploy_success=true
            ;;
        parallel)
            deploy_parallel && deploy_success=true
            ;;
        *)
            log ERROR "Unknown deployment method: $DEPLOY_METHOD"
            exit 1
            ;;
    esac

    # Handle deployment result
    if ! $deploy_success; then
        log ERROR "Deployment failed"

        if $BACKUP_ENABLED && ! $DRY_RUN; then
            read -p "Rollback to backup? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rollback
            fi
        fi

        generate_report
        exit 1
    fi

    log SUCCESS "Deployment completed successfully"

    # Restart service if configured
    restart_service || {
        log WARN "Service restart failed, but deployment succeeded"
    }

    # Run health checks
    run_health_check || {
        log WARN "Health checks failed"
    }

    # Close multiplexed connection
    ssh -O exit "$SERVER" 2>/dev/null || true

    # Generate report
    generate_report

    log SUCCESS "All done! Deployment ID: $DEPLOY_ID"
    echo ""
}

# Run main function
main "$@"
