## Script Development Patterns

### Bash Template (Reusable)

```bash
#!/bin/bash
set -euo pipefail

# Script: my-script.sh
# Purpose: What this script does
# Usage: ./my-script.sh [OPTIONS]

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMEOUT="${TIMEOUT:-10}"
MAX_RETRIES="${MAX_RETRIES:-3}"

log() { printf '%s\n' "$*" >&2; }
info() { log "$(printf '%b' "${BLUE}i${NC}") $*"; }
success() { log "$(printf '%b' "${GREEN}ok${NC}") $*"; }
warn() { log "$(printf '%b' "${YELLOW}warn${NC}") $*"; }
error() { log "$(printf '%b' "${RED}err${NC}") $*"; exit 1; }

main() {
  info "Validating prerequisites..."
  [[ -f "$PROJECT_ROOT/.env" ]] || error ".env file not found"
  command -v docker >/dev/null || error "Docker not installed"
  success "Script completed"
}

main "$@"
```

### Error Handling Pattern

```bash
set -euo pipefail
trap 'rm -f /tmp/tempfile 2>/dev/null' EXIT

if ! command -v docker &>/dev/null; then
  echo "ERROR: Docker not found" >&2; exit 1
fi

curl -f "$URL" || {
  echo "WARNING: Failed to reach $URL, retrying..." >&2
  sleep 5
  curl -f "$URL" || exit 1
}
```

