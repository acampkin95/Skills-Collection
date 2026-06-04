---
name: technical-writing
description: "Technical writing standards, documentation frameworks (Diátaxis), writing for clarity, documentation-as-code, API documentation, and style guides for non-CLI agents. Use when writing technical documentation, creating guides, documenting APIs, writing tutorials, or producing reference material."
version: "1.0.0"
metadata:
  category: reporting-documentation
  scope: non-cli
---

# Technical Writing

Standards, frameworks, and best practices for creating clear, effective technical documentation.

## Diátaxis Documentation Framework

### The Four Documentation Types

```
                    ACTION-ORIENTED          KNOWLEDGE-ORIENTED
                    (Doing)                  (Understanding)
            ┌───────────────────────┬───────────────────────┐
  PRACTICAL  │       TUTORIAL       │        HOW-TO         │
  (Learning) │  Learning-oriented   │   Task-oriented       │
             │  "Follow me"         │   "Do this"           │
             │  Guided path         │   Step-by-step recipe │
             ├───────────────────────┼───────────────────────┤
  THEORETICAL│     EXPLANATION      │      REFERENCE        │
  (Knowing)  │  Understanding-oriented│  Information-oriented│
             │  "Let me explain"    │   "Look this up"      │
             │  Context, why        │   Facts, specifications│
             └───────────────────────┴───────────────────────┘
```

### When to Write Each Type

| Type | User Needs | You Write | Characteristics |
|------|-----------|-----------|-----------------|
| **Tutorial** | "I'm new, teach me" | Guided learning path | Step-by-step, single path, works every time |
| **How-to Guide** | "I need to do X" | Specific task solution | Steps, multiple valid approaches, practical |
| **Explanation** | "Why does it work this way?" | Context and reasoning | Discussion, alternatives, history, trade-offs |
| **Reference** | "What are the options?" | Complete specifications | Structured, exhaustive, factual, no narrative |

## Writing Principles

### Clarity First

```
WRITE FOR THE READER, NOT YOURSELF:
────────────────────────────────────
BEFORE (poor):                    AFTER (clear):
"The function takes a param      "Give the function a string to
that accepts a string value       search for:
for the search query."
                                   search('my query')"

BEFORE:                           AFTER:
"Instantiate the object by        "Create a new client:
invoking the constructor."
                                   const client = new Client()"

BEFORE:                           AFTER:
"Utilize the aforementioned       "Use the API to send email."
API for the purpose of
transmitting electronic mail."
```

### Rules for Technical Writing

```
1. SHORT SENTENCES (max 25 words average)
2. ACTIVE VOICE ("Click the button" not "The button should be clicked")
3. SECOND PERSON ("You can..." not "Users can...")
4. PRESENT TENSE ("Clicks the button" not "Clicked the button")
5. ONE IDEA PER PARAGRAPH
6. CONCRETE EXAMPLES over abstract descriptions
7. SCANNABLE HEADINGS (noun phrases for reference, verb phrases for guides)
8. LEAD WITH THE ANSWER (don't bury the key info)
```

### Document Structure Patterns

```
TUTORIAL STRUCTURE:
───────────────────
# Tutorial: [What They'll Learn]

## Prerequisites
- What they need before starting

## Introduction (2-3 sentences: what and why)

## Step 1: [Action-Oriented Title]
Explain what and why. Then the action.
Verify: "You should see..."

## Step 2: [Action-Oriented Title]
Continue the journey...

## Step N: Final Step
Wrap up and verify the complete result.

## Summary
What they learned, where to go next.

HOW-TO GUIDE STRUCTURE:
───────────────────────
# How to [Achieve Specific Goal]

## Overview (1-2 sentences)

## Prerequisites (if any)

## Option A: [Approach Name]
Steps for this approach.

## Option B: [Alternative Approach]
Steps for alternative.

## Troubleshooting
Common issues and fixes.

REFERENCE STRUCTURE:
────────────────────
# [Component/API Name] Reference

## Overview (1 sentence)

## Properties / Parameters
| Name | Type | Required | Default | Description |
...

## Methods / Endpoints
### methodName()
Description. Returns: type.

## Types
Type definitions.

## Examples
3-5 practical examples.

EXPLANATION STRUCTURE:
─────────────────────
# Understanding [Concept]

## Overview
What this concept is and why it matters.

## How It Works
The mechanics and reasoning.

## Trade-offs
Advantages and disadvantages.

## Alternatives
Other approaches and why this one was chosen.

## Further Reading
Links to deeper resources.
```

