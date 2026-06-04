#!/bin/bash
###############################################################################
# Deployment Hooks System
# Pre/post deployment hooks for custom actions
###############################################################################

HOOKS_DIR="${HOME}/.claude/skills/hooks"
mkdir -p "$HOOKS_DIR"

###############################################################################
# Hook Functions
###############################################################################

run_pre_deploy_hooks() {
    local context="$1"  # build|deploy|restart

    if [ -d "$HOOKS_DIR/pre-${context}.d" ]; then
        echo "[HOOKS] Running pre-${context} hooks..."
        for hook in "$HOOKS_DIR/pre-${context}.d"/*.sh; do
            [ -f "$hook" ] && [ -x "$hook" ] && {
                echo "[HOOKS] Executing: $(basename $hook)"
                "$hook" || echo "[HOOKS] Warning: Hook failed: $hook"
            }
        done
    fi
}

run_post_deploy_hooks() {
    local context="$1"  # deploy|restart|complete

    if [ -d "$HOOKS_DIR/post-${context}.d" ]; then
        echo "[HOOKS] Running post-${context} hooks..."
        for hook in "$HOOKS_DIR/post-${context}.d"/*.sh; do
            [ -f "$hook" ] && [ -x "$hook" ] && {
                echo "[HOOKS] Executing: $(basename $hook)"
                "$hook" || echo "[HOOKS] Warning: Hook failed: $hook"
            }
        done
    fi
}

###############################################################################
# Example Hooks Setup
###############################################################################

setup_example_hooks() {
    echo "Setting up example hooks..."

    # Create hook directories
    mkdir -p "$HOOKS_DIR"/{pre-build.d,pre-deploy.d,post-deploy.d,post-complete.d}

    # Pre-build hook: Check for uncommitted changes
    cat > "$HOOKS_DIR/pre-build.d/01-check-git.sh" << 'EOF'
#!/bin/bash
# Check for uncommitted changes

if [ -d .git ] && ! git diff-index --quiet HEAD --; then
    echo "[HOOK] Warning: Uncommitted changes detected"
    git status --short
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi
EOF

    # Pre-deploy hook: Tag deployment
    cat > "$HOOKS_DIR/pre-deploy.d/01-tag-deploy.sh" << 'EOF'
#!/bin/bash
# Tag deployment in git

if [ -d .git ]; then
    DEPLOY_TAG="deploy-$(date +%Y%m%d-%H%M%S)"
    git tag -a "$DEPLOY_TAG" -m "Deployment: $(date)" 2>/dev/null || true
    echo "[HOOK] Tagged: $DEPLOY_TAG"
fi
EOF

    # Post-deploy hook: Notify deployment
    cat > "$HOOKS_DIR/post-deploy.d/01-notify.sh" << 'EOF'
#!/bin/bash
# Send deployment notification

DEPLOY_ID="${DEPLOY_ID:-unknown}"
SERVER="${SERVER:-unknown}"

# Log to deployment history
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deployed to $SERVER - ID: $DEPLOY_ID" >> ~/.claude/deployment-history.log

# Optional: Send Slack/Discord notification
# curl -X POST webhook_url -d "Deployed to $SERVER"

echo "[HOOK] Deployment logged"
EOF

    # Post-complete hook: Cleanup
    cat > "$HOOKS_DIR/post-complete.d/01-cleanup.sh" << 'EOF'
#!/bin/bash
# Cleanup temporary files

# Remove old deployment logs (keep last 10)
ls -t /tmp/deploy-*.log 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

# Remove old backups on server (keep last 5)
ssh vmi02d "ls -dt /opt/wattlewool.backup-* 2>/dev/null | tail -n +6 | xargs rm -rf" 2>/dev/null || true

echo "[HOOK] Cleanup completed"
EOF

    # Make all hooks executable
    chmod +x "$HOOKS_DIR"/**/*.sh 2>/dev/null || true

    echo "Example hooks created in: $HOOKS_DIR"
    echo ""
    echo "Hook directories:"
    echo "  - pre-build.d/    - Run before npm run build"
    echo "  - pre-deploy.d/   - Run before deployment"
    echo "  - post-deploy.d/  - Run after deployment"
    echo "  - post-complete.d/ - Run after everything"
}

###############################################################################
# Hook Management
###############################################################################

list_hooks() {
    echo "Installed Hooks:"
    echo ""

    for dir in "$HOOKS_DIR"/*.d; do
        if [ -d "$dir" ]; then
            echo "$(basename $dir):"
            for hook in "$dir"/*.sh; do
                if [ -f "$hook" ]; then
                    local status="✗ disabled"
                    [ -x "$hook" ] && status="✓ enabled"
                    echo "  $status - $(basename $hook)"
                fi
            done
            echo ""
        fi
    done
}

enable_hook() {
    local hook_path="$1"
    if [ -f "$hook_path" ]; then
        chmod +x "$hook_path"
        echo "Enabled: $hook_path"
    else
        echo "Hook not found: $hook_path"
    fi
}

disable_hook() {
    local hook_path="$1"
    if [ -f "$hook_path" ]; then
        chmod -x "$hook_path"
        echo "Disabled: $hook_path"
    else
        echo "Hook not found: $hook_path"
    fi
}

###############################################################################
# CLI Interface
###############################################################################

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    case "${1:-help}" in
        setup)
            setup_example_hooks
            ;;
        list)
            list_hooks
            ;;
        enable)
            enable_hook "$2"
            ;;
        disable)
            disable_hook "$2"
            ;;
        *)
            echo "Deployment Hooks Management"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  setup    - Create example hooks"
            echo "  list     - List installed hooks"
            echo "  enable   - Enable a hook"
            echo "  disable  - Disable a hook"
            echo ""
            echo "Hook locations: $HOOKS_DIR"
            ;;
    esac
fi
