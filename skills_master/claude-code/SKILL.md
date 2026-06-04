---
name: claude-code
description: Claude Code CLI configuration, MCP server setup, and multi-agent orchestration. Use for settings.json, model routing, subagent spawning, and provider configuration.
version: 2.0.0
reviewed: "2026-06-04"
---
# Claude Code Development Knowledge

## Quick Reference

### Configuration File Locations

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | User settings (permissions, hooks, model, MCP servers) |
| `.claude/settings.json` | Project settings (shared via git) |
| `.claude/settings.local.json` | Local project settings (gitignored) |
| `~/.claude.json` | Global state (theme, OAuth, allowed tools) |
| `.mcp.json` | Project MCP servers (shared via git) |
| `CLAUDE.md` or `.claude/CLAUDE.md` | Memory/instructions loaded at startup |
| `CLAUDE.local.md` | Local memory (gitignored) |

### Model Aliases

| Alias | Description |
|-------|-------------|
| `default` | Recommended model based on account type |
| `sonnet` | Latest Sonnet 4.5 for daily coding |
| `opus` | Opus 4.5 for complex reasoning |
| `haiku` | Fast/efficient for simple tasks |
| `sonnet[1m]` | Sonnet with 1M token context |
| `opusplan` | Opus for planning, Sonnet for execution |

### Essential Commands

```bash
# Model switching
claude --model opus                    # Start with specific model
/model sonnet                          # Switch mid-session

# MCP management
claude mcp list                        # List configured servers
claude mcp add --transport http <n> <url>  # Add HTTP server
claude mcp add --transport stdio <n> -- <cmd>  # Add local server
claude mcp remove <n>               # Remove server
/mcp                                   # Check status/authenticate

# Checkpointing (NEW in 2025)
/rewind                                # Rewind to previous state
/compact                               # Reduce context size
claude doctor                          # Check installation health
/status                                # Current model and account info
/config                                # Open settings interface

# Agent features (NEW in 2025)
/agents                                # List available subagents
/subagent <name>                       # Delegate to a subagent
```

## 2025 New Features

### Checkpointing System

Claude Code now saves state automatically before each change, enabling instant rewinds:

```bash
/rewind           # Rewind to previous state (press Esc twice for quick rewind)
```

**What rewinding restores:**
- Code state (Claude's edits only)
- Conversation context

**What it doesn't restore:**
- User edits
- Bash command outputs
- Shell state

Use this for confident delegation of complex refactoring tasks.

### Subagents

Create specialized AI agents for parallel work:

**Configuration (`~/.claude/agents/reviewer.yaml`):**
```yaml
name: code-reviewer
description: Reviews code for security, performance, and maintainability
model: sonnet
color: purple
```

**Usage:**
```bash
/subagent code-reviewer    # Delegate to reviewer agent
/subagent backend-dev      # Parallel backend work
/subagent frontend-dev     # Parallel frontend work
```

### Plan Mode (Shift+Tab twice)

Outline implementation steps before writing code to reduce mistakes and token usage.

### Enhanced MCP Integration

```bash

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.