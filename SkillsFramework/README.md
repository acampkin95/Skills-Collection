# SkillsFramework Hub

Comprehensive infrastructure for building, validating, packaging, and managing Claude Code skills. This is the central repository for all skill development tooling, templates, validators, and conversion utilities.

## Directory Structure

```
SkillsFramework/
├── skill-template/           # Master skill template with comprehensive guides
│   ├── SKILL.md             # Complete skill architecture guide
│   └── references/          # 5 detailed reference guides
│
├── validators/              # Skill validation and verification tools
│   ├── validate-skill-upload.py      # Check skill structure and frontmatter
│   └── verify-compatibility.py       # Verify skill compatibility
│
├── scripts/                 # Utility scripts for skill management
│   ├── package.sh          # Package skills for distribution
│   └── sync.sh             # Sync skills across environments
│
├── tools/                   # Advanced skill management tools
│   ├── promote-skill-production.py   # Promote skills through dev→staging→prod
│   └── generate-skill-index.py       # Generate skill index and metadata
│
├── conversion/              # Skill format conversion utilities
│   └── [conversion tools]   # Convert between skill formats
│
├── packaging/               # Skill packaging and distribution tools
│   └── [packaging tools]    # Create distributable skill packages
│
└── docs/                    # Additional documentation
    └── [implementation guides]
```

## Quick Start

### 1. Use the Skill Template

Start with the proven template in `skill-template/`:

```bash
cp -r SkillsFramework/skill-template/ /path/to/new-skill
cd /path/to/new-skill
# Edit SKILL.md and organize your skill
```

The template includes:
- Complete SKILL.md with best practices
- 5 reference guides covering all aspects
- Progressive disclosure patterns
- Token optimization guidance

### 2. Validate Your Skill

Before uploading, validate with:

```bash
python SkillsFramework/validators/validate-skill-upload.py my-skill-name

# Check compatibility
python SkillsFramework/validators/verify-compatibility.py my-skill-name
```

Validators check:
- YAML frontmatter structure
- Folder naming conventions
- Required fields and content length
- File structure completeness
- Common anti-patterns

### 3. Promote Through Stages

Development → Staging → Production

```bash
# Move to staging after devtesting
python SkillsFramework/tools/promote-skill-production.py my-skill --stage staging

# After staging validation, promote to production
python SkillsFramework/tools/promote-skill-production.py my-skill --stage master

# Preview before promoting
python SkillsFramework/tools/promote-skill-production.py my-skill --dry-run
```

### 4. Package for Distribution

```bash
# Package skill as distributable
bash SkillsFramework/scripts/package.sh my-skill-name

# Output: my-skill-name.zip ready for GitHub or distribution
```

## Skill Development Workflow

### Phase 1: Development (skills_devtesting)

1. Copy template: `cp -r SkillsFramework/skill-template/ skills_devtesting/my-skill`
2. Edit SKILL.md with your use cases
3. Add references, scripts, assets as needed
4. Test triggering in Claude Code
5. Iterate based on observation

### Phase 2: Validation (Before Staging)

1. Run validators:
   ```bash
   python SkillsFramework/validators/validate-skill-upload.py my-skill
   python SkillsFramework/validators/verify-compatibility.py my-skill
   ```
2. Fix any issues
3. Test final version in Claude Code

### Phase 3: Staging (skills_staging)

1. Promote to staging:
   ```bash
   python SkillsFramework/tools/promote-skill-production.py my-skill --stage staging
   ```
2. Test with broader audience
3. Collect feedback
4. Iterate if needed

### Phase 4: Production (skills_master)

1. Final validation:
   ```bash
   python SkillsFramework/tools/promote-skill-production.py my-skill --dry-run
   ```
2. Promote to master:
   ```bash
   python SkillsFramework/tools/promote-skill-production.py my-skill --stage master
   ```
3. Generate index:
   ```bash
   python SkillsFramework/tools/generate-skill-index.py
   ```
4. Package for distribution:
   ```bash
   bash SkillsFramework/scripts/package.sh my-skill
   ```

## Core Components

### Skill Template (skill-template/)

**Main file:** SKILL.md
- Complete architectural guide
- YAML frontmatter patterns
- Progressive disclosure patterns
- Script bundling guidance
- Token optimization techniques
- Validation checklists
- Anti-patterns and troubleshooting

