---
name: prompt-engineering
description: Prompt engineering for Claude models — system prompts, structured output, tool use, chain-of-thought, and evaluation patterns.
version: 2.0.0
reviewed: "2026-06-04"
---
# Prompt Engineering

**Quick reference:**
- `references/anthropic-api.md` — Claude models, API, version selection
- `references/structured-output.md` — JSON output, tool use, schema design
- `references/evaluation.md` — Testing, metrics, prompt evals

## Core Principles

1. **Be specific** - Vague instructions produce vague outputs
2. **Show, don't tell** - Examples outperform descriptions
3. **Structure matters** - XML tags, markdown, numbered lists improve parsing
4. **Think step by step** - Complex tasks benefit from decomposition
5. **Assign a role** - System prompts set context and constraints

## Prompt Architecture Patterns

### System -> Context -> Task -> Format -> Constraints

```
┌─────────────────────────────────────────────┐
│ SYSTEM: Role, identity, global rules        │  ← Cached (static prefix)
├─────────────────────────────────────────────┤
│ CONTEXT: Documents, data, conversation      │  ← Dynamic per request
├─────────────────────────────────────────────┤
│ TASK: What to do with the context           │  ← User's actual question
├─────────────────────────────────────────────┤
│ FORMAT: Output structure, JSON schema       │  ← Parsing expectations
├─────────────────────────────────────────────┤
│ CONSTRAINTS: Boundaries, safety, limits     │  ← Guardrails
└─────────────────────────────────────────────┘
```

```ts
const messages = [
  {
    role: "system",
    content: [
      // SYSTEM layer — cached for cost savings
      "You are a medical triage assistant for a telehealth platform.",
      "You help patients describe symptoms and recommend urgency levels.",
      "",
      // CONSTRAINTS layer — always in system prompt
      "## Rules",
      "- Never diagnose conditions. Only assess urgency.",
      "- Always recommend seeing a doctor for serious symptoms.",
      "- Output urgency as: emergency | urgent | routine | self-care",
    ].join("\n"),
  },
  {
    role: "user",
    content: [
      // CONTEXT layer
      "<patient_history>",
      patientHistory,
      "</patient_history>",
      "",
      // TASK layer
      `The patient reports: "${symptoms}"`,
      "",
      // FORMAT layer
      "Respond with JSON: { urgency, reasoning, next_steps: string[] }",
    ].join("\n"),
  },
];
```

### Decomposition for Complex Tasks

Break large tasks into sequential prompts rather than one mega-prompt:

| Step | Prompt Purpose | Output |
|------|---------------|--------|
| 1 | Extract key entities from document | Entity list |
| 2 | Classify relationships between entities | Relationship graph |
| 3 | Generate summary from entities + relationships | Final summary |

This gives better results than "Extract entities, find relationships, and summarize."


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.