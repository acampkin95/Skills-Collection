---
name: skills-framework-master
description: Master guide for building high-quality Claude Code skills. Teaches skill architecture, YAML frontmatter, progressive disclosure, validation patterns, and token optimization. Use when building, refining, or evaluating Claude skills.
metadata:
  author: Claude Skills Repository
  version: 1.0.0
  category: skill-development
  tags: [skill-building, architecture, best-practices, token-optimization]
---

# Skills Framework Master

Comprehensive framework for designing, building, testing, and optimizing Claude Code skills.

## Quick Start: Skill Architecture

Every skill requires this structure:

```
skill-name/
├── SKILL.md           # Required: YAML frontmatter + core instructions
├── scripts/           # Optional: Deterministic CLIs (Python, Bash)
├── references/        # Optional: Detailed docs, schemas, templates
└── assets/            # Optional: Templates, examples, static files
```

## YAML Frontmatter: The Routing Layer

The frontmatter is loaded into Claude's system prompt and determines when your skill activates.

**Required fields:**
```yaml
---
name: skill-name-in-kebab-case
description: What it does and when to use it. Include specific trigger phrases.
---
```

**Best practices:**
- **Name**: lowercase, hyphens only, max 64 chars, no "claude" or "anthropic"
- **Description**: Include BOTH what + when; specific trigger phrases users say; mention file types if relevant
- **Negative triggers**: Add "Do NOT use for X" to prevent over-triggering

**Good example:**
```yaml
description: Creates sophisticated frontend designs from specifications. Use when user uploads design specs, asks to "build a React component", or provides "UI mockups". Do NOT use for Vue or Svelte projects.
```

## Progressive Disclosure: Three-Level Loading

Keep context lean by loading instructions only when needed:

| Level | When | Content |
|-------|------|---------|
| **1. Frontmatter** | Always | name + description (~50 tokens) |
| **2. SKILL.md body** | When skill triggers | Full instructions + examples (~500 tokens) |
| **3. References** | On-demand | Detailed docs, schemas, templates |

**Implementation pattern:**
- Keep SKILL.md under 500 lines, focused on core workflow
- Move detailed docs to `references/api.md`, `references/schema.md`
- Use explicit instructions: "Before starting, read `references/validation.md`"

## SKILL.md Body: Imperative Instructions

Write instructions in third-person imperative, using clear steps.

**Structure template:**
```markdown
# Skill Name

## Instructions

### Step 1: [First Action]
Clear explanation of what happens and why.

Example:
\`\`\`bash
command --flag value
\`\`\`

Expected output: [describe success]

### Step 2: [Second Action]
...

## Common Workflows

**Scenario 1:** [User request]
1. Do X
2. Do Y
Result: [outcome]

## Troubleshooting

**Error:** [Common error]
**Cause:** [Why it happens]
**Solution:** [How to fix]
```

**Best practices:**
- ✅ Specific: "Run `python scripts/validate.py --file {name}`"
- ❌ Vague: "Validate the data before proceeding"
- Include error handling and recovery steps
- Provide 2-3 concrete examples per major workflow

## Scripts: Deterministic Code Inside Skills

Bundle small Python/Bash scripts for non-trivial logic instead of asking Claude to improvise.

**When to add a script:**
- Parsing or data transformation (regex, JSON parsing)
- Calling internal APIs or databases
- Validation logic
- Complex file operations

**Script best practices:**
```python
#!/usr/bin/env python3
"""Clear one-line description."""

def do_something(input_file):
    """
    Process file.
    
    Args:
        input_file: Path to file
    
    Returns:
        Processed result or None if error
    """
    try:
        # Logic
        return result
    except FileNotFoundError:
        print(f"Error: File {input_file} not found")
        return None
```

- Small, focused CLIs with clear arguments
- Emit JSON or structured output
- Descriptive error messages so Claude can self-correct
- Keep scripts under 100 lines; larger logic belongs in your main codebase

## Reference Files: Organized Documentation

Use `references/` for detailed knowledge that Claude loads on-demand.

**Common reference types:**

```
references/
├── api-guide.md          # API endpoints, parameters, responses
├── error-codes.md        # Error codes + recovery steps
├── schema.md             # Data structures, JSON schema
├── examples.md           # Code samples for common tasks
└── compliance.md         # Rules, constraints, regulations
```

