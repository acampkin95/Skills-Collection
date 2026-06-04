---
name: structured-thinking
description: "Analytical thinking frameworks including MECE, first principles, systems thinking, decision matrices, mental models, problem decomposition, and reasoning patterns for non-CLI agents. Use when breaking down complex problems, making structured decisions, analyzing systems, applying mental models, or reasoning through ambiguity."
version: "1.0.0"
metadata:
  category: structured-thinking
  scope: non-cli
---

# Structured Thinking

Analytical frameworks, mental models, and reasoning patterns for systematic problem-solving and decision-making.

## Core Frameworks

### MECE (Mutually Exclusive, Collectively Exhaustive)

The foundation of structured analysis. Every problem can be broken into parts that don't overlap and cover everything.

```
RULES:
├── Mutually Exclusive: No item appears in more than one category
├── Collectively Exhaustive: All items are accounted for
└── Test: Can any item fit in two buckets? Is anything unaccounted for?

EXAMPLE — Revenue decline:
                    REVENUE = PRICE × VOLUME
                   ┌──────────┴──────────┐
              PRICE FACTORS          VOLUME FACTORS
              ├ Discounting           ├ New customers (down)
              ├ Competition           ├ Retention (down)
              ├ Mix shift             ├ Purchase frequency
              └ Inflation offset      └ Average order size

Each branch is MECE — no overlap, everything covered.
```

### First Principles Thinking

Break problems down to fundamental truths and build up from there.

```
PROCESS:
1. IDENTIFY the problem and current assumptions
2. DECOMPOSE into fundamental truths (what is definitely true?)
3. CHALLENGE each assumption (is this actually true? or just conventional?)
4. REBUILD from the fundamentals (what's possible now?)

EXAMPLE:
Problem: "We need a better search engine"
Assumptions:
  - We need to build our own
  - We need Elasticsearch
  - It will cost $50K/month

Fundamentals:
  - Users need to find content quickly
  - We have 10,000 documents
  - Latency must be under 200ms

Challenge:
  - Build our own? → No, Meilisearch is free and handles this scale
  - Elasticsearch? → Overkill for 10K docs
  - $50K? → Meilisearch on a $20/month server handles this

Rebuild:
  - Deploy Meilisearch → $20/month, 50ms latency
```

### Systems Thinking

Understand systems as interconnected wholes rather than isolated parts.

```
KEY CONCEPTS:
─────────────
FEEDBACK LOOPS:
├── Reinforcing (positive): A → more B → more A (growth/decline spiral)
│   Example: More users → more data → better product → more users
├── Balancing (negative): A → more B → less A (stabilizing)
│   Example: More traffic → slower response → less traffic

DELAY:
├── Action and effect are often separated in time
├── Cause and effect may be distant in space
└── Fixing symptoms can worsen root causes

LEVERAGE POINTS (where to intervene, most to least effective):
12. Constants, parameters (least effective)
11. Buffer sizes
10. Structure of material stocks and flows
9. Length of delays
8. Strength of balancing feedback loops
7. Gain around reinforcing feedback loops
6. Structure of information flows
5. Rules of the system
4. Power to add/change system goals
3. Power of self-organization
2. Goals of the system
1. Mindset out of which the system arises (most effective)
```

## Decision Frameworks

### Decision Matrix

```
USAGE: Compare options against weighted criteria

STEP 1: Define criteria and weights (total = 100%)
STEP 2: Score each option per criterion (1-10)
STEP 3: Multiply score × weight for each cell
STEP 4: Sum weighted scores for each option

EXAMPLE:
                Weight  Option A  Option B  Option C
Cost            30%     8 (2.4)   5 (1.5)   3 (0.9)
Performance     25%     6 (1.5)   8 (2.0)   9 (2.25)
Ecosystem       20%     9 (1.8)   7 (1.4)   4 (0.8)
Learning curve  15%     7 (1.05)  6 (0.9)   5 (0.75)
Support         10%     8 (0.8)   7 (0.7)   6 (0.6)
                ─────   ────────  ────────  ────────
TOTAL                   7.55      6.50      5.30

WINNER: Option A (highest weighted score)
```

### Impact/Effort Matrix

```
        HIGH IMPACT
            │
   DO FIRST │  DO NEXT
   (Quick   │  (Strategic
    Wins)   │   Projects)
            │
────────────┼────────────  EFFORT
            │
   DON'T DO │  DO LAST
   (Drop    │  (Fill-ins/
    or      │   Delegate)
   Deprior) │
            │
        LOW IMPACT
```

### Pros/Cons with Weighting

```
DECISION: [What you're deciding]

FACTOR              PRO (+)         CON (-)         WEIGHT
─────────────────────────────────────────────────────────
Cost                $5K cheaper     —               High
Speed               —               30% slower      High
Quality             Better UX       —               Medium
Timeline            —               2 weeks longer  Medium
Risk                Proven tech     —               Low
Team skills         —               New learning    Low
─────────────────────────────────────────────────────────
BALANCE:            3 pros          3 cons
WEIGHTED:           2 high pros     2 high cons
                    → Tied, decide on tiebreaker (speed vs cost)
```

