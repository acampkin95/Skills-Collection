# Writing Effective Instructions

## SKILL.md Body Structure

```markdown
# Skill Name

## Instructions

### Step 1: [Action]
Explanation of what happens.

Example:
\`\`\`bash
command --flag value
\`\`\`

### Step 2: [Action]
...

## Common Workflows

**Scenario 1:** User request
1. Action 1
2. Action 2
Result: outcome

## Troubleshooting

**Error:** Common error
**Cause:** Why it happens
**Solution:** How to fix
```

## Best Practices

✅ **Do:**
- Write in third-person imperative
- Use numbered steps with explicit branches
- Include error handling and recovery
- Provide 2-3 concrete examples
- Keep under 500 lines
- Use consistent terminology

❌ **Don't:**
- Use vague language ("validate the data")
- Assume everything works
- Create wall-of-text instructions
- Duplicate domain knowledge in CLAUDE.md

## Progressive Disclosure Pattern

**SKILL.md**: Orchestration and core workflow

**references/**: Detailed docs, schemas, API reference

In SKILL.md, explicitly tell Claude:
```markdown
## Before starting:
Read `references/schema.md` to understand data structures.
Read `references/error-codes.md` for recovery steps.
```

## Scripts: Deterministic Code

Bundle small scripts for:
- Parsing, data transformation
- API calls, database queries
- Validation logic
- File operations

Keep scripts under 100 lines with:
- Clear CLI arguments
- Structured JSON output
- Descriptive error messages
