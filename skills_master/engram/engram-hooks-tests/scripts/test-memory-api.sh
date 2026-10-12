#!/usr/bin/env bash
# Engram Memory API — Test Suite Runner
# Delegates to Python for reliable JSON parsing
set -o pipefail

API="${ENGRAM_API_URL:-http://100.78.187.5:8000}"
KEY="${ENGRAM_API_KEY:-88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc}"

exec python3 "$(dirname "$0")/test-memory-api.py" "$API" "$KEY"
