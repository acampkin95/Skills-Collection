# Skills Fundamentals

## What is a Skill?

A skill is a folder containing:
- **SKILL.md** (required): Instructions in Markdown with YAML frontmatter
- **scripts/** (optional): Executable code (Python, Bash, etc.)
- **references/** (optional): Documentation loaded as needed
- **assets/** (optional): Templates, fonts, icons used in output

## File Structure

```
your-skill-name/
├── SKILL.md           # Required - main skill file
├── scripts/           # Optional - executable code
├── references/        # Optional - documentation
└── assets/            # Optional - templates
```

## Critical Rules

- **SKILL.md naming**: Must be exactly `SKILL.md` (case-sensitive)
- **Folder naming**: Use kebab-case (e.g., `notion-project-setup`)
- **No README.md**: All documentation goes in SKILL.md or references/

## Minimal YAML Frontmatter

```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

## Field Requirements

**name**: kebab-case, max 64 chars, no "claude" or "anthropic"

**description**: 
- Include WHAT + WHEN
- Under 1024 characters
- No XML tags (< >)
- Include trigger phrases users actually say
- Mention file types if relevant

**Optional fields**:
- `license`: MIT, Apache-2.0
- `compatibility`: Environment requirements
- `metadata`: Custom key-value pairs (author, version, mcp-server)