## Writing for Different Audiences

```
BEGINNER:
├── Define every term on first use
├── Explain the "why" before the "what"
├── Provide complete, runnable examples
├── Anticipate confusion points
├── Link to prerequisites
└── Use analogies to familiar concepts

INTERMEDIATE:
├── Assume basic domain knowledge
├── Focus on practical application
├── Show common patterns and shortcuts
├── Mention gotchas and edge cases
└── Link to reference for details

EXPERT:
├── Get to the point quickly
├── Focus on architecture and trade-offs
├── Show advanced patterns
├── Discuss internals when relevant
└── Provide specification references
```

## API Documentation

### Endpoint Documentation Pattern

```markdown
### POST /api/v2/articles

Create a new article.

**Required scope:** `articles:write`

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Article title (3-200 characters) |
| `body` | string | Yes | Article content (markdown) |
| `tags` | string[] | No | Tags (max 10) |
| `status` | string | No | `draft` (default) or `published` |

#### Request Example

```json
{
  "title": "Getting Started with APIs",
  "body": "# Introduction\n\nThis guide...",
  "tags": ["api", "getting-started"],
  "status": "draft"
}
```

#### Response

**201 Created**
```json
{
  "data": { "id": 123, "title": "...", "status": "draft" },
  "meta": { "created_at": "2025-01-15T10:30:00Z" }
}
```

**400 Bad Request**
```json
{
  "error": { "code": "VALIDATION_ERROR", "message": "..." }
}
```
```

## Style Guide Essentials

### Formatting Standards

```
TERMINOLOGY:
├── Use one term per concept (don't mix "folder"/"directory")
├── Define terms on first use, then use consistently
├── Capitalize product names correctly
└── Use code formatting for code terms: `variable`, `className`

CODE BLOCKS:
├── Always specify language: ```python, ```json
├── Keep examples short and runnable
├── Highlight key lines with comments
├── Show expected output after code
└── Use realistic values (not "foo", "bar")

HEADINGS:
├── Use sentence case: "Getting started" not "Getting Started"
├── Tasks: Verb phrases: "Configure authentication"
├── Reference: Noun phrases: "Authentication configuration"
├── Keep headings descriptive (not "More info")
└── Don't skip levels (h1 → h2 → h3, never h1 → h3)

LISTS:
├── Ordered: Sequential steps (do this first, then this)
├── Unordered: Non-sequential items
├── Keep items parallel (same grammatical structure)
└── Start with a capital, end with period (or not, but be consistent)
```

### Common Mistakes to Avoid

```
DON'T:
├── Use jargon without definition
├── Write long paragraphs (break them up)
├── Bury important info in walls of text
├── Assume the reader's context
├── Use passive voice excessively
├── Create documentation that rots (no maintenance plan)
├── Duplicate information across pages
└── Forget to update docs when code changes

DO:
├── Front-load the most important information
├── Use examples for every concept
├── Test your instructions (actually follow them)
├── Include error messages and troubleshooting
├── Date your documents and review regularly
├── Link between related documents
└── Get feedback from actual users
```


## When to Use

- Writing tutorials, how-to guides, reference docs, or explanations
- Structuring documentation using the Diátaxis framework
- Creating API documentation with consistent formatting
- Writing for different audiences (beginners, developers, executives)
- Editing technical prose for clarity, brevity, and accuracy

## Limitations

- Domain-specific terminology requires subject matter expert review
- Code examples need testing to ensure accuracy
- Documentation structure depends on the specific product or library
- Style guides should be adapted to organizational conventions

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [information-architecture](../information-architecture/SKILL.md) | IA principles inform documentation structure |
| [reporting](../reporting/SKILL.md) | Report writing applies technical writing principles |
| [content-strategy](../content-strategy/SKILL.md) | Content strategy governs documentation planning |
| [design-principles](../design-principles/SKILL.md) | Writing clarity mirrors design clarity principles |
