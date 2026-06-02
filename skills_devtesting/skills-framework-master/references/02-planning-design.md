# Planning and Design

## Start with Use Cases

Before coding, identify 2-3 concrete use cases:

```
Use Case: Project Sprint Planning

Trigger: User says "help me plan this sprint"

Steps:
1. Fetch current project status
2. Analyze team velocity
3. Suggest prioritization
4. Create tasks with labels

Result: Fully planned sprint
```

## Three Skill Categories

**Category 1: Document Creation**
- Frontend designs, reports, presentations
- Style guides, templates, quality checks
- No external tools required

**Category 2: Workflow Automation**
- Multi-step processes, validation gates
- Templates for common structures
- Iterative refinement loops

**Category 3: MCP Enhancement**
- Workflow guidance for tool access
- Sequence MCP calls
- Embed domain expertise

## Success Criteria

**Quantitative:**
- Triggers on 90% of relevant queries
- Completes workflow in X tool calls
- 0 failed API calls per workflow

**Qualitative:**
- Users don't need clarification prompts
- Consistent results across sessions
- New users succeed on first try

## Problem-First vs Tool-First

**Problem-first**: "I need to set up a workspace" → skill orchestrates tools

**Tool-first**: "I have MCP connected" → skill teaches best practices

Most skills lean one direction. Choose based on your use case.

## When to Create a Skill

Skills justify existence when:
- Workflow recurs often
- Complex enough that ad-hoc prompting fails
- Benefits materially from consistent steps
