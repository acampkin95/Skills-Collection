# Token Optimization and Leaf Skills

## Why Token Optimization Matters

Claude Code cost scales directly with context size. Skills are a lever for cost reduction because instructions and domain knowledge load progressively instead of being baked into every spawn.

Two goals:
1. Reduce baseline context (always loaded)
2. Reduce incremental context per task (loaded by skill)

## Keep Global Context Lean

Anthropic's cost guide stresses that `CLAUDE.md` loads before Claude sees user input.

**Best practices:**
- Keep `CLAUDE.md` under 3,000 tokens
- Move multi-step procedures → skills
- Move domain rules → specialized skills
- Use path-scoped rules for file-specific guidance

## Progressive Disclosure Inside Skills

Three-level model:
1. **Frontmatter** (always): name + description (~50 tokens)
2. **SKILL.md body** (when active): instructions (~500 tokens)
3. **References** (on-demand): detailed docs, schemas

**Implementation:**
- Keep frontmatter descriptions focused on routing
- Keep `SKILL.md` under 500 lines
- Use explicit instructions: "Before drafting, read `references/template.md`"

## Leaf Skills: Narrow and Composable

**Definition**: Skills that do ONE thing exceptionally well.

**Characteristics:**
- Single responsibility (one clearly defined job)
- Sharp description (clear what, when, when not to use)
- Small `SKILL.md` (fits on one screen)
- Deterministic helpers (scripts for parsing, validation)
- Concrete examples (worked examples, not abstract rules)

**Benefits:**
- Shorter files mean fewer tokens consumed
- Narrow focus reduces reference loading
- Easier to test and debug
- Composable into larger workflows

## Minimizing Tokens per Task

**Techniques:**
- Specific instructions: "Edit only auth.ts and update login()"
- Single responsibility: One skill, one job
- Anti-gravity constraints: Discourage unnecessary reasoning
- Hooks and preprocessing: Filter large logs before Claude sees them

**Example impact:**
- Without skill: 15 messages, 12,000 tokens
- With skill: 2 clarifying questions, 6,000 tokens (50% reduction)

## Leaf Skill Hierarchies

Leaf skills work best within composition patterns:

**Coordinator skill**: High-level skill that clarifies intent, selects leaves, and sequences calls

**Domain family**: Set of focused skills sharing a domain (pdf-extract, pdf-redact, pdf-annotate)

**Tool-pairing**: Skill whose instructions are a protocol for using an MCP server consistently

## Validation and Evaluation

**Static validation**: Check structure, frontmatter, antipatterns
- YAML validity
- Folder name matches `name` field
- Description length and content
- Presence of required sections

**Behavioral evaluation**: Run scenario-based tests
- Generate test prompts
- Define correct output assertions
- Compare skill vs baseline
- Grade outputs and iterate

## Integrated Practices

Combine optimization, validation, and leaf-skill design:

1. Design narrow skills (description reads like router rule)
2. Use progressive disclosure aggressively
3. Bundle deterministic scripts
4. Integrate validation CLIs and CI checks
5. Employ behavioral evaluation frameworks
6. Monitor token usage and refactor when needed
