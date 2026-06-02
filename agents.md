# Agent Skills Repository - Workspace Structure & Operations

**Location:** `/Users/alex/Projects/Infra/Skills_Repo`  
**Scope:** Production-ready agent skills for Claude Code, Codex, OpenCode, and Pi  
**Governance:** Follows `/Users/alex/Projects/AGENTS.md` and `/Users/alex/Projects/Infra/AGENTS.md`

---

## Table of Contents

1. [Folder Structure](#folder-structure)
2. [Skill Lifecycle](#skill-lifecycle)
3. [Validation & Promotion](#validation--promotion)
4. [Best Practices](#best-practices)
5. [Agent Compatibility](#agent-compatibility)
6. [Reference Index](#reference-index)

---

## Folder Structure

```
Skills_Repo/
├── skills_master/               # PRODUCTION MASTER (aliased as 'skills')
│   ├── [skill-name]/
│   │   ├── SKILL.md            # Main skill definition
│   │   ├── references/         # Optional reference materials
│   │   ├── examples/           # Optional usage examples
│   │   └── scripts/            # Optional executable utilities
│   └── [skill-name]/
│
├── skills_staging/              # PRE-PRODUCTION VALIDATION
│   ├── [skill-name]/           # Updated skills awaiting promotion
│   ├── validation.log          # Validation history
│   └── INDEX.md                # Staging inventory
│
├── skills_devtesting/           # DEVELOPMENT & TESTING
│   ├── [skill-name]/           # New skills in development
│   ├── [agent]/                # Agent-specific variants (early stage)
│   └── validation-notes.md     # Testing observations
│
├── skills_conversions/          # AGENT-SPECIFIC ADAPTATIONS
│   ├── claude/                 # Claude Code specific skills
│   ├── codex/                  # Codex CLI specific skills
│   ├── opencode/               # OpenCode specific skills
│   └── pi/                     # Pi-specific skill variants
│
├── Packaged/                    # Pre-built packaged skills (read-only)
│   └── [vendor]/[skill]/
│
├── .archive/                    # Historical/deprecated skills
│   └── [archived-skill]/
│
├── Plans/                       # Planning & roadmap documents
│   ├── skill-roadmap.md
│   └── quarterly-plan.md
│
├── Scripts/                     # Repository-wide utilities
│   ├── validate-skill-upload.py      # Move devtesting → staging
│   ├── promote-skill-production.py   # Move staging → master
│   ├── verify-compatibility.py       # Check agent compatibility
│   ├── generate-skill-index.py       # Create skill inventory
│   └── cleanup-skills.py             # Cleanup/formatting
│
├── .aistore/                    # AI working directory (git-ignored)
│   ├── research/
│   ├── drafts/
│   └── logs/
│
├── agents.md                    # This file
├── claude.md                    # Claude-specific workspace guidance
├── README.md                    # Workspace overview
├── CHANGELOG.md                 # Change log
└── Skils-Guidance-Readme.md     # Complete authoring guide
```

---

## Folder Purposes & Rules

### `skills_master/` — PRODUCTION SKILLS

**Purpose:** Canonical, production-ready skills used across all agents

**Rules:**
- Only promote through validated staging process
- No experimental or incomplete skills
- Every skill must pass validation script
- Aliases available: `skills`, `skills:production`
- Used by: Claude Code, Codex, OpenCode, Pi (direct symlink or copy)

**Promotion Path:** `skills_staging/` → `skills_master/`  
**Script:** `Scripts/promote-skill-production.py`

**Quality Gate:**
- ✅ Passes `validate-skill-upload.py`
- ✅ All metadata compliant (name, description)
- ✅ No syntax errors in SKILL.md
- ✅ All references correctly structured
- ✅ Tested on target agents

---

### `skills_staging/` — PRE-PRODUCTION VALIDATION

**Purpose:** Recently updated skills or new skills awaiting promotion to master

**Rules:**
- Skills here are nearly production-ready
- Minor amendments and final validation occur here
- Max 30 days residence; move to master or archive after review
- Maintain `INDEX.md` with skill status
- Log all validation attempts in `validation.log`

**Promotion Path:** `skills_devtesting/` → `skills_staging/`  
**Promotion Script:** `Scripts/validate-skill-upload.py`

**Before Promotion to Master:**
- [ ] Run full validation suite
- [ ] Test on all target agents
- [ ] Update CHANGELOG.md
- [ ] Verify no name/description conflicts
- [ ] Check for deprecated dependencies

**Files:**
- `INDEX.md` — Staging skill inventory with status
- `validation.log` — Timestamped validation history

---

### `skills_devtesting/` — EARLY DEVELOPMENT

**Purpose:** New skills in active development or scoping phase

**Rules:**
- No stability guarantee
- For individual contributors and early-stage skill building
- Skills here may change significantly
- Move to staging only after core functionality complete
- Document design decisions in skill's README.md

**Promotion Path:** Ready skills → `skills_staging/`  
**Manual Process:** Copy to staging, update INDEX.md

**Requirements to Promote:**
- [ ] Core SKILL.md complete and functional
- [ ] Name and description finalized
- [ ] At least one working example
- [ ] Design decisions documented (in skill's README.md)

---

### `skills_conversions/` — AGENT-SPECIFIC ADAPTATIONS

**Purpose:** Skills modified or duplicated for specific agent compatibility

**Structure:**
```
skills_conversions/
├── claude/          # Claude Code specific
│   ├── [skill-name]/
│   │   ├── SKILL.md
│   │   ├── claude-specific-notes.md
│   │   └── scripts/
│   └── INDEX.md
├── codex/          # Codex specific
├── opencode/       # OpenCode specific
└── pi/             # Pi-specific
```

**When to Use:**
- Agent lacks native support for a feature (e.g., specific file operations)
- Agent has unique capabilities to expose
- Special handling needed for that agent's environment

**Maintenance:**
- Keep in sync with `skills_master/` base version
- Document divergences clearly in `agent-specific-notes.md`
- Update master → cascade to conversions on each release

---

### `Packaged/` — VENDOR/THIRD-PARTY SKILLS

**Purpose:** Pre-built packaged skills from Anthropic or other vendors (read-only)

**Rules:**
- Do not edit vendor skills
- Use as reference for custom skill design
- Create custom fork in `skills_master/` if modifications needed
- Reference in documentation with original source

**Organization:** `Packaged/[vendor]/[skill-name]/`

---

### `.archive/` — DEPRECATED/HISTORICAL SKILLS

**Purpose:** Keep historical record of deprecated or superseded skills

**Rules:**
- Moved when skills are deprecated or replaced
- Preserved for audit trail and learning
- Never deleted or modified
- Indexed with deprecation reason

**Naming:** Archive with date: `[skill-name]-deprecated-2026-01-15/`

---

### `Plans/` — ROADMAP & PLANNING

**Purpose:** Strategic planning documents for skill development

**Contains:**
- Quarterly skill roadmap
- Development priorities
- Agent compatibility roadmap
- Research and feasibility studies

---

### `Scripts/` — REPOSITORY UTILITIES

Core validation and management scripts. Always run from repo root.

#### **validate-skill-upload.py**
Validates a skill before moving from `skills_devtesting/` to `skills_staging/`

```bash
cd /Users/alex/Projects/Infra/Skills_Repo
python Scripts/validate-skill-upload.py [skill-name] [--dry-run]
```

**Checks:**
- SKILL.md exists and is parseable
- Metadata compliant (name, description)
- No syntax errors
- References are correctly structured
- Scripts are executable

---

#### **promote-skill-production.py**
Promotes a validated skill from `skills_staging/` to `skills_master/`

```bash
python Scripts/promote-skill-production.py [skill-name] [--auto-conversions]
```

**Actions:**
- Validates skill meets all requirements
- Creates backup of replaced skill (if exists)
- Moves to master
- Updates `skills_master/INDEX.md`
- Logs change in CHANGELOG.md
- Optionally creates agent-specific copies

---

#### **verify-compatibility.py**
Tests skill compatibility across target agents

```bash
python Scripts/verify-compatibility.py [skill-name] [--agents claude,codex,pi]
```

**Tests:**
- File access patterns
- Required packages availability
- Script execution compatibility
- Metadata loading

---

#### **generate-skill-index.py**
Generates comprehensive skill inventory

```bash
python Scripts/generate-skill-index.py [--format markdown|json|csv]
```

**Output:**
- Complete skill directory with metadata
- Agent compatibility matrix
- Dependency mapping
- Usage recommendations

---

### `.aistore/` — AI WORKING DIRECTORY

**Purpose:** AI-only working directory for research, drafts, and logs

**Rules:**
- Git-ignored (not committed)
- Auto-cleanup after 7 days
- For sketches, research, intermediate outputs
- Not for permanent work

---

## Skill Lifecycle

```
idea/research
    ↓
create in skills_devtesting/ → test locally
    ↓
run validate-skill-upload.py
    ↓
move to skills_staging/
    ↓
test on target agents (claude, codex, pi, opencode)
    ↓
run promote-skill-production.py
    ↓
in skills_master/ (production)
    ↓
minor updates → back to staging
    ↓
major changes → deprecated, archived
```

---

## Validation & Promotion

### Development → Staging Promotion

**When:** Skill core is functional and ready for broader testing

**Process:**
```bash
# 1. Validate the skill
python Scripts/validate-skill-upload.py my-skill-name

# 2. If validation passes, manually copy to staging
cp -r skills_devtesting/my-skill-name/ skills_staging/

# 3. Update staging INDEX.md
# 4. Document in .aistore/promotion-notes.md
# 5. Request human review if multi-agent skill
```

**Requirements Checklist:**
- [ ] SKILL.md complete and functional
- [ ] Name and description finalized and compliant
- [ ] At least one working example
- [ ] No breaking changes documented
- [ ] README.md exists in skill folder with design notes

---

### Staging → Production Promotion

**When:** Skill tested, validated, and ready for production use

**Process:**
```bash
# 1. Full validation
python Scripts/promote-skill-production.py my-skill-name --dry-run

# 2. If dry-run successful, promote
python Scripts/promote-skill-production.py my-skill-name

# 3. Verify in master
ls skills_master/my-skill-name/
```

**Requirements Checklist:**
- [ ] Passes `validate-skill-upload.py` completely
- [ ] Tested on all target agents (Claude, Codex, Pi, OpenCode)
- [ ] Zero outstanding issues in skill's ISSUES.md (if exists)
- [ ] Metadata has no conflicts with existing skills
- [ ] CHANGELOG.md updated in master
- [ ] No uncommitted changes in skills_staging/

---

### Backward Compatibility

**Rules:**
- Never break existing API in production skills
- Changes to existing skills:
  - Bug fixes: minor version bump
  - Feature additions: minor version bump
  - Breaking changes: new skill version (e.g., `skill-name-v2`)
- Document breaking changes in MIGRATION.md

---

## Best Practices

### Naming Conventions

✅ **Good:**
- Gerund form: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`
- Noun form: `pdf-processor`, `data-analyzer`
- Action form: `process-pdfs`, `validate-json`

❌ **Avoid:**
- Vague names: `helper`, `utils`, `tools`
- Abbreviations without context: `proc`, `mgmt`
- Reserved words: `anthropic-*`, `claude-*`

---

### Description Format

**Rule:** Write in third person, include what + when to use

✅ **Good:**
```yaml
description: Processes Excel spreadsheets, creates pivot tables, and generates charts. Use when analyzing spreadsheet data, Excel files, or tabular datasets.
```

❌ **Bad:**
```yaml
description: I can help with Excel
description: Helps with documents
```

---

### Folder Organization

**For small skills (<200 lines):**
```
skill-name/
├── SKILL.md           # Everything in one file
└── examples.md        # Optional
```

**For medium skills (200-500 lines):**
```
skill-name/
├── SKILL.md           # Core instructions
├── REFERENCE.md       # API/methods
├── EXAMPLES.md        # Code examples
└── scripts/           # Utilities
```

**For large skills (>500 lines):**
```
skill-name/
├── SKILL.md           # Overview & navigation
├── reference/
│   ├── api.md
│   ├── advanced.md
│   └── troubleshooting.md
├── examples/
│   ├── basic.md
│   └── advanced.md
└── scripts/
    ├── helper.py
    └── validate.py
```

---

### Progressive Disclosure

**Principle:** Load only what's needed

**Pattern:** SKILL.md → references → scripts

```markdown
# My Skill

## Quick start
[Essential info, <100 lines]

## Advanced usage
See [REFERENCE.md](REFERENCE.md) for complete API

## Examples
See [EXAMPLES.md](EXAMPLES.md) for code samples

## Troubleshooting
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
```

---

## Agent Compatibility

### Supported Agents

| Agent | Environment | Network | Packages | Skills Location |
|-------|-------------|---------|----------|-----------------|
| **Claude Code** | macOS/Linux | ✅ Full | ✅ Install | `~/.claude/skills/` or `.claude/skills/` |
| **Claude API** | Cloud | ❌ No | ❌ No | Upload via API |
| **Claude.ai** | Cloud | Varies | ✅ npm/PyPI | Account-scoped |
| **Codex** | Local | ✅ Full | ✅ Install | `skills_conversions/codex/` |
| **OpenCode** | Local | ✅ Full | ✅ Install | `skills_conversions/opencode/` |
| **Pi** | Local | ✅ Full | ✅ Install | Uses `~/.pi/agent/skills/` |

### Compatibility Matrix

**Multi-agent compatible skills** (most common):
- Pure Markdown/instructions
- Python scripts with standard libraries
- Bash utilities
- No platform-specific code

**Agent-specific skills** (use `skills_conversions/`):
- Claude Code IDE integrations
- Codex editor plugins
- Pi-specific subagent coordination

---

### Testing on All Agents

**Process before promoting to master:**

```bash
# 1. Claude Code
# Copy to ~/.claude/skills/ and test in IDE

# 2. Pi
# Copy to ~/.pi/agent/skills/ and test in TUI

# 3. Codex (if applicable)
# Copy to skills_conversions/codex/ and test

# 4. Run verification
python Scripts/verify-compatibility.py skill-name --agents all
```

---

## Reference Index

### Skill Categories

#### **Code & Development**
- `processing-code` — Code analysis and transformation
- `git-automation` — Git operations and workflows
- `testing-automation` — Test writing and validation
- `linting-formatting` — Code quality and style

#### **Data & Analytics**
- `spreadsheet-processing` — Excel/CSV operations
- `data-visualization` — Charts and graphs
- `sql-operations` — Database queries
- `statistical-analysis` — Data analysis

#### **Document Processing**
- `pdf-processing` — PDF generation and analysis
- `word-processing` — DOCX creation and editing
- `markdown-conversion` — Format conversion
- `document-templating` — Template-based generation

#### **Infrastructure & DevOps**
- `kubernetes-operations` — K8s management
- `terraform-management` — IaC operations
- `container-management` — Docker/container utilities
- `aws-operations` — AWS SDK wrapper

#### **Content & Creativity**
- `writing-assistance` — Grammar, style, clarity
- `creative-writing` — Narrative, fiction support
- `brand-consistency` — Brand guide enforcement
- `seo-optimization` — SEO best practices

---

## Quick Reference: Adding a New Skill

### Step 1: Scaffold in `skills_devtesting/`

```bash
mkdir skills_devtesting/my-new-skill
cd skills_devtesting/my-new-skill

# Create SKILL.md with:
cat > SKILL.md << 'EOF'
---
name: my-new-skill
description: Brief description of what this does and when to use it.
---
# My New Skill
## Instructions
[Your guidance here]
EOF
```

### Step 2: Develop & Test Locally

- Write SKILL.md with clear instructions
- Add examples and references as needed
- Create scripts in `scripts/` subdirectory if needed

### Step 3: Validate & Move to Staging

```bash
cd /Users/alex/Projects/Infra/Skills_Repo
python Scripts/validate-skill-upload.py my-new-skill

# If validation passes:
cp -r skills_devtesting/my-new-skill/ skills_staging/
```

### Step 4: Test on Target Agents

Test the skill manually with Claude Code, Pi, Codex as needed.

### Step 5: Promote to Master

```bash
python Scripts/promote-skill-production.py my-new-skill
```

### Step 6: Archive or Iterate

- If skill works: done! It's in production.
- If minor fixes needed: go back to step 2, return to staging
- If major rework: keep in devtesting, create version 2

---

## Governance & Change Log

- **Workspace Changes:** Log in `/Users/alex/Projects/CHANGELOG.md`
- **Skills Changes:** Log in `CHANGELOG.md` (this directory)
- **Governance Updates:** Log in `.aiglobalguidance/references/`
- **Agent-specific Changes:** Note in `Scripts/agents-compatibility.md`

---

## Support & Questions

- **Skill Authoring:** See `Skils-Guidance-Readme.md`
- **Agent Integration:** See `claude.md` (Claude Code specific)
- **Governance:** See `/Users/alex/Projects/AGENTS.md`
- **Scripts Help:** `python Scripts/[script].py --help`

---

## References

- **Core Authoring Guide:** `Skils-Guidance-Readme.md`
- **Claude Workspace:** `claude.md`
- **Skill Packaging:** `Packaged/` folder
- **Archived Skills:** `.archive/` folder
- **Planning:** `Plans/` folder
