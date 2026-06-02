# Skills Repository

**Location:** `/Users/alex/Projects/Infra/Skills_Repo`  
**Purpose:** Central production and development hub for agent skills  
**Agents:** Claude Code, Codex, OpenCode, Pi  
**Governance:** Follows project AGENTS.md and Infra workspace rules

---

## Quick Start

### For Claude Code Users

```bash
# Option 1: Symlink to master skills (recommended)
ln -s /Users/alex/Projects/Infra/Skills_Repo/skills_master \
      ~/.claude/skills

# Option 2: Copy skills (if symlink not available)
cp -r /Users/alex/Projects/Infra/Skills_Repo/skills_master/* \
      ~/.claude/skills/
```

Then in Claude Code: **Command Palette → Reload Skills**

### For Skill Developers

```bash
# Create new skill in development
mkdir skills_devtesting/my-new-skill
cd skills_devtesting/my-new-skill

# Create SKILL.md with:
cat > SKILL.md << 'EOF'
---
name: my-new-skill
description: What this skill does and when to use it.
---
# My New Skill
## Instructions
[Your guidance here]
EOF

# Validate and promote through pipeline:
# 1. Test locally in Claude Code
# 2. Validate: python Scripts/validate-skill-upload.py my-new-skill
# 3. Move to staging: cp -r skills_devtesting/my-new-skill skills_staging/
# 4. Promote: python Scripts/promote-skill-production.py my-new-skill
```

---

## Folder Structure

```
skills_master/          ← PRODUCTION (aliased as 'skills')
skills_staging/         ← Pre-production validation
skills_devtesting/      ← Development & testing
skills_conversions/     ← Agent-specific adaptations
Packaged/              ← Vendor/third-party skills (read-only)
.archive/              ← Deprecated skills
Plans/                 ← Roadmap & planning
Scripts/               ← Validation & management utilities
```

**See `agents.md` for detailed folder descriptions and purposes.**

---

## Documentation

| Document | Purpose |
|----------|---------|
| **agents.md** | Complete folder structure, lifecycle, validation process, best practices |
| **claude.md** | Claude Code specific guidance, setup, skill design, troubleshooting |
| **Skils-Guidance-Readme.md** | Complete skill authoring guide (16 sections, comprehensive reference) |
| **CHANGELOG.md** | Change history and promotions |
| **README.md** | This file - quick reference |

---

## Skill Lifecycle

### Development → Production Pipeline

```
idea
  ↓
Create in skills_devtesting/
  ↓
Test locally in Claude Code
  ↓
python Scripts/validate-skill-upload.py my-skill
  ↓
Move to skills_staging/
  ↓
Test on target agents (claude, codex, pi, opencode)
  ↓
python Scripts/promote-skill-production.py my-skill
  ↓
In skills_master/ (PRODUCTION) ✅
  ↓
Minor updates → back to staging
  ↓
Major changes → deprecated, archived
```

---

## Key Scripts

All scripts run from the repository root: `/Users/alex/Projects/Infra/Skills_Repo/`

### validate-skill-upload.py
Validates skill before moving to staging.

```bash
# Validate single skill
python Scripts/validate-skill-upload.py my-skill-name

# Validate all in devtesting
python Scripts/validate-skill-upload.py all

# Verbose output
python Scripts/validate-skill-upload.py my-skill-name --verbose
```

**Checks:**
- SKILL.md exists and is parseable
- YAML frontmatter valid
- Name/description requirements
- No conflicts with existing skills
- File references valid

---

### promote-skill-production.py
Promotes validated skill from staging to master.

```bash
# Dry run (validation only)
python Scripts/promote-skill-production.py my-skill --dry-run

# Promote to production
python Scripts/promote-skill-production.py my-skill

# With agent-specific copies
python Scripts/promote-skill-production.py my-skill --auto-conversions
```

**Actions:**
- Validates metadata
- Backs up existing skill
- Copies to master
- Updates CHANGELOG.md
- Updates INDEX.md
- Creates agent-specific variants (optional)

---

## Common Tasks

### Add a New Skill

