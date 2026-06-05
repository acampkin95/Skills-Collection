# Learned Skill: Multi-Config Model Migration

**Extracted:** 2026-02-22
**Updated:** 2026-03-06
**Session type:** Config migration
**Confidence:** High

## Pattern: Migrating model tiers across OMC + oh-my-opencode

When the user asks to change model routing (e.g. opus → sonnet, or sonnet → minimax), two config surfaces must be updated together:

### 1. `~/.claude/CLAUDE.md` (OMC agent catalog)

Search for all `(opus)` annotations in:
- `<agent_catalog>` — agent role definitions
- `<team_pipeline>` — stage agent routing (team-plan, team-prd)
- `<model_routing>` — tier descriptions and examples
- `<verification>` — sizing guidance model references

Replace `(opus)` → `(sonnet)` and update any `model="opus"` example calls.

When collapsing from 3-tier (haiku/sonnet/opus) to 2-tier (haiku/sonnet), fold opus descriptions into sonnet's line:
```
- `sonnet`: standard implementation, debugging, reviews, architecture, deep analysis
```

### 2. `~/.config/opencode/oh-my-opencode.json` (oh-my-opencode agents)

- Replace model strings for affected agents
- **Remove `variant: max`** when downgrading from opus — this field is opus-specific (extended output). Sonnet and other models do not support it; leaving it may cause schema errors or be silently ignored.
- Add a migration entry to `_migrations[]`:
  ```json
  "model-version:anthropic/claude-opus-4-6->anthropic/claude-sonnet-4-6"
  ```

### 3. Verification commands

```bash
# Confirm oracle is on Opus with high variant (not fast/max/1M)
grep -A3 '"oracle"' ~/.config/opencode/oh-my-opencode.json

# Confirm no stray max variants on non-oracle agents
grep '"variant": "max"' ~/.config/opencode/oh-my-opencode.json

# Confirm new providers present
grep '"moonshot"\|"perplexity"' ~/.config/opencode/opencode.json
```

---

## Pattern: Multi-Model Autonomous Routing (2026-03-06)

When setting up multiple model providers for autonomous/agentic work:

### Agent Role → Model Assignments

| Agent / Category | Model | Rationale |
|---|---|---|
| `sisyphus` (orchestrator) | `anthropic/claude-sonnet-4-6` variant `medium` | Orchestration doesn't need max tokens |
| `sisyphus-junior` (autonomous worker) | `moonshot/kimi-k2` | Primary fast autonomous execution |
| `oracle` | `anthropic/claude-opus-4-6` variant `high` | Deep reasoning ONLY — NOT fast/max/1M |
| `prometheus` / `metis` (planning) | `anthropic/claude-sonnet-4-6` (no variant) | Planning stays Sonnet, no extended tokens |
| `librarian` (research) | `perplexity/sonar-pro` | Real-time web search for research tasks |
| `hephaestus` / `momus` | `openai/gpt-5.x` | Selective ChatGPT use (review, codex) |
| coding agents (`javascript-dev`, `react-specialist`, `backend-developer`) | `zai-coding-plan/glm-5` | GLM-5 Opencode Go for coding |
| `typescript-pro` / `python-pro` | `minimax/minimax-m2.5-highspeed` | High-speed mechanical code gen |
| `unspecified-low` category | `moonshot/kimi-k2` | Kimi for general autonomous work |
| `unspecified-high` category | `zai-coding-plan/glm-5` | GLM-5 for larger autonomous tasks |
| `quick` category | `anthropic/claude-haiku-4-5` | Trivial tasks stay on haiku |

### Autopilot No-Questions Mode

Add `permission` block to `sisyphus` AND `sisyphus-junior` in oh-my-opencode.json:
```json
"permission": {
  "edit": "allow",
  "bash": "allow",
  "webfetch": "allow",
  "doom_loop": "allow"
}
```

This stops the orchestrator from asking approval for tool usage in autopilot mode.

### Adding New Providers to opencode.json

All custom providers use `@ai-sdk/openai-compatible` npm package. Pattern:
```json
"moonshot": {
  "npm": "@ai-sdk/openai-compatible",
  "options": {
    "baseURL": "https://api.moonshot.cn/v1",
    "apiKey": "YOUR_KEY"
  },
  "models": {
    "kimi-k2": {
      "name": "Kimi K2 (Opencode Go - Primary Autonomous)",
      "limit": { "context": 131072, "output": 8192 },
      "modalities": { "input": ["text"], "output": ["text"] }
    }
  }
},
"perplexity": {
  "npm": "@ai-sdk/openai-compatible",
  "options": {
    "baseURL": "https://api.perplexity.ai",
    "apiKey": "YOUR_KEY"
  },
  "models": {
    "sonar-pro": { ... },
    "sonar-reasoning-pro": { ... }
  }
}
```

**CRITICAL:** When adding models to an existing provider's `models` object, append INSIDE the `models: {}` block. Never add model entries at the provider root level (alongside `options` and `models`). This is easy to mis-do with `append` operations — always verify the indentation level after edit. If in doubt, replace the entire provider block.

### Key API endpoints

| Provider | Base URL | Key Env Var |
|---|---|---|
| Moonshot (Kimi) | `https://api.moonshot.cn/v1` | `KIMI_API_KEY` |
| Perplexity | `https://api.perplexity.ai` | `PERPLEXITY_API_KEY` |
| ZhipuAI (GLM) | Built into `zai-coding-plan` provider | `ZAI_API_KEY` |
| Minimax | Built-in opencode provider | (built-in) |

---

## Pattern: Spot-optimizing specific agents to faster/cheaper models

For execution-heavy agents (e.g. `typescript-pro`, `python-pro`) that do mechanical code generation rather than reasoning, `minimax/minimax-m2.5-highspeed` is a cost-effective alternative to sonnet.

Analysis/review agents (`debugger`, `security-architecture-analyst`, `production-code-auditor`) should stay on sonnet for reasoning quality.

## Pattern: Parallel edits for independent config files

When two config files need independent changes, fire Edit calls in the same message turn — they execute concurrently and halve wall time.

```
Edit(CLAUDE.md, ...) + Edit(oh-my-opencode.json, ...)  ← same message, parallel
```
