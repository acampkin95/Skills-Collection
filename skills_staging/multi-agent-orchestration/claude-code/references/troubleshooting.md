# Claude Code Troubleshooting

## Installation Issues

### Native Installation (Recommended)

Bypass npm issues entirely:

```bash
# macOS/Linux/WSL - Stable
curl -fsSL https://claude.ai/install.sh | bash

# Latest version
curl -fsSL https://claude.ai/install.sh | bash -s latest

# Specific version
curl -fsSL https://claude.ai/install.sh | bash -s 1.0.58

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

### WSL-Specific Issues

**OS/platform detection:**
```bash
npm config set os linux
npm install -g @anthropic-ai/claude-code --force --no-os-check
```

**Node not found (using Windows Node in WSL):**
```bash
# Check if using Windows paths
which npm  # Should NOT start with /mnt/c/
which node

# Fix: Install Linux Node via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.nvm/nvm.sh
nvm install --lts
```

**nvm version conflicts:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

### Permission/PATH Issues (Linux/Mac)

```bash
# Fix npm global prefix
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
# Add to shell profile to persist
```

## Authentication Issues

**General auth reset:**
```bash
/logout
rm -rf ~/.config/claude-code/auth.json
claude  # Re-authenticate
```

**OAuth stuck:**
- Clear browser cookies for claude.ai
- Try incognito/private browsing
- Check firewall isn't blocking OAuth callback

## Configuration Reset

**Complete reset:**
```bash
# Remove all user settings and state
rm ~/.claude.json
rm -rf ~/.claude/

# Remove project settings
rm -rf .claude/
rm .mcp.json
```

**Reset specific components:**
```bash
# Just MCP project approvals
claude mcp reset-project-choices

# Just authentication
rm -rf ~/.config/claude-code/auth.json
```

## Performance Issues

### High CPU/Memory

1. Use `/compact` regularly to reduce context
2. Close and restart between major tasks
3. Add build directories to `.gitignore`:
   ```
   node_modules/
   dist/
   build/
   .next/
   ```

### Command Hangs/Freezes

1. Press `Ctrl+C` to cancel
2. If unresponsive, close terminal and restart
3. Check for infinite loops in any hooks

### Slow Search Results

**Install system ripgrep:**
```bash
# macOS
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Windows
winget install BurntSushi.ripgrep.MSVC
```

**Use system ripgrep:**
```bash
export USE_BUILTIN_RIPGREP=0
```

**WSL cross-filesystem penalty:**
- Move project to Linux filesystem (`/home/`)
- Or use native Windows Claude Code instead

## IDE Integration Issues

### JetBrains Not Detected (WSL2)

**Option 1: Firewall rule (recommended)**
```powershell
# PowerShell as Admin
$wslIp = wsl hostname -I
New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" `
  -Direction Inbound -Protocol TCP -Action Allow `
  -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16
```

**Option 2: Mirrored networking**
Add to `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
networkingMode=mirrored
```
Then: `wsl --shutdown`

### Escape Key Not Working (JetBrains)

1. Settings → Tools → Terminal
2. Uncheck "Move focus to the editor with Escape"
   OR
3. Configure terminal keybindings → delete "Switch focus to Editor"

## MCP Troubleshooting

### Server Not Loading

```bash
# Test server directly
npx -y <package-name> --version

# Check config
claude mcp get <server-name>

# Increase timeout
MCP_TIMEOUT=30000 claude

# Check logs
/mcp  # In Claude Code
```

### Connection Closed (Windows)

Windows requires `cmd /c` wrapper for npx:
```bash
claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
```

### Authentication Failed

```bash
# Clear and re-authenticate
/mcp
# Select server → Clear authentication
# Then re-authenticate
```

### Output Too Large

```bash
# Increase limit (default 25000)
export MAX_MCP_OUTPUT_TOKENS=50000
```

## Model/Provider Issues

### Using Alternative Providers

**Via LLM Gateway:**
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://gateway.example.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your-key"
  }
}
```

**Disable experimental betas (for third-party providers):**
```bash
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
```

### Bedrock/Vertex/Foundry

```bash
# AWS Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# Google Vertex
export CLAUDE_CODE_USE_VERTEX=1

# Microsoft Foundry
export CLAUDE_CODE_USE_FOUNDRY=1

# Skip provider auth (for gateways)
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1
export CLAUDE_CODE_SKIP_FOUNDRY_AUTH=1
```

### Extended Thinking Issues

```bash
# Set thinking token budget
export MAX_THINKING_TOKENS=10000
```

Or in settings.json:
```json
{
  "alwaysThinkingEnabled": true
}
```

## Bash Tool Issues

### Environment Variables Not Persisting

Env vars set in one Bash command don't persist to next. Solutions:

**Option 1: Activate before starting**
```bash
conda activate myenv
claude
```

**Option 2: Use CLAUDE_ENV_FILE**
```bash
export CLAUDE_ENV_FILE=/path/to/env-setup.sh
claude
```

**Option 3: SessionStart hook**
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "echo 'conda activate myenv' >> \"$CLAUDE_ENV_FILE\""
      }]
    }]
  }
}
```

### Maintain Working Directory

```bash
export CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=1
```

## Markdown Formatting Issues

### Missing Language Tags

Ask Claude: "Add appropriate language tags to all code blocks"

Or use post-processing hooks:
```json
{
  "hooks": {
    "PostToolUse": {
      "Edit": "your-markdown-fixer.sh"
    }
  }
}
```

## Diagnostic Commands

```bash
# Check installation health
claude doctor

# In Claude Code:
/status          # Model and account info
/config          # Open settings
/mcp             # MCP server status
/compact         # Reduce context size
/bug             # Report issue to Anthropic
```

## Getting Help

1. Run `/bug` in Claude Code to report issues
2. Check [GitHub issues](https://github.com/anthropics/claude-code)
3. Run `claude doctor` for health check
4. Ask Claude about its capabilities (has built-in docs access)
