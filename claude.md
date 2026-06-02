# Claude Code Workspace Guide

**Workspace:** Skills Repository for Claude Code Integration  
**Location:** `/Users/alex/Projects/Infra/Skills_Repo`  
**Related:** See `agents.md` for full repository structure

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Claude Code Skills Loading](#claude-code-skills-loading)
3. [Best Practices for Claude Code](#best-practices-for-claude-code)
4. [Workflow Guide](#workflow-guide)
5. [Skill Design for Claude Code](#skill-design-for-claude-code)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Setup: Enable Skills in Claude Code

**On macOS M4 Pro (Your daily driver):**

1. Open Claude Code Settings → Skills
2. Set skill directory:
   ```
   ~/.claude/skills/
   ```
3. Or use workspace-local skills:
   ```
   .claude/skills/
   ```

**Option A: Symlink to Master (Recommended)**
```bash
# One-time setup: link master skills to Claude
ln -s /Users/alex/Projects/Infra/Skills_Repo/skills_master \
      ~/.claude/skills

# Or workspace-scoped:
cd /Users/alex/Projects/Infra
ln -s ./Skills_Repo/skills_master .claude/skills
```

**Option B: Copy Production Skills (If symlink not supported)**
```bash
# Copy skills to Claude's directory
cp -r /Users/alex/Projects/Infra/Skills_Repo/skills_master/* \
      ~/.claude/skills/
```

### Load Skills in Claude Code

1. Open Claude Code
2. Press `Cmd+K` (command palette)
3. Type "Reload Skills" or restart Claude Code
4. Skills should appear in the Skills sidebar

---

## Claude Code Skills Loading

### How Skills Are Discovered

Claude Code scans for skills in:
1. **Startup:** Loads metadata (name + description) from all `SKILL.md` files
2. **User Request:** When a skill is triggered, Claude reads the full `SKILL.md`
3. **As Needed:** Claude reads additional files (references, examples) on demand

### Three-Tier Loading Model

| Tier | When Loaded | Token Cost | Content |
|------|-------------|------------|---------|
| **Metadata** | Startup | ~50 tokens/skill | Name + description |
| **Instructions** | Triggered | <500 tokens | SKILL.md body |
| **Resources** | On-demand | Minimal | Scripts, examples, references |

### Automatic Discovery

Skills in the configured directory are **automatically discovered** without any registration step. Claude Code:
- Scans `~/.claude/skills/` (or `.claude/skills/`) at startup
- Reads metadata from each skill's `SKILL.md` frontmatter
- Loads full instructions when relevant to your task
- Reads additional files (REFERENCE.md, EXAMPLES.md) as needed

---

## Best Practices for Claude Code

### Skill Organization (Claude-Specific)

**For Claude Code, skills should:**

✅ Use filesystem operations
✅ Leverage bash/shell access
✅ Reference local files and projects
✅ Execute Python/Node.js scripts
✅ Integrate with IDE file tree

❌ Assume network access (may be restricted)
❌ Require external API connections without documentation
❌ Expect specific IDE UI features
❌ Assume Windows paths

### Metadata Requirements

```yaml
---
name: your-skill-name
description: What this does and when Claude should use it. Use when [specific triggers].
---
```

**Name Rules:**
- Lowercase letters, numbers, hyphens only
- Max 64 characters
- No "claude", "anthropic", or XML tags
- Gerund form preferred: `processing-pdfs`, `analyzing-spreadsheets`

**Description Rules:**
- Third person (Claude reads as system instruction)
- Include both what + when to use
- Max 1024 characters
- No XML tags

**Good examples:**
```yaml
description: Processes Excel spreadsheets, creates pivot tables, generates charts. Use when analyzing .xlsx files or spreadsheet data.

description: Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDFs or document operations.

description: Writes clear test cases and validates code behavior. Use when writing unit tests or validating test coverage.
```

---

## Workflow Guide

### Creating a Skill in Claude Code

#### 1. **Design Phase** (in devtesting)

Start in `skills_devtesting/`:

```bash
# Create skill folder
mkdir skills_devtesting/my-skill-name
cd skills_devtesting/my-skill-name

# Create basic SKILL.md
cat > SKILL.md << 'EOF'
---
name: my-skill-name
description: Clear description of what this does and when to use it.
---
# My Skill Name

## Instructions
[Step-by-step guidance]

## Quick Example
[Simple working example]

## Reference
See [REFERENCE.md](REFERENCE.md) for complete API
EOF
```

#### 2. **Test Phase** (in Claude Code)

```bash
# Option A: Link to devtesting directory temporarily
ln -s /Users/alex/Projects/Infra/Skills_Repo/skills_devtesting \
      ~/.claude/skills-dev

# Option B: Copy to skills directory for testing
cp -r skills_devtesting/my-skill-name ~/.claude/skills/my-skill-name-dev
```

**Test the skill:**
1. Open Claude Code
2. Command palette → "Reload Skills"
3. Create a test file in your project
4. Ask Claude: "Use my-skill-name-dev to [your task]"
5. Observe how Claude navigates and uses the skill
6. Note any missing guidance or confusing instructions

#### 3. **Refinement Phase** (iterate in devtesting)

Based on testing observations:
- Simplify unclear sections
- Add missing examples
- Reorganize for better progressive disclosure
- Fix broken references

Re-test in Claude Code after changes.

#### 4. **Validation Phase** (move to staging)

When skill is stable and well-tested:

```bash
cd /Users/alex/Projects/Infra/Skills_Repo

# Validate the skill
python Scripts/validate-skill-upload.py my-skill-name

# If validation passes:
cp -r skills_devtesting/my-skill-name/ skills_staging/

# Update staging INDEX.md with skill metadata
```

#### 5. **Production Phase** (promote to master)

After staging validation:

```bash
# Final validation before promotion
python Scripts/promote-skill-production.py my-skill-name --dry-run

# If dry-run successful:
python Scripts/promote-skill-production.py my-skill-name

# Update Claude's skills directory
ln -s /Users/alex/Projects/Infra/Skills_Repo/skills_master \
      ~/.claude/skills
```

---

## Skill Design for Claude Code

### Principle 1: Trust Claude's Intelligence

Claude already knows most of what it needs. Only document what Claude might not know.

❌ **Over-explain (wastes tokens):**
```markdown
## PDF Processing

PDF files are a common file format that contains text, images, and other
content. When working with PDF files, you may need to extract text, 
read tables, or perform other operations. There are several Python libraries
available for working with PDFs, including pdfplumber, PyPDF2, and others.
For this skill, we recommend pdfplumber because it...
```

✅ **Concise (efficient):**
```markdown
## PDF Processing

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For table extraction, use: `pdf.pages[0].extract_tables()`
```

### Principle 2: Progressive Disclosure

**SKILL.md should contain:**
- Quick start / essential information
- Most common use cases
- References to additional files

**Split into separate files when:**
- SKILL.md exceeds 300 lines
- Different audiences (beginner vs advanced)
- Different use patterns (basic vs expert)

**Example structure:**
```
pdf-processing/
├── SKILL.md           # Quick start + overview
├── REFERENCE.md       # Complete API reference
├── EXAMPLES.md        # Code samples
└── scripts/
    ├── extract.py     # Text extraction utility
    └── fill_form.py   # Form filling utility
```

**In SKILL.md, reference additional files:**
```markdown
## Complete API Reference
See [REFERENCE.md](REFERENCE.md) for all available methods.

## Code Examples
See [EXAMPLES.md](EXAMPLES.md) for common patterns and usage.

## Form Filling
For form-specific operations, see [FORMS.md](FORMS.md).
```

### Principle 3: Appropriate Degrees of Freedom

| Level | Guidance | When |
|-------|----------|------|
| **High** | "Write a clear function that does X" | Multiple valid approaches |
| **Medium** | "Use this template and customize as needed" | Preferred pattern exists |
| **Low** | "Run exactly: `python script.py --flag`" | Operations are fragile |

**Example: High Freedom**
```markdown
## Code Review
Review the provided code for:
- Potential bugs or edge cases
- Performance improvements
- Readability and maintainability
- Security concerns

Provide specific suggestions with examples.
```

**Example: Low Freedom (Specific Operation)**
```markdown
## Form Validation
Run validation before submitting:
```bash
python scripts/validate_form.py --check-required --check-types
```
Only proceed if validation returns exit code 0.
```

### Principle 4: File References (One Level Deep)

✅ **Good (one level):**
```
SKILL.md → REFERENCE.md ✓
SKILL.md → EXAMPLES.md ✓
SKILL.md → scripts/helper.py ✓
```

❌ **Bad (nested):**
```
SKILL.md → advanced.md → details.md ✗
SKILL.md → reference/ → api/ → core.md ✗
```

All files should link directly from SKILL.md.

---

## Skill Writing Checklist for Claude Code

### Content Quality
- [ ] Description is specific (not "helps with documents")
- [ ] Description includes when to use it
- [ ] SKILL.md is under 300 lines
- [ ] Progressive disclosure used (references to other files)
- [ ] Examples are concrete, not abstract
- [ ] No unnecessary explanation of basic concepts
- [ ] Consistent terminology throughout
- [ ] File references are one-level deep from SKILL.md

### Code & Scripts
- [ ] Scripts solve problems (don't punt to Claude)
- [ ] Error handling is explicit
- [ ] Required packages listed and verified available
- [ ] Scripts have clear documentation
- [ ] No Windows-style paths (`scripts\helper.py`)
- [ ] All hardcoded values justified with comments
- [ ] Validation/verification steps for critical operations

### Metadata
- [ ] `name` is max 64 chars, lowercase, hyphenated
- [ ] `name` doesn't contain "claude" or "anthropic"
- [ ] `description` is max 1024 chars
- [ ] `description` is third person
- [ ] `description` specifies both what + when to use

### Testing
- [ ] Tested in Claude Code IDE
- [ ] Tested on both macOS and Linux (if applicable)
- [ ] Tested with Sonnet and Opus models
- [ ] Claude successfully navigates references
- [ ] Examples actually work when copied

---

## Advanced: Executable Scripts

### Writing Scripts for Claude Code

**Goals:**
1. **Solve, don't punt:** Handle errors explicitly
2. **Be clear about intent:** Run vs. read for reference
3. **Validate outputs:** Verify critical operations
4. **Document constants:** Justify all hardcoded values

**Good example:**
```python
#!/usr/bin/env python3
"""Extract structured data from PDF files."""

import sys
import pdfplumber

# Page timeout: PDFs can have complex rendering
# 30 seconds balances reliability vs. speed
PAGE_TIMEOUT = 30

def extract_text(pdf_path, page_num=0):
    """Extract text from a specific page.
    
    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)
    
    Returns:
        Extracted text or empty string if page not found
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num >= len(pdf.pages):
                print(f"Warning: PDF has {len(pdf.pages)} pages, "
                      f"requested page {page_num}")
                return ""
            return pdf.pages[page_num].extract_text() or ""
    except FileNotFoundError:
        print(f"Error: File {pdf_path} not found")
        return ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract.py <pdf_path> [page_num]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    text = extract_text(pdf_path, page_num)
    print(text)
```

### Running Scripts in SKILL.md

**Clear intent:**

```markdown
## Extract PDF text
Run the extraction script:
```bash
python scripts/extract.py my_file.pdf
```

See [scripts/extract.py](scripts/extract.py) for the implementation details.
```

vs.

```markdown
## Extraction Algorithm
The extraction uses pdfplumber's built-in methods. See 
[scripts/extract.py](scripts/extract.py) for reference implementation.
```

---

## Troubleshooting

### Skills Not Loading in Claude Code

**Problem:** Skills don't appear in sidebar

**Solutions:**
1. Check path: `~/.claude/skills/` exists and contains skill folders
2. Verify SKILL.md exists in each skill folder
3. Reload skills: Command palette → "Reload Skills"
4. Restart Claude Code if reload doesn't work
5. Check SKILL.md metadata: must have valid YAML frontmatter

**Debug:**
```bash
# Check skill directory
ls -la ~/.claude/skills/

# Verify SKILL.md exists
ls ~/.claude/skills/*/SKILL.md

# Check for parsing errors
head -20 ~/.claude/skills/my-skill/SKILL.md
```

---

### Claude Doesn't Use a Skill

**Problem:** Skill is loaded but Claude doesn't use it

**Causes:**
1. **Description doesn't match task** — Add trigger words to description
2. **Instructions too verbose** — Claude may miss key guidance in wall of text
3. **Skill scope too narrow** — Description too specific

**Solutions:**

✅ **Better description:**
```yaml
description: Processes Excel spreadsheets, creates pivot tables, generates 
charts. Use when analyzing .xlsx files, spreadsheet data, or working with 
tabular information.
```

❌ **Poor description:**
```yaml
description: Processes Excel
```

---

### Claude Reads Wrong Files

**Problem:** Claude reads REFERENCE.md instead of SKILL.md

**Likely cause:** SKILL.md is too short; Claude seeks more comprehensive guidance

**Solutions:**
1. Expand SKILL.md with more details
2. Make SKILL.md self-contained for common tasks
3. Use REFERENCE.md for edge cases, not core functionality

---

### Validation Fails When Promoting

**Problem:** Skill fails `validate-skill-upload.py`

**Common issues:**
- SKILL.md frontmatter is malformed
- Name contains invalid characters
- Description exceeds 1024 characters
- Referenced files don't exist

**Debugging:**
```bash
# Run validation with verbose output
python Scripts/validate-skill-upload.py my-skill --verbose

# Check SKILL.md frontmatter
head -10 skills_devtesting/my-skill/SKILL.md
```

---

### File References Broken

**Problem:** Claude can't find referenced files

**Rules:**
- All references must be one level deep: `SKILL.md` → `REFERENCE.md` ✓
- Use relative paths: `[REFERENCE.md](REFERENCE.md)` not `/path/to/...`
- Verify files exist before promoting

**Fix:**
```bash
# Check file structure
find skills_devtesting/my-skill -type f

# Verify links are relative
grep -n "](/\|](\.\./\.\./)" skills_devtesting/my-skill/SKILL.md
```

---

## Quick Reference: Common Tasks

### Adding a New Skill

```bash
cd /Users/alex/Projects/Infra/Skills_Repo

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
cp -r skills_devtesting/my-skill-name ~/.claude/skills/

# 3. Validate & move to staging
python Scripts/validate-skill-upload.py my-skill-name
cp -r skills_devtesting/my-skill-name skills_staging/

# 4. Promote to master
python Scripts/promote-skill-production.py my-skill-name
```

### Updating an Existing Skill

```bash
# 1. Make changes in skills_master/my-skill/
vim skills_master/my-skill/SKILL.md

# 2. For non-breaking changes, done!
# (No need to go through staging for minor updates)

# 3. For breaking changes:
# - Move to skills_staging/
# - Test thoroughly
# - Use new version name (e.g., my-skill-v2)
```

### Removing a Skill

```bash
# 1. Move to archive (never delete)
mv skills_master/my-skill/ .archive/my-skill-deprecated-2026-01-15/

# 2. Remove from ~/.claude/skills/
rm -rf ~/.claude/skills/my-skill

# 3. Update CHANGELOG.md
# 4. Update INDEX.md files
```

---

## Integration with Project Workflow

### Using Skills in Your Projects

In any Claude Code session in `/Users/alex/Projects/`:

```
1. Skills automatically load from ~/.claude/skills/
2. In your task, Claude will suggest relevant skills
3. Accept skill recommendations
4. Claude handles skill loading and navigation
5. Skills are context-aware based on your files/task
```

### Linking Skills to Project Root

For project-specific skills, create workspace-scoped directory:

```bash
cd /Users/alex/Projects/MyProject

# Create local skills directory
mkdir .claude
ln -s /Users/alex/Projects/Infra/Skills_Repo/skills_master .claude/skills

# In Claude Code settings, use project-local skills:
# Skills directory: .claude/skills
```

---

## Related Documentation

- **Full Skills Guide:** `Skils-Guidance-Readme.md`
- **Repository Structure:** `agents.md`
- **Validation Scripts:** `Scripts/` directory
- **Project Governance:** `/Users/alex/Projects/AGENTS.md`
- **Infra Workspace:** `/Users/alex/Projects/Infra/AGENTS.md`

---

## Getting Help

- **Skill authoring questions:** See `Skils-Guidance-Readme.md` sections 1-10
- **Claude Code specific:** See `claude.md` (this file)
- **Validation errors:** Run scripts with `--help` flag
- **Governance questions:** See `/Users/alex/Projects/AGENTS.md`
