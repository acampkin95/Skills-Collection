# Claude Code Settings Reference

## Complete settings.json Options

### Core Settings

| Key | Description | Example |
|-----|-------------|---------|
| `model` | Default model alias or name | `"opus"`, `"claude-sonnet-4-5-20250929"` |
| `env` | Environment variables for sessions | `{"FOO": "bar"}` |
| `cleanupPeriodDays` | Session deletion threshold (default: 30) | `20` |
| `companyAnnouncements` | Startup messages (cycled randomly) | `["Welcome!"]` |
| `statusLine` | Custom status line config | See below |
| `outputStyle` | Adjust response style | `"Explanatory"` |
| `alwaysThinkingEnabled` | Extended thinking by default | `true` |
| `deepThinkingEnabled` | Deep thinking mode | `true` |

### API Configuration

| Key | Description |
|-----|-------------|
| `apiKeyHelper` | Script to generate auth value (executed in `/bin/sh`) |
| `forceLoginMethod` | `"claudeai"` or `"console"` to restrict login type |
| `forceLoginOrgUUID` | Auto-select organization during login |

### Permission Settings

```json
{
  "permissions": {
    "allow": ["Bash(git diff:*)"],
    "ask": ["Bash(git push:*)"],
    "deny": ["WebFetch", "Read(./.env)"],
    "additionalDirectories": ["../docs/"],
    "defaultMode": "acceptEdits",
    "disableBypassPermissionsMode": "disable"
  }
}
```

**Permission modes:**
- `default` - Standard interactive mode
- `acceptEdits` - Auto-accept file modifications
- `bypassPermissions` - Trust all operations

**Pattern syntax:**
- `Bash(command:*)` - Match command prefix
- `Read(path)` - File read permission
- `Edit(path)` - File edit permission
- `Write(path)` - File write permission
- `WebFetch` - Network access
- `**` - Recursive glob
- `*` - Single segment glob

### Sandbox Settings

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["git", "docker"],
    "allowUnsandboxedCommands": false,
    "network": {
      "allowUnixSockets": ["~/.ssh/agent-socket"],
      "allowLocalBinding": true,
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    },
    "enableWeakerNestedSandbox": false
  }
}
```

### Attribution Settings

```json
{
  "attribution": {
    "commit": "🤖 Generated with Claude\n\nCo-Authored-By: Claude <ai@example.com>",
    "pr": ""
  }
}
```

Empty string hides attribution. Replaces deprecated `includeCoAuthoredBy`.

### MCP Server Settings

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {"API_KEY": "value"}
    }
  },
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["memory", "github"],
  "disabledMcpjsonServers": ["filesystem"]
}
```

### Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": {
      "Bash": "echo 'Pre-bash hook'"
    },
    "PostToolUse": {
      "Edit": "npm run format"
    }
  },
  "disableAllHooks": false,
  "allowManagedHooksOnly": false
}
```

### Status Line Configuration

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

### File Suggestion Configuration

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  }
}
```

Script receives JSON via stdin: `{"query": "src/comp"}`
Output: newline-separated file paths (max 15)

## Plugin Configuration

```json
{
  "enabledPlugins": {
    "formatter@acme-tools": true,
    "deployer@acme-tools": true
  },
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": "github",
      "repo": "acme-corp/claude-plugins"
    }
  },
  "strictKnownMarketplaces": [
    {"source": "github", "repo": "approved/plugins"}
  ]
}
```

## Environment Variables Reference

### Model Configuration

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_MODEL` | Override model selection |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Model for `opus` alias |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Model for `sonnet` alias |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Model for `haiku` alias |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents |

### API Configuration

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key (X-Api-Key header) |
| `ANTHROPIC_AUTH_TOKEN` | Authorization header value |
| `ANTHROPIC_BASE_URL` | Custom API endpoint |
| `ANTHROPIC_CUSTOM_HEADERS` | Additional headers (Name: Value format) |

### Provider Selection

| Variable | Description |
|----------|-------------|
| `CLAUDE_CODE_USE_BEDROCK` | Use AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI |
| `CLAUDE_CODE_USE_FOUNDRY` | Use Microsoft Foundry |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | Skip AWS auth (for gateways) |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | Skip Google auth (for gateways) |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | Skip Azure auth (for gateways) |

### Behavior Configuration

| Variable | Description |
|----------|-------------|
| `MAX_THINKING_TOKENS` | Extended thinking token budget |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Max output tokens per request |
| `BASH_DEFAULT_TIMEOUT_MS` | Default bash timeout |
| `BASH_MAX_TIMEOUT_MS` | Maximum allowed bash timeout |
| `BASH_MAX_OUTPUT_LENGTH` | Max chars before truncation |
| `MCP_TIMEOUT` | MCP server startup timeout (ms) |
| `MCP_TOOL_TIMEOUT` | MCP tool execution timeout (ms) |
| `MAX_MCP_OUTPUT_TOKENS` | Max MCP response tokens (default: 25000) |

### Feature Toggles

| Variable | Description |
|----------|-------------|
| `DISABLE_PROMPT_CACHING` | Disable all prompt caching |
| `DISABLE_PROMPT_CACHING_HAIKU` | Disable Haiku caching |
| `DISABLE_PROMPT_CACHING_SONNET` | Disable Sonnet caching |
| `DISABLE_PROMPT_CACHING_OPUS` | Disable Opus caching |
| `DISABLE_AUTOUPDATER` | Disable auto-updates |
| `DISABLE_TELEMETRY` | Disable Statsig telemetry |
| `DISABLE_ERROR_REPORTING` | Disable Sentry reporting |
| `DISABLE_BUG_COMMAND` | Disable /bug command |
| `DISABLE_COST_WARNINGS` | Disable cost warnings |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable all non-essential traffic |

### Paths and Proxies

| Variable | Description |
|----------|-------------|
| `CLAUDE_CONFIG_DIR` | Custom config directory |
| `HTTP_PROXY` | HTTP proxy server |
| `HTTPS_PROXY` | HTTPS proxy server |
| `NO_PROXY` | Domains to bypass proxy |
| `USE_BUILTIN_RIPGREP` | Set `0` to use system ripgrep |

## Settings Precedence (Highest to Lowest)

1. **Managed settings** (Enterprise remote)
2. **File-based managed settings** (`managed-settings.json`)
3. **Command line arguments**
4. **Local project settings** (`.claude/settings.local.json`)
5. **Shared project settings** (`.claude/settings.json`)
6. **User settings** (`~/.claude/settings.json`)

## Tools Available to Claude

| Tool | Description | Permission Required |
|------|-------------|---------------------|
| AskUserQuestion | Multiple choice questions | No |
| Bash | Execute shell commands | Yes |
| BashOutput | Get background shell output | No |
| Edit | Targeted file edits | Yes |
| ExitPlanMode | Exit planning mode | Yes |
| Glob | Pattern-based file finding | No |
| Grep | Content pattern search | No |
| KillShell | Kill background shell | No |
| NotebookEdit | Jupyter notebook editing | Yes |
| Read | File reading | No |
| Skill | Execute skill | Yes |
| SlashCommand | Custom slash commands | Yes |
| Task | Sub-agent tasks | No |
| TodoWrite | Task list management | No |
| WebFetch | URL content fetching | Yes |
| WebSearch | Domain-filtered search | Yes |
| Write | File creation/overwrite | Yes |