## Problem Decomposition

### Issue Tree Method

```
ROOT PROBLEM: Website conversion rate is low (1.2% vs 3% target)

├── TRAFFIC QUALITY
│   ├── Wrong audience (marketing mismatch)
│   ├── High bounce from ads (poor landing pages)
│   └── Bot traffic inflating numbers
│
├── FIRST IMPRESSION
│   ├── Slow load time (LCP > 4s)
│   ├── Unclear value proposition
│   ├── Trust signals missing
│   └── Design looks dated
│
├── USER EXPERIENCE
│   ├── Complex navigation
│   ├── Too many steps to convert
│   ├── Mobile experience broken
│   └── Confusing pricing page
│
└── CONVERSION PATH
    ├── Form too long (12 fields)
    ├── No urgency/incentive
    ├── CTA unclear
    └── No social proof on page

PRIORITIZE: Fix load time first (biggest impact, measurable)
```

### 5 Whys (Root Cause Analysis)

```
PROBLEM: Users abandoning checkout

1. Why are they abandoning?
   → Getting stuck on payment page
2. Why are they stuck?
   → Error message after entering card details
3. Why is there an error?
   → Address validation failing for international addresses
4. Why is validation failing?
   → Only US address format supported
5. Why only US format?
   → MVP was US-only, international was "future phase"

ROOT CAUSE: Technical debt from MVP scoping
FIX: Add international address validation (not "fix error message")
```

### Pre-Mortem Analysis

```
PRE-MORTEM: Imagine the project has failed. Why?

PROJECT: [What you're planning]

POSSIBLE FAILURES:
├── Technical: Database can't handle the load
├── User: Nobody adopts the new feature
├── Timeline: 6 months becomes 18 months
├── Budget: Costs 3x the estimate
├── Team: Key person leaves mid-project
├── Integration: Third-party API changes
└── Market: Competitor launches similar product

MITIGATION FOR EACH:
├── Load testing before launch
├── Beta program with real users
├── Buffer time + milestone checkpoints
├── 20% contingency budget
├── Knowledge sharing / documentation
├── Abstraction layer over external APIs
└── Focus on differentiation, not speed
```

## Reasoning Patterns

### Ladder of Inference

```
OBSERVE → SELECT DATA → ADD MEANING → MAKE ASSUMPTIONS → DRAW CONCLUSIONS → ADOPT BELIEFS → TAKE ACTION

DANGER: We can jump from observation to action without examining intermediate steps.

CHECK: At each step, ask "Is this a fact or an interpretation?"
```

### Occam's Razor

```
Among competing explanations, prefer the one with fewest assumptions.

NOT: "The database is slow because of a cosmic ray flipping a bit in the cache layer causing cascading failures"
BUT: "The database is slow because we added a new query without an index"

APPLY: When debugging, check simple explanations before complex ones.
```

### Inversion

```
Instead of asking "How do I succeed?"
Ask "How would I definitely fail?" Then avoid those things.

INSTEAD OF: "How do I build a great product?"
ASK: "What would make this product terrible?"
├── Ignore user feedback
├── Over-engineer everything
├── No documentation
├── Ship without testing
├── Change scope constantly
→ Now avoid each of these systematically.
```

## Mental Models Quick Reference

| Model | Use When | Key Insight |
|-------|----------|-------------|
| **Pareto (80/20)** | Prioritizing effort | 80% of results from 20% of causes |
| **Second-order effects** | Evaluating decisions | Actions have ripple effects |
| **Opportunity cost** | Choosing between options | Value of the next-best alternative |
| **Sunk cost** | Continuing vs stopping | Past investment shouldn't influence future decisions |
| **Margin of safety** | Risk management | Build buffer for uncertainty |
| **Circle of competence** | Making judgments | Stay within your expertise |
| **Hanlon's Razor** | Attributing intent | Don't assume malice when incompetence explains it |
| **Dunning-Kruger** | Self-assessment | Beginners overestimate; experts underestimate |
| **Availability heuristic** | Estimating probability | Recent/vivid events seem more likely |
| **Confirmation bias** | Evaluating evidence | We seek data that confirms our beliefs |


## When to Use

- Breaking complex problems into manageable components
- Applying decision frameworks (cost-benefit, risk matrix, SWOT)
- Using first principles or analogical reasoning
- Making trade-off decisions with explicit criteria
- Planning multi-step workflows with dependency analysis

## Limitations

- Frameworks are simplifications — real problems have edge cases
- Structured thinking cannot substitute domain-specific expertise
- Over-frameworking can slow decision-making on time-critical tasks
- Quality of analysis depends on quality of input information

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [deep-research](../deep-research/SKILL.md) | Research planning uses structured thinking frameworks |
| [data-synthesis](../data-synthesis/SKILL.md) | Synthesis requires structured combination of evidence |
| [reporting](../reporting/SKILL.md) | Report recommendations follow structured decision logic |
| [content-strategy](../content-strategy/SKILL.md) | Content planning applies structured thinking |
