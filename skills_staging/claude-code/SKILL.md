---
name: claude-code
description: Claude Code CLI configuration, MCP server setup, and multi-agent orchestration (OMC) automation.
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
# Full MCP workflow
claude mcp list            # List all configured servers
claude mcp add github      # Add GitHub MCP
claude mcp add filesystem  # Add file system access
claude mcp remove <name>   # Remove a server
```

**Popular MCP servers for 2025:**
- `github` - Repository and PR management
- `filesystem` - Local file operations
- `memory` - Cross-session context
- `fetch` - HTTP requests
- `brave-search` - Web search

## Configuration Deep Dive

For detailed settings.json options, see: `references/settings-reference.md`

### Key Settings Structure

```json
{
  "model": "opus",
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.example.com",
    "ANTHROPIC_AUTH_TOKEN": "your-token"
  },
  "permissions": {
    "allow": ["Bash(npm run:*)"],
    "deny": ["Read(.env)", "Read(.env.*)"],
    "defaultMode": "acceptEdits"
  },
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": { "API_KEY": "value" }
    }
  },
  "sandbox": { "enabled": true },
  "alwaysThinkingEnabled": true
}
```

### Alternative Provider Configuration

To use non-Anthropic providers (via LLM gateways):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://your-gateway.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your-api-key"
  }
}
```

**Environment variables for provider switching:**
- `CLAUDE_CODE_USE_BEDROCK=1` - Use AWS Bedrock
- `CLAUDE_CODE_USE_VERTEX=1` - Use Google Vertex AI
- `CLAUDE_CODE_USE_FOUNDRY=1` - Use Microsoft Foundry

## MCP Server Configuration

For comprehensive MCP documentation, see: `references/mcp-reference.md`

### Adding Servers

```bash
# Remote HTTP (recommended)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Remote SSE (deprecated, use HTTP)
claude mcp add --transport sse asana https://mcp.asana.com/sse

# Local stdio
claude mcp add --transport stdio airtable \
  --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server
```

### Scope Selection

- `--scope local` (default): You only, current project
- `--scope project`: Team-shared via `.mcp.json`
- `--scope user`: You only, all projects

## Troubleshooting

For detailed troubleshooting steps, see: `references/troubleshooting.md`

### Quick Fixes

**Authentication issues:**
```bash
/logout
rm -rf ~/.config/claude-code/auth.json
claude  # Re-authenticate
```

**Reset all configuration:**
```bash
rm ~/.claude.json
rm -rf ~/.claude/
rm -rf .claude/
rm .mcp.json
```

**MCP server not loading:**
```bash
# Test server directly
npx -y <package-name> --version

# Check configuration
claude mcp get <server-name>

# Restart Claude Code after changes
```

**Search/discovery issues:**
```bash
# Install system ripgrep
brew install ripgrep  # macOS
apt install ripgrep   # Linux

# Force use of system ripgrep
export USE_BUILTIN_RIPGREP=0
```

**High resource usage:**
- Use `/compact` to reduce context
- Close/restart between major tasks
- Add build directories to `.gitignore`

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_MODEL` | Override default model |
| `ANTHROPIC_BASE_URL` | Custom API endpoint |
| `ANTHROPIC_AUTH_TOKEN` | Custom auth token |
| `MAX_THINKING_TOKENS` | Extended thinking budget |
| `MCP_TIMEOUT` | MCP server startup timeout (ms) |
| `MAX_MCP_OUTPUT_TOKENS` | Max MCP response tokens (default: 25000) |
| `BASH_DEFAULT_TIMEOUT_MS` | Bash command timeout |
| `DISABLE_PROMPT_CACHING` | Set to `1` to disable caching |
| `CLAUDE_CONFIG_DIR` | Custom config location |

## Permissions System

### Permission Rules Format

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)",
      "Read(./.env)",
      "Read(./secrets/**)"
    ],
    "defaultMode": "bypassPermissions"
  }
}
```

### Permission Modes

- `default` - Ask for most operations
- `acceptEdits` - Auto-accept file edits
- `bypassPermissions` - Trust all operations (use `--dangerously-skip-permissions`)

## Hooks System

Configure pre/post actions for tool executions in settings.json:

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash": "echo 'Running command...'"
    },
    "PostToolUse": {
      "Edit": "npm run format"
    },
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "echo 'setup' >> \"$CLAUDE_ENV_FILE\""
      }]
    }]
  }
}
```

## Plugin System

### Enable Plugins

```json
{
  "enabledPlugins": {
    "plugin-name@marketplace": true
  },
  "extraKnownMarketplaces": {
    "custom-marketplace": {
      "source": "github",
      "repo": "org/plugins"
    }
  }
}
```

### Plugin Management

Use `/plugin` command to:
- Browse available plugins
- Install/uninstall plugins
- Enable/disable plugins
- Add/remove marketplaces

## Subagents

Custom AI agents stored as Markdown with YAML frontmatter:
- User agents: `~/.claude/agents/`
- Project agents: `.claude/agents/`

## Native Installation

Bypass npm issues with native installer:

```bash
# macOS/Linux/WSL
curl -fsSL https://claude.ai/install.sh | bash

# Specific version
curl -fsSL https://claude.ai/install.sh | bash -s 1.0.58

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```
