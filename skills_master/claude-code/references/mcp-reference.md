# MCP Server Reference

## Adding MCP Servers

### HTTP Transport (Recommended)

```bash
# Basic
claude mcp add --transport http <n> <url>

# With authentication
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"

# With scope
claude mcp add --transport http notion --scope user https://mcp.notion.com/mcp
```

### SSE Transport (Deprecated)

```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

### Stdio Transport (Local Servers)

```bash
# Basic
claude mcp add --transport stdio <n> -- <command> [args...]

# With environment variables
claude mcp add --transport stdio airtable \
  --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server

# Windows requires cmd wrapper
claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
```

**Note:** The `--` separates Claude CLI flags from the server command.

## MCP Scopes

| Scope | Location | Sharing |
|-------|----------|---------|
| `local` (default) | `~/.claude.json` per project | Private, current project |
| `project` | `.mcp.json` | Team-shared via git |
| `user` | `~/.claude.json` global | Private, all projects |

## Management Commands

```bash
claude mcp list                    # List all servers
claude mcp get <n>              # Server details
claude mcp remove <n>           # Remove server
claude mcp reset-project-choices   # Reset .mcp.json approvals
claude mcp add-from-claude-desktop # Import from Claude Desktop
claude mcp add-json <n> '<json>'  # Add from JSON config
```

## JSON Configuration Format

### In settings.json

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### In .mcp.json (Project Scope)

```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DB_DSN}"],
      "env": {}
    },
    "api": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

### Environment Variable Expansion

Supported in `command`, `args`, `env`, `url`, `headers`:
- `${VAR}` - Required variable
- `${VAR:-default}` - With default value

## Popular MCP Servers

### First-Party Remote Servers

| Server | Command |
|--------|---------|
| Notion | `claude mcp add --transport http notion https://mcp.notion.com/mcp` |
| Linear | `claude mcp add --transport http linear https://mcp.linear.app/mcp` |
| Figma | `claude mcp add --transport http figma https://mcp.figma.com/mcp` |
| GitHub | `claude mcp add --transport http github https://api.githubcopilot.com/mcp/` |
| Sentry | `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp` |
| Stripe | `claude mcp add --transport http stripe https://mcp.stripe.com` |
| Netlify | `claude mcp add --transport http netlify https://netlify-mcp.netlify.app/mcp` |
| Vercel | `claude mcp add --transport http vercel https://mcp.vercel.com` |
| Atlassian | `claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse` |
| Asana | `claude mcp add --transport sse asana https://mcp.asana.com/sse` |

### Common Local Servers

```bash
# Filesystem access
claude mcp add --transport stdio fs -- npx -y @modelcontextprotocol/server-filesystem /path/to/dir

# PostgreSQL
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "postgresql://user:pass@host:5432/db"

# Git operations
claude mcp add --transport stdio git -- npx -y @modelcontextprotocol/server-git

# Memory/knowledge base
claude mcp add --transport stdio memory -- npx -y @modelcontextprotocol/server-memory
```

## OAuth Authentication

For remote servers requiring OAuth:

1. Add the server
2. Run `/mcp` in Claude Code
3. Select "Authenticate" for the server
4. Complete browser OAuth flow

Tokens are stored securely and refreshed automatically.

## Using Claude Code as MCP Server

```bash
claude mcp serve
```

Claude Desktop configuration:
```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "/full/path/to/claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

## MCP Resources

Reference resources with `@` mentions:
```
@server:protocol://resource/path
@github:issue://123
@postgres:schema://users
```

## MCP Prompts

Execute as slash commands:
```
/mcp__servername__promptname
/mcp__github__pr_review 456
```

## Output Limits

- Warning threshold: 10,000 tokens
- Default max: 25,000 tokens
- Configure with `MAX_MCP_OUTPUT_TOKENS` environment variable

## Plugin-Provided MCP Servers

Plugins can bundle MCP servers in `.mcp.json` at plugin root or inline in `plugin.json`:

```json
{
  "name": "my-plugin",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

## Enterprise MCP Configuration

### Option 1: Exclusive Control

Deploy `managed-mcp.json` to system directory:
- macOS: `/Library/Application Support/ClaudeCode/`
- Linux/WSL: `/etc/claude-code/`
- Windows: `C:\Program Files\ClaudeCode\`

### Option 2: Policy-Based Control

In `managed-settings.json`:

```json
{
  "allowedMcpServers": [
    {"serverName": "github"},
    {"serverCommand": ["npx", "-y", "approved-package"]},
    {"serverUrl": "https://mcp.company.com/*"}
  ],
  "deniedMcpServers": [
    {"serverName": "dangerous-server"},
    {"serverUrl": "https://*.untrusted.com/*"}
  ]
}
```

**Restriction types:**
- `serverName` - Match configured name
- `serverCommand` - Exact command match (for stdio)
- `serverUrl` - URL pattern with wildcards (for remote)

## Troubleshooting MCP

**Server not starting:**
```bash
# Test package directly
npx -y <package-name> --version

# Check configuration
claude mcp get <n>

# Increase timeout
MCP_TIMEOUT=30000 claude
```

**Connection issues:**
- Verify URL is accessible
- Check authentication headers
- Review firewall/proxy settings

**Output too large:**
```bash
export MAX_MCP_OUTPUT_TOKENS=50000
```
