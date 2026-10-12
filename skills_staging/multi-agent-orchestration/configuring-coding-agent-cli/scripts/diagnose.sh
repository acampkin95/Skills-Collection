#!/bin/bash
# Claude Code Diagnostic Script
# Run this to gather diagnostic information about your Claude Code installation

set -euo pipefail

echo "======================================"
echo "Claude Code Diagnostic Report"
echo "======================================"
echo "Generated: $(date)"
echo ""

# System info
echo "## System Information"
echo "OS: $(uname -s)"
echo "Architecture: $(uname -m)"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS Version: $(sw_vers -productVersion)"
elif [[ -f /etc/os-release ]]; then
    echo "Linux Distribution: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
fi
echo ""

# Check if running in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "## WSL Detected"
    echo "WSL Version: $(wsl.exe --version 2>/dev/null | head -1 || echo 'Unable to determine')"
    echo ""
fi

# Node.js info
echo "## Node.js Environment"
if command -v node &> /dev/null; then
    echo "Node Version: $(node --version)"
    echo "Node Path: $(which node)"
else
    echo "Node: NOT FOUND"
fi

if command -v npm &> /dev/null; then
    echo "npm Version: $(npm --version)"
    echo "npm Path: $(which npm)"
    echo "npm Global Prefix: $(npm config get prefix)"
else
    echo "npm: NOT FOUND"
fi

if command -v npx &> /dev/null; then
    echo "npx Path: $(which npx)"
else
    echo "npx: NOT FOUND"
fi
echo ""

# Claude Code installation
echo "## Claude Code Installation"
if command -v claude &> /dev/null; then
    echo "Claude Path: $(which claude)"
    echo "Claude Version: $(claude --version 2>/dev/null || echo 'Unable to determine')"
else
    echo "Claude: NOT FOUND in PATH"
    # Check common locations
    for loc in ~/.local/bin/claude /usr/local/bin/claude ~/.npm-global/bin/claude; do
        if [[ -f "$loc" ]]; then
            echo "Found at: $loc (not in PATH)"
        fi
    done
fi
echo ""

# Configuration files
echo "## Configuration Files"
config_files=(
    "$HOME/.claude/settings.json"
    "$HOME/.claude.json"
    ".claude/settings.json"
    ".claude/settings.local.json"
    ".mcp.json"
    "CLAUDE.md"
    ".claude/CLAUDE.md"
)

for f in "${config_files[@]}"; do
    if [[ -f "$f" ]]; then
        echo "✓ $f ($(wc -c < "$f") bytes)"
    else
        echo "✗ $f (not found)"
    fi
done
echo ""

# MCP servers
echo "## MCP Server Configuration"
if command -v claude &> /dev/null; then
    echo "Configured MCP servers:"
    claude mcp list 2>/dev/null || echo "Unable to list MCP servers"
else
    echo "Claude not found, cannot list MCP servers"
fi
echo ""

# Environment variables
echo "## Relevant Environment Variables"
env_vars=(
    "ANTHROPIC_API_KEY"
    "ANTHROPIC_AUTH_TOKEN"
    "ANTHROPIC_BASE_URL"
    "ANTHROPIC_MODEL"
    "CLAUDE_CODE_USE_BEDROCK"
    "CLAUDE_CODE_USE_VERTEX"
    "CLAUDE_CODE_USE_FOUNDRY"
    "CLAUDE_CONFIG_DIR"
    "MAX_THINKING_TOKENS"
    "MCP_TIMEOUT"
    "HTTP_PROXY"
    "HTTPS_PROXY"
)

for var in "${env_vars[@]}"; do
    if [[ -n "${!var}" ]]; then
        # Mask sensitive values
        if [[ "$var" == *"KEY"* ]] || [[ "$var" == *"TOKEN"* ]]; then
            echo "$var: [SET - masked]"
        else
            echo "$var: ${!var}"
        fi
    fi
done
echo ""

# ripgrep
echo "## Search Tool (ripgrep)"
if command -v rg &> /dev/null; then
    echo "ripgrep Version: $(rg --version | head -1)"
    echo "ripgrep Path: $(which rg)"
else
    echo "System ripgrep: NOT FOUND"
fi
echo "USE_BUILTIN_RIPGREP: ${USE_BUILTIN_RIPGREP:-not set}"
echo ""

# Network
echo "## Network Check"
if command -v curl &> /dev/null; then
    echo "Testing Anthropic API connectivity..."
    if curl -s --connect-timeout 5 https://api.anthropic.com/v1/messages -o /dev/null -w "%{http_code}" 2>/dev/null | grep -q "401\|403"; then
        echo "✓ Can reach Anthropic API (auth required)"
    else
        echo "? Anthropic API connectivity unclear"
    fi
else
    echo "curl not available for network check"
fi
echo ""

# Disk space
echo "## Disk Space"
if [[ -d "$HOME/.claude" ]]; then
    echo "~/.claude directory: $(du -sh "$HOME/.claude" 2>/dev/null | cut -f1)"
fi
echo ""

echo "======================================"
echo "Diagnostic report complete"
echo "======================================"