```bash
# 1. Create in devtesting
mkdir skills_devtesting/my-skill-name
cat > skills_devtesting/my-skill-name/SKILL.md << 'EOF'
---
name: my-skill-name
description: What it does and when to use it.
---
# My Skill Name
## Instructions
...
EOF

# 2. Test in Claude Code
cp -r skills_devtesting/my-skill-name ~/.claude/skills/my-skill-name-dev
# Test in Claude Code IDE...

# 3. Validate & move to staging
python Scripts/validate-skill-upload.py my-skill-name
cp -r skills_devtesting/my-skill-name skills_staging/

# 4. Promote to master
python Scripts/promote-skill-production.py my-skill-name
```

---

### Update an Existing Skill

```bash
# For minor fixes/updates in master:
vim skills_master/my-skill/SKILL.md
# Changes are live in production

# For significant changes:
# 1. Copy to staging
cp -r skills_master/my-skill skills_staging/my-skill-v2
# 2. Make changes and test
# 3. Promote as new version
python Scripts/promote-skill-production.py my-skill-v2
```

---

### Test Skill on Multiple Agents

```bash
# Copy to each agent's skill directory
cp -r skills_master/my-skill ~/.claude/skills/
cp -r skills_master/my-skill skills_conversions/codex/
cp -r skills_master/my-skill ~/.pi/agent/skills/

# Test in each agent environment
# Check that skill loads and functions correctly
```

---

## Skill Metadata Requirements

Every skill must have a valid `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name
description: What this skill does and when to use it
---
# Skill Name
[Your markdown content]
```

**Name Rules:**
- Lowercase letters, numbers, hyphens only
- 3-64 characters
- No "claude" or "anthropic"
- No XML tags
- Gerund form preferred: `processing-pdfs`, `analyzing-spreadsheets`

**Description Rules:**
- Max 1024 characters
- Written in third person
- Include both what + when to use
- No XML tags

**Good Example:**
```yaml
description: Processes Excel spreadsheets, creates pivot tables, generates charts. Use when analyzing .xlsx files or spreadsheet data.
```

---

## Agent Compatibility

| Agent | Status | Location | Network | Notes |
|-------|--------|----------|---------|-------|
| **Claude Code** | ✅ Full | `~/.claude/skills/` | Full | Primary use case |
| **Pi** | ✅ Full | `~/.pi/agent/skills/` | Full | Supports subagents |
| **Codex** | ✅ Full | `skills_conversions/codex/` | Full | May need variants |
| **OpenCode** | ✅ Full | `skills_conversions/opencode/` | Full | May need variants |
| **Claude API** | ⚠️ Limited | Upload via API | No network | Different distribution |

---

## Best Practices

### Skill Design

✅ **Do:**
- Keep SKILL.md under 300 lines
- Use progressive disclosure (reference additional files)
- Write in third person
- Include concrete examples
- Document error handling
- Test on all target agents

❌ **Don't:**
- Over-explain basic concepts
- Create deeply nested file references
- Use first/second person in descriptions
- Assume network access
- Leave skills untested

### Naming

✅ **Good:**
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`

❌ **Avoid:**
- `helper`, `utils`, `tools`
- `my-skill`, `test123`
- `claude-helper`, `anthropic-skill`

---

## Governance

- **Workspace:** `/Users/alex/Projects/Infra`
- **Project Law:** `/Users/alex/Projects/AGENTS.md`
- **Workspace Law:** `/Users/alex/Projects/Infra/AGENTS.md`
- **Changes:** Log in CHANGELOG.md (this directory) and project CHANGELOG.md

---

## Support & Reference

- **Detailed folder structure & lifecycle:** See `agents.md`
- **Claude Code specific:** See `claude.md`
- **Complete authoring guide:** See `Skils-Guidance-Readme.md`
- **Repository scripts:** `Scripts/` directory with `--help` flag
- **Skill examples:** `skills_master/` (production ready)

---

## Key Contacts & Escalation

**For questions about:**
- **Skill authoring:** See `Skils-Guidance-Readme.md` sections 1-10
- **Claude Code integration:** See `claude.md`
- **Validation errors:** Run scripts with `--help` and check inline docs
- **Governance:** See `/Users/alex/Projects/AGENTS.md`
- **Workspace:** See `/Users/alex/Projects/Infra/AGENTS.md`

---

## Quick Links

- **Master Skills:** `skills_master/`
- **Development:** `skills_devtesting/`
- **Staging:** `skills_staging/`
- **Scripts:** `Scripts/`
- **Full Documentation:** `agents.md` (comprehensive reference)