In SKILL.md, explicitly tell Claude when to read:
```markdown
## Before creating a report:
Read `references/schema.md` to understand required fields.
Read `references/error-codes.md` for handling validation failures.
```

## Assets: Templates and Examples

Store concrete templates in `assets/` so Claude copies structured patterns.

```
assets/
├── report-template.md    # Markdown template for reports
├── schema.json          # JSON schema example
└── config-example.yaml  # Configuration template
```

In SKILL.md:
```markdown
## Creating a new report:
Use the template from `assets/report-template.md`.
Replace [PLACEHOLDER] fields with actual data.
```

## Triggering Tests

Verify your skill activates at the right times.

**Test cases:**
```
Should trigger:
- "Help me build a React component"
- "Create a frontend design from specs"
- "Design a Next.js dashboard"

Should NOT trigger:
- "Help me learn JavaScript"
- "Build a Vue component" (if Vue excluded)
- "Write Python code"
```

## Token Optimization Patterns

Reduce token usage by orders of magnitude.

**Global context (CLAUDE.md):**
- Keep under 3,000 tokens
- Move procedures → skills
- Move domain rules → specialized skills

**Per-skill optimization:**
- Short frontmatter descriptions (target: 150 chars)
- Keep SKILL.md under 500 lines
- Use progressive disclosure aggressively
- Bundle deterministic scripts to avoid repeated reasoning

**Example impact:**
- Without skill: 15 back-and-forth messages, 12,000 tokens
- With skill: 2 clarifying questions, 6,000 tokens (50% reduction)

## Validation Checklist

Before promoting a skill to production:

- [ ] Folder named in kebab-case
- [ ] SKILL.md exists (exact spelling, case-sensitive)
- [ ] YAML frontmatter has proper --- delimiters
- [ ] name is kebab-case, no capitals or spaces
- [ ] description includes both WHAT and WHEN
- [ ] No XML angle brackets (< >) in any field
- [ ] Instructions are imperative and clear
- [ ] Error handling and examples provided
- [ ] References linked with relative paths only
- [ ] Tested triggering on obvious tasks
- [ ] Tested triggering on paraphrased requests
- [ ] Does NOT trigger on unrelated topics
- [ ] Scripts are deterministic and tested
- [ ] File structure is complete

## Anti-Patterns to Avoid

❌ **Mega-skills**: Trying to handle 5+ unrelated workflows
- **Fix**: Split into focused leaf skills

❌ **Vague descriptions**: "Helps with projects"
- **Fix**: "Manages Linear project sprints, including planning and task assignment"

❌ **Over-triggering**: Loading for irrelevant queries
- **Fix**: Add negative triggers; be specific about scope

❌ **Wall-of-text instructions**: 2000+ line SKILL.md
- **Fix**: Move details to references; use progressive disclosure

❌ **No error handling**: Instructions assume everything works
- **Fix**: Add troubleshooting section with common failures

## Reference Documentation

For complete details, see:
- `references/01-fundamentals.md` - Core concepts and file structure
- `references/02-planning-design.md` - Use cases and design decisions
- `references/03-best-practices.md` - Writing effective instructions
- `references/04-patterns.md` - Common workflow patterns
- `references/05-token-optimization.md` - Cost and context optimization

## Common Workflows

### Building a Skill from Scratch

1. **Identify use case**: Document 2-3 concrete workflows
2. **Design frontmatter**: Trigger-optimized name + description
3. **Write instructions**: Imperative, numbered steps
4. **Add references**: Move detailed docs to references/
5. **Add scripts**: Bundle deterministic logic
6. **Test triggering**: Verify skill activates correctly
7. **Iterate**: Refine based on observation

### Optimizing an Existing Skill

1. **Measure baseline**: Count tokens, tool calls, user corrections
2. **Trim SKILL.md**: Move heavy docs to references/
3. **Refine description**: Test trigger accuracy
4. **Add scripts**: Replace repeated reasoning with code
5. **Re-measure**: Compare token usage before/after

### Debugging Over-Triggering

1. Check current description with Claude: "When would you use this skill?"
2. Add specific exclusions: "Do NOT use for X or Y"
3. Test paraphrased exclusions
4. Iterate until accuracy improves

## Getting Help

- **Skill authoring**: See 03-best-practices.md
- **Validation errors**: Check Validation Checklist section above
- **Token optimization**: See 05-token-optimization.md
- **Patterns**: See 04-patterns.md for sequential, multi-MCP, iterative patterns
