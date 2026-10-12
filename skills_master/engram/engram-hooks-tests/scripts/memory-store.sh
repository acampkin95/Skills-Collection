#!/usr/bin/env bash
# Engram Memory — Post-session store hook (v2)
# Tier-aware storage with project detection and content classification

set -o pipefail

API="${ENGRAM_API_URL:-http://100.78.187.5:8000}"
KEY="${ENGRAM_API_KEY:-88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc}"
TENANT="${ENGRAM_TENANT_ID:-default}"

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
SUMMARY="${CLAUDE_SUMMARY:-}"
CONTENT="${SUMMARY:-$TRANSCRIPT}"

CWD="${PWD:-}"

# Skip if no substantial content
[ ${#CONTENT} -lt 100 ] && exit 0

# ---------------------------------------------------------------------------
# Project detection from CWD
# ---------------------------------------------------------------------------
PROJECT_SLUG=""
if [ -n "$CWD" ]; then
  PROJECT_SLUG=$(printf '%s' "$CWD" | python3 -c '
import sys, re
path = sys.stdin.read().strip()
base = path.split("/")[-1] if path else ""
slug = re.sub(r"^[0-9]+_", "", base).lower()
slug = re.sub(r"[_\s]+", "-", slug)
print(slug[:64] if slug else "")
' 2>/dev/null)
fi

# ---------------------------------------------------------------------------
# Extract key facts, classify tier, build payload
# ---------------------------------------------------------------------------
MEMORY_PAYLOAD=$(printf '%s' "$CONTENT" | python3 - <<'EOF'
import json, sys, re

ACTION_KEYWORDS = [
    "deployed", "fixed", "created", "configured", "installed",
    "updated", "migrated", "resolved", "implemented", "refactored",
    "removed", "added", "changed", "renamed", "moved", "deleted",
    "enabled", "disabled", "upgraded", "downgraded", "reverted",
]

CODE_SIGNALS = [
    ".ts", ".tsx", ".py", ".sh", ".json", ".yml", ".yaml",
    "function", "class", "import", "export", "const ", "async ",
    "docker", "npm", "pip", "git", "ssh", "curl", "api", "http",
    "error:", "failed:", "fixed:", "bug:", "feat:", "fix(",
]

# Global/best-practice signals
GLOBAL_SIGNALS = [
    "best practice", "always", "never", "recommend", "standard",
    "pattern", "principle", "guideline", "convention",
]

# User preference signals
USER_SIGNALS = [
    "prefer", "preference", "i like", "i use", "my workflow",
    "my setup", "don't like",
]

content = sys.stdin.read()[:4000]
content_lower = content.lower()

found_actions = [k for k in ACTION_KEYWORDS if k in content_lower]
if not found_actions:
    sys.exit(0)

lines = content.split("\n")

# Collect lines containing action keywords
action_lines = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    line_lower = line.lower()
    if any(k in line_lower for k in ACTION_KEYWORDS):
        line = re.sub(r'^[#*\->\s]+', '', line).strip()
        if len(line) > 20:
            action_lines.append(line)

if not action_lines:
    sys.exit(0)

# Deduplicate while preserving order
seen = set()
unique_lines = []
for l in action_lines:
    key = l[:60].lower()
    if key not in seen:
        seen.add(key)
        unique_lines.append(l)

# Build summary text from top 6 unique lines
summary_text = " | ".join(unique_lines[:6])[:600]

# Detect content characteristics
has_code = any(sig in content_lower for sig in CODE_SIGNALS)
has_global = any(sig in content_lower for sig in GLOBAL_SIGNALS)
has_user = any(sig in content_lower for sig in USER_SIGNALS)

# Tier determination
if has_global:
    tier = 3
elif has_user:
    tier = 2
elif has_code:
    tier = 1
else:
    tier = 2

# Importance based on content richness
importance = 0.8 if has_code and has_global else (0.7 if has_code else 0.5)

# Tags
tags = ["session-auto"]
if has_code:
    tags.append("code-change")

# Project detection from content
project_slug = ""
import os
cwd = os.environ.get("PWD", "")
if cwd:
    base = cwd.split("/")[-1] if cwd else ""
    project_slug = re.sub(r"^[0-9]+_", "", base).lower()
    project_slug = re.sub(r"[_\s]+", "-", project_slug)[:64]

# Subproject detection from content
if "engram-platform" in content_lower or "next.js" in content_lower or "frontend" in content_lower:
    tags.append("platform")
elif "engram-mcp" in content_lower or "mcp server" in content_lower:
    tags.append("mcp")
elif "engram-memory" in content_lower or "memory-api" in content_lower or "weaviate" in content_lower:
    tags.append("memory-api")
elif "crawler" in content_lower or "crawl4ai" in content_lower:
    tags.append("crawler")

tags.append(f"tier-{tier}")
if project_slug:
    tags.append(f"project:{project_slug}")

payload = {
    "content": summary_text,
    "memory_type": "fact" if has_code else "conversation",
    "tier": tier,
    "importance": importance,
    "tags": tags,
    "tenant_id": os.environ.get("ENGRAM_TENANT_ID", "default"),
}
if project_slug and tier == 1:
    payload["project_id"] = project_slug

print(json.dumps(payload))
EOF
) 2>/dev/null

[ -z "$MEMORY_PAYLOAD" ] && exit 0

# Store the memory
curl -sf --connect-timeout 2 --max-time 5 \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d "$MEMORY_PAYLOAD" \
  "$API/memories" >/dev/null 2>&1

exit 0
