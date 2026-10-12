#!/usr/bin/env bash
# Engram Memory — Pre-prompt recall hook (v2)
# Multi-tier recall with project awareness
# Searches Tier 1 (project) → Tier 2 (user) → Tier 3 (global), merges results

set -o pipefail

API="${ENGRAM_API_URL:-http://100.78.187.5:8000}"
KEY="${ENGRAM_API_KEY:-88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc}"
TENANT="${ENGRAM_TENANT_ID:-default}"

PROMPT="${CLAUDE_USER_CONTENT:-}"
CWD="${PWD:-}"

# Skip if prompt is too short, a slash command, or a bare bang
[ ${#PROMPT} -lt 15 ] && exit 0
[[ "$PROMPT" == /* ]] && exit 0
[[ "$PROMPT" == "!" ]] && exit 0

# ---------------------------------------------------------------------------
# Project detection from CWD
# ---------------------------------------------------------------------------
PROJECT_SLUG=""
if [ -n "$CWD" ]; then
  PROJECT_SLUG=$(printf '%s' "$CWD" | python3 -c '
import sys, re
path = sys.stdin.read().strip()
base = path.split("/")[-1] if path else ""
# Strip leading numbers like "09_", convert to kebab-case
slug = re.sub(r"^[0-9]+_", "", base).lower()
slug = re.sub(r"[_\s]+", "-", slug)
print(slug[:64] if slug else "")
' 2>/dev/null)
fi

# ---------------------------------------------------------------------------
# Build search query from prompt
# ---------------------------------------------------------------------------
PAYLOAD=$(printf '%s' "$PROMPT" | python3 - <<'EOF'
import json, sys, re
prompt = sys.stdin.read()
# Strip markdown code fences and backticks for cleaner query
clean = re.sub(r'```[^`]*```', '', prompt, flags=re.DOTALL)
clean = re.sub(r'`[^`]+`', '', clean)
clean = clean.strip()[:300]
if not clean:
    clean = prompt[:300]
print(json.dumps({"query": clean}))
EOF
) 2>/dev/null || exit 0

[ -z "$PAYLOAD" ] && exit 0

QUERY=$(printf '%s' "$PAYLOAD" | python3 -c "import json,sys; print(json.load(sys.stdin)['query'])" 2>/dev/null)
[ -z "$QUERY" ] && exit 0

# ---------------------------------------------------------------------------
# Multi-tier recall search
# ---------------------------------------------------------------------------
recall_tier() {
  local tier=$1 limit=$2 project_filter=""
  if [ "$tier" = "1" ] && [ -n "$PROJECT_SLUG" ]; then
    project_filter="\"project_id\":\"$PROJECT_SLUG\","
  fi
  curl -sf --connect-timeout 2 --max-time 4 \
    -H "X-API-Key: $KEY" \
    -H "Content-Type: application/json" \
    -X POST \
    -d "{\"query\":$(printf '%s' "$QUERY" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),\"tier\":$tier,\"tenant_id\":\"$TENANT\",${project_filter}\"limit\":$limit,\"min_importance\":0.25}" \
    "$API/memories/search" 2>/dev/null
}

# Search all tiers in parallel (Tier 1: 5, Tier 2: 3, Tier 3: 2)
T1_RESULTS=$(recall_tier 1 5) || T1_RESULTS=""
T2_RESULTS=$(recall_tier 2 3) || T2_RESULTS=""
T3_RESULTS=$(recall_tier 3 2) || T3_RESULTS=""

# ---------------------------------------------------------------------------
# Merge, deduplicate, and format results
# ---------------------------------------------------------------------------
CONTEXT=$(python3 - <<PYEOF
import json, sys

tier_labels = {1: "project", 2: "user", 3: "global"}
seen_ids = set()
all_memories = []

for tier_num, raw in [(1, """$T1_RESULTS"""), (2, """$T2_RESULTS"""), (3, """$T3_RESULTS""")]:
    if not raw:
        continue
    try:
        data = json.loads(raw)
        for r in data.get("results", []):
            mid = r.get("memory_id", "")
            score = r.get("score", 0)
            if score < 0.55:
                continue
            if mid and mid in seen_ids:
                continue
            if mid:
                seen_ids.add(mid)
            all_memories.append((tier_num, score, r))
    except Exception:
        pass

if not all_memories:
    sys.exit(0)

# Sort by score descending
all_memories.sort(key=lambda x: x[1], reverse=True)

lines = ["[Engram Memory Context]"]
for tier_num, score, r in all_memories[:8]:
    content = r.get("content", "")[:280]
    mtype = r.get("memory_type", "fact")
    importance = r.get("importance", 0)
    tags = ",".join(r.get("tags", [])[:3])
    tier_label = tier_labels.get(tier_num, "?")
    tag_str = f" #{tags}" if tags else ""
    lines.append(f"- [{tier_label}|{mtype}|imp:{importance:.1f}] {content} (score:{score:.2f}){tag_str}")

print("\n".join(lines))
PYEOF
) 2>/dev/null

# Inject context into conversation env
if [ -n "$CONTEXT" ] && [ -n "$CLAUDE_ENV_FILE" ]; then
  printf 'ENGRAM_MEMORY_CONTEXT=%s\n' "$(printf '%s' "$CONTEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')" >> "$CLAUDE_ENV_FILE"
fi
