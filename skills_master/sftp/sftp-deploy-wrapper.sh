#!/bin/bash
###############################################################################
# Quick Deployment Wrappers
# Convenient shortcuts for common deployment scenarios
###############################################################################

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_SCRIPT="$SCRIPT_DIR/sftp-deploy.sh"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

###############################################################################
# Wrapper Functions
###############################################################################

deploy_quick() {
    echo -e "${BLUE}Quick Deploy${NC} - No build, rsync only"
    "$DEPLOY_SCRIPT" --method rsync --restart wattlewool --check
}

deploy_full() {
    echo -e "${BLUE}Full Deploy${NC} - Build, deploy, restart, check"
    "$DEPLOY_SCRIPT" --build --method auto --restart wattlewool --check
}

deploy_fast() {
    echo -e "${BLUE}Fast Deploy${NC} - Tar stream, no build"
    "$DEPLOY_SCRIPT" --method tar --restart wattlewool --check
}

deploy_parallel() {
    echo -e "${BLUE}Parallel Deploy${NC} - Fastest for large builds"
    "$DEPLOY_SCRIPT" --method parallel --restart wattlewool --check
}

deploy_dry() {
    echo -e "${BLUE}Dry Run${NC} - Show what would be done"
    "$DEPLOY_SCRIPT" --dry-run --verbose
}

deploy_api() {
    echo -e "${BLUE}API Routes Only${NC} - Deploy just API routes"
    cd .next/standalone/.next/server
    rsync -avz --delete app/api/ vmi02d:/opt/wattlewool/.next/standalone/.next/server/app/api/
    ssh vmi02d "pm2 reload wattlewool"
    echo -e "${GREEN}✓${NC} API routes deployed"
}

deploy_help() {
    echo "Quick Deployment Wrappers"
    echo ""
    echo "Usage: source ~/.claude/skills/sftp-deploy-wrapper.sh"
    echo ""
    echo "Available commands:"
    echo "  deploy-quick      - Quick rsync deployment (no build)"
    echo "  deploy-full       - Full deployment with build"
    echo "  deploy-fast       - Fast tar stream deployment"
    echo "  deploy-parallel   - Parallel chunk deployment (fastest)"
    echo "  deploy-dry        - Dry run (test mode)"
    echo "  deploy-api        - Deploy API routes only"
    echo ""
    echo "Advanced:"
    echo "  ~/.claude/skills/sftp-deploy.sh --help"
}

###############################################################################
# Export Functions (if sourced)
###############################################################################

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced, export functions
    export -f deploy_quick
    export -f deploy_full
    export -f deploy_fast
    export -f deploy_parallel
    export -f deploy_dry
    export -f deploy_api
    export -f deploy_help

    echo -e "${GREEN}✓${NC} Deployment wrappers loaded"
    echo "Run: deploy-help"
else
    # Script is being executed directly
    if [ $# -eq 0 ]; then
        deploy_help
    else
        case "$1" in
            quick) deploy_quick ;;
            full) deploy_full ;;
            fast) deploy_fast ;;
            parallel) deploy_parallel ;;
            dry) deploy_dry ;;
            api) deploy_api ;;
            help|*) deploy_help ;;
        esac
    fi
fi
