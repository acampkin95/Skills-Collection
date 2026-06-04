---
name: engram-hooks-tests
description: Use when running the Engram live API test suite against the Memory API, or understanding how the memory recall/store hooks work. Covers 56 tests across health, CRUD, search, RAG, graph, tenants, key management, audit logging, maintenance, export, and auth edge cases. Scripts at ~/.claude/skills/engram/engram-hooks-tests/scripts/.
---

# Engram Memory API — Test Suite

Run the full Engram Memory API test suite against the live instance on devnode.

## Usage

```bash
# Run full test suite
bash ~/.claude/skills/engram/engram-hooks-tests/scripts/test-memory-api.sh

# Or set custom API target
ENGRAM_API_URL=http://100.78.187.5:8000 ENGRAM_API_KEY=your-key bash ~/.claude/skills/engram/engram-hooks-tests/scripts/test-memory-api.sh
```

## Test Categories (56 tests)

| Category | Tests | Description |
|---|---|---|
| Health & Stats | 5 | Health check, detailed health, stats, analytics, search stats |
| Memory CRUD | 10 | Add tier 1/2/3, all memory types, get, list, batch add |
| Search & RAG | 6 | Semantic search, tier filter, tag filter, RAG, context build |
| Entities & Graph | 6 | Add entities, list, get by name, query graph |
| Tenants | 4 | Create, list, scoped memory, delete |
| Key Management | 6 | List, create, use, rename, revoke, verify rejection |
| Audit Log | 5 | Query, method filter, path filter, summary 1h/24h |
| Maintenance | 4 | Cleanup, decay, confidence maintenance, consolidation |
| Export | 3 | JSON, CSV, Markdown (tier-scoped) |
| Auth Edge Cases | 4 | No auth, invalid key, empty key, invalid JWT |
| Cleanup | 3 | Delete test memories, bulk delete, tenant cleanup |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ENGRAM_API_URL` | `http://100.78.187.5:8000` | Memory API base URL |
| `ENGRAM_API_KEY` | `88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc` | API key for auth |

## Exit Codes

- `0` — All critical tests passed
- `1` — One or more critical tests failed

## Output

Color-coded pass/fail per test, followed by a summary table:
```
==========================================
RESULTS: 52/56 passed, 4 failed
==========================================
Category          Pass  Fail
Health & Stats       5     0
Memory CRUD         10     0
...
```

## Memory Hooks

Two hooks run automatically in every Claude Code session:

| Hook | Event | Script | Action |
|------|-------|--------|--------|
| Memory Recall | `UserPromptSubmit` | `memory-recall.sh` | Searches memory for relevant context, injects via `ENGRAM_MEMORY_CONTEXT` |
| Memory Store | `Stop` | `memory-store.sh` | Extracts key facts/decisions from session, stores as memories |

### Recall Hook Behaviour

- Skips prompts < 15 chars, slash commands (`/`), and bare `!`
- Strips markdown code fences before building the search query (cleaner vectors)
- Query: first 300 chars of prompt
- Threshold: score ≥ **0.65** (was 0.7)
- Results: up to **5** memories (was 3)
- Output format: `[type|imp:N.N] content (score:N.NN) #tags`

### Store Hook Behaviour

- Detects **action keywords**: deployed, fixed, created, configured, installed, updated, migrated, resolved, implemented, refactored, removed, added, changed, renamed, moved, deleted, enabled, disabled, upgraded, downgraded, reverted
- **Importance**: 0.7 for sessions with code/tech signals (`.ts`, `docker`, `npm`, `error:` etc.), 0.5 otherwise
- **memory_type**: `fact` for code-change sessions, `conversation` otherwise
- **Auto-tags subproject**: `platform`, `mcp`, `memory-api`, or `crawler` based on content; adds `code-change` tag when code signals present
- Deduplicates action lines (by first 60 chars), stores up to 6 per session

### Testing Hooks Manually

```bash
# Test recall hook
CLAUDE_USER_CONTENT="deploying to devnode" \
CLAUDE_ENV_FILE=/tmp/test-env.txt \
bash ~/.claude/skills/engram/engram-hooks-tests/scripts/memory-recall.sh
cat /tmp/test-env.txt

# Test store hook
CLAUDE_SUMMARY="deployed memory-api to acdev-devnode, fixed redis connection" \
bash ~/.claude/skills/engram/engram-hooks-tests/scripts/memory-store.sh
```

### Hook Configuration (settings.json)

```json
"hooks": {
  "UserPromptSubmit": [{"matcher": "", "hooks": [{"type": "command",
    "command": "/Users/alex/.claude/skills/engram/engram-hooks-tests/scripts/memory-recall.sh",
    "timeout": 5}]}],
  "Stop": [{"matcher": "", "hooks": [{"type": "command",
    "command": "/Users/alex/.claude/skills/engram/engram-hooks-tests/scripts/memory-store.sh",
    "timeout": 10}]}]
}
```