**Reference guides:**
1. **01-fundamentals.md** — File structure, naming, requirements
2. **02-planning-design.md** — Use cases, success criteria, categories
3. **03-best-practices.md** — Writing instructions, progressive disclosure
4. **04-patterns.md** — Sequential, multi-MCP, iterative patterns
5. **05-token-optimization.md** — Cost reduction, leaf skills, validation

### Validators (validators/)

**validate-skill-upload.py**
- Check YAML frontmatter syntax
- Verify folder name matches `name` field
- Validate description length and content
- Detect missing required sections
- Flag known anti-patterns (mega-skills, vague descriptions)
- Verify reference file paths

**verify-compatibility.py**
- Check environmental requirements
- Verify MCP server compatibility
- Test script dependencies
- Validate asset references

### Tools (tools/)

**promote-skill-production.py**
- Move skills through dev→staging→master stages
- Backup previous versions
- Update metadata
- Generate promotion reports
- Support dry-run mode for safety

**generate-skill-index.py**
- Create skill index from frontmatter
- Generate metadata.json
- Build searchable skill catalog
- Create GitHub Pages index

### Scripts (scripts/)

**package.sh**
- Zip skill for distribution
- Include only production files
- Exclude development and test files
- Create release-ready packages

**sync.sh**
- Synchronize skills across environments
- Backup before sync
- Verify integrity after sync
- Support bidirectional sync

## Best Practices Encoded

The SkillsFramework embeds Anthropic's official guidance and community best practices:

✅ **Progressive Disclosure**
- Frontmatter for routing
- SKILL.md for core instructions
- References for detailed knowledge

✅ **Composability**
- Leaf skills (single responsibility)
- Coordinator skills for orchestration
- Domain families (related skills)

✅ **Token Efficiency**
- Frontmatter under 150 chars
- SKILL.md under 500 lines
- Scripts for deterministic logic
- References for on-demand loading

✅ **Validation**
- Static validation before upload
- Behavioral testing during development
- A/B comparison with baseline
- Regression detection

✅ **Lifecycle Management**
- Clear stage progression
- Version tracking
- Rollback capability
- Distribution packaging

## Examples and Templates

The `skill-template/` directory contains:

**SKILL.md Sections:**
- Architecture overview
- Quick start patterns
- YAML frontmatter guide
- Progressive disclosure patterns
- Script bundling guide
- Reference file organization
- Asset management
- Validation checklist
- Anti-pattern catalog
- Troubleshooting guide

**Reference Files:**
- Complete fundamentals guide
- Planning and design framework
- Best practices for instructions
- 5 common workflow patterns
- Token optimization strategies
- Leaf skill design
- Validation approaches

## Integration with Skill Stages

```
skills_devtesting/         Development
       ↓
   (validate)
       ↓
skills_staging/            Testing & Feedback
       ↓
   (validate)
       ↓
skills_master/             Production Ready
       ↓
   (package)
       ↓
GitHub Releases            Public Distribution
```

## Automation

All tools support automation:

```bash
# Validate all skills in devtesting
for skill in skills_devtesting/*/; do
  python SkillsFramework/validators/validate-skill-upload.py $(basename $skill)
done

# Batch promote to staging
python SkillsFramework/tools/promote-skill-production.py --batch --stage staging

# Generate index after updates
python SkillsFramework/tools/generate-skill-index.py
```

## Contributing New Tools

To add a new tool to SkillsFramework:

1. **Validators** - Add to `validators/` for pre-upload checks
2. **Scripts** - Add to `scripts/` for operational tasks
3. **Tools** - Add to `tools/` for advanced management
4. **Conversion** - Add to `conversion/` for format transforms
5. **Documentation** - Add to `docs/` with implementation guide

Each tool should:
- Have clear, single responsibility
- Support dry-run mode where applicable
- Provide verbose output and logging
- Include error handling and recovery
- Work in automation pipelines

## Resources

**In this repository:**
- `skill-template/SKILL.md` — Complete skill architecture guide
- `skill-template/references/` — 5 detailed reference guides
- `validators/` — Pre-upload validation tools
- `tools/` — Promotion and indexing tools

**External references:**
- Anthropic's Official Skill Guide
- Claude Code Documentation
- Community Skills Directory

## Support

- **Creating skills:** See `skill-template/SKILL.md`
- **Validation issues:** See `validators/validate-skill-upload.py --help`
- **Promotion errors:** See `tools/promote-skill-production.py --help`
- **Packaging:** See `scripts/package.sh --help`

---

**SkillsFramework is the canonical source for Claude Code skill development, validation, and distribution.**
