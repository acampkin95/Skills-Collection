---
name: data-synthesis
description: "Multi-source data synthesis, evidence combination, fact-checking workflows, bias detection, claim verification, and analytical reasoning for non-CLI agents. Use when combining information from multiple sources, resolving contradictions, grading evidence quality, detecting bias in data, or synthesizing findings into coherent conclusions."
version: "1.0.0"
metadata:
  category: structured-thinking
  scope: non-cli
---

# Data Synthesis & Analysis

Combining information from multiple sources, resolving contradictions, grading evidence, and drawing defensible conclusions.

## Synthesis Process

### The Four Stages

```
STAGE 1: COLLECT
├── Gather raw data from all sources
├── Standardize format and encoding
├── Tag each datum with source metadata
└── Create source index for traceability

STAGE 2: COMPARE
├── Map overlapping claims across sources
├── Identify agreements and contradictions
├── Note unique contributions per source
└── Flag gaps where no source provides data

STAGE 3: RECONCILE
├── Resolve contradictions (strongest evidence wins)
├── Merge overlapping information
├── Note unresolved conflicts
└── Assign confidence to each reconciled point

STAGE 4: SYNTHESIZE
├── Build coherent narrative from reconciled data
├── Identify patterns and themes
├── Draw conclusions with confidence levels
└── Flag assumptions and limitations
```

## Evidence Combination

### Combining Multiple Sources

```
AGREEMENT MATRIX:
─────────────────
                    Source A   Source B   Source C   Source D
Claim 1: X is true    ✓          ✓          ✓          ✗
Claim 2: Y is false   ✓          ✓          ?          ✓
Claim 3: Z is...      ✗          ✓          ✓          ?

LEGEND:
  ✓ = Source supports claim
  ✗ = Source contradicts claim
  ? = Source doesn't address claim

RESOLUTION:
  All ✓          → High confidence, adopt claim
  Mostly ✓       → Good confidence, note dissent
  Mixed ✓/✗      → Low confidence, investigate why
  All ✗          → High confidence, claim is false
  Mostly ?       → Insufficient evidence, note as gap
```

### Weighted Evidence Synthesis

```
EVIDENCE WEIGHTING:
───────────────────
Weight = Source Authority × Evidence Type × Recency × Independence

SOURCE AUTHORITY:
├── Official/primary (3x)
├── Peer-reviewed (2.5x)
├── Reputable secondary (2x)
├── Community/expert (1.5x)
└── Unverified/anonymous (0.5x)

EVIDENCE TYPE:
├── Experimental data (3x)
├── Statistical analysis (2.5x)
├── Documented case study (2x)
├── Expert reasoning (1.5x)
└── Anecdotal (0.5x)

RECENCY:
├── < 6 months (1.5x)
├── < 2 years (1.0x)
├── < 5 years (0.75x)
└── > 5 years (0.5x)

INDEPENDENCE:
├── Independently derived (1.5x)
├── Cites original source (1.0x)
├── Copies without citation (0.5x)
└── Unknown provenance (0.25x)
```

## Contradiction Resolution

### When Sources Disagree

```
RESOLUTION PROTOCOL:
────────────────────
1. VERIFY THE CONTRADICTION
   Are they actually saying different things?
   Or talking about different contexts/time periods?

2. CHECK METHODOLOGY
   How did each source reach their conclusion?
   Which methodology is more rigorous?

3. CHECK CURRENCY
   Is one source more recent?
   Has the situation changed?

4. CHECK AUTHORITY
   Which source has deeper domain expertise?
   Which has the stronger track record?

5. CHECK SCOPE
   Are they actually talking about different populations/environments?
   Could both be true in different contexts?

6. RESOLVE
   ┌── Clear winner → Adopt that position, note the disagreement
   ├── Context-dependent → State both, with applicable contexts
   └── Irresolvable → Flag as "debated" with evidence on both sides
```

### Handling Statistical Conflicts

```
WHEN NUMBERS DISAGREE:
─────────────────────
Check:
├── Definitions: Are they measuring the same thing?
├── Methodology: Survey vs census vs sample?
├── Time period: Same date range?
├── Population: Same target group?
├── Margin of error: Are they within each other's confidence intervals?
└── Adjustments: Raw vs seasonally adjusted?

RULE: Never average conflicting statistics.
Instead, report the range and explain the discrepancy.
"Estimates range from 20% (Survey A, 1000 respondents) to 35% 
(Report B, enterprise data). The gap likely reflects different 
methodologies and populations."
```

## Fact-Checking Patterns

### Claim Verification Workflow

```
CLAIM: "React is the most popular frontend framework"

STEP 1: DECOMPOSE
├── What exactly is being claimed? (popularity ranking)
├── What metric defines "most popular"? (downloads? surveys? jobs?)
├── What timeframe? (currently? ever?)
└── What comparison set? (all frameworks? just JS frameworks?)

STEP 2: DEFINE METRICS
├── npm downloads (quantitative, verifiable)
├── Developer surveys (State of JS, Stack Overflow)
├── Job postings (LinkedIn, Indeed data)
├── GitHub stars (community engagement)
└── Production usage (BuiltWith, Wappalyzer)

STEP 3: VERIFY
├── npm trends: React > Vue > Angular (verified ✓)
├── State of JS 2024: React #1 in usage (verified ✓)
├── Downloads: React highest (but React includes non-framework use)
├── Caveat: "Downloads" is imperfect metric for framework popularity

STEP 4: CONTEXTUALIZE
├── True for: usage, downloads, job market
├── Not true for: developer satisfaction (Svelte scores higher)
├── Nuance: "most popular" ≠ "best"

STEP 5: CONCLUDE
SUPPORTED: Yes, by multiple metrics
CONFIDENCE: High
CAVEATS: Depends on metric chosen; satisfaction differs from popularity
```

### Statistical Literacy

```
QUESTIONS TO ASK OF ANY STATISTIC:
──────────────────────────────────
1. Source: Who produced this number and why?
2. Method: How was it measured?
3. Sample: Who/what was included?
4. Sample size: Is it large enough to be meaningful?
5. Margin of error: What's the confidence interval?
6. Context: Compared to what baseline?
7. Trend: Is this a one-time snapshot or part of a trend?
8. Definition: What exactly does the number represent?
9. Conflicts: Do other sources agree?
10. Significance: Is the difference statistically significant?

COMMON STATISTICAL FALLACIES:
├── Correlation ≠ Causation
├── Survivorship bias (only counting successes)
├── Base rate neglect (ignoring the underlying probability)
├── Selection bias (non-representative sample)
├── Anchoring (over-weighting the first number seen)
├── Regression to the mean (extreme values tend to normalize)
└── Simpson's paradox (trend reverses when groups combined)
```

## Synthesis Output Formats

### Finding Card

```
┌─────────────────────────────────────────────┐
│ FINDING: [Clear statement of what was found] │
│ CONFIDENCE: [High/Medium/Low]               │
│ SOURCES: [N] independent sources             │
│ EVIDENCE GRADE: [A/B/C/D/E]                 │
│                                              │
│ Supporting:                                  │
│ • Source A (Level B): [brief summary]        │
│ • Source B (Level A): [brief summary]        │
│                                              │
│ Contradicting:                               │
│ • Source C (Level C): [brief summary]        │
│                                              │
│ Context: [When/where this applies]           │
│ Caveats: [Important limitations]             │
└─────────────────────────────────────────────┘
```

### Synthesis Summary

```markdown
# Synthesis: [Topic]

## Consensus (what sources agree on)
- [Agreed point 1] — supported by [N] sources
- [Agreed point 2] — supported by [N] sources

## Debate (where sources disagree)
- [Debated point]: [Position A] (Sources X, Y) vs [Position B] (Sources Z)
  - Likely reason: [Why they disagree]

## Gaps (what no source adequately addresses)
- [Gap 1]: Mentioned by [N] sources but not deeply explored
- [Gap 2]: No source addresses this

## Confidence Assessment
| Finding | Confidence | Evidence Grade |
|---------|-----------|----------------|
| [Finding 1] | High | A |
| [Finding 2] | Medium | B |

## Key Takeaways
1. [Most important conclusion]
2. [Second most important conclusion]
3. [Action recommendation]
```


## When to Use

- Combining information from multiple sources into coherent conclusions
- Resolving contradictions between different sources
- Fact-checking claims against multiple evidence points
- Producing synthesis reports with consensus/debate/gap structure
- Assessing confidence levels for conclusions based on evidence quality

## Limitations

- Synthesis quality is bounded by source quality and coverage
- Contradiction resolution may require domain expertise beyond available sources
- Confidence assessments are qualitative, not statistically rigorous
- Temporal drift — synthesized knowledge decays as sources age

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [source-evaluation](../source-evaluation/SKILL.md) | Source quality ratings inform synthesis confidence |
| [web-research](../web-research/SKILL.md) | Research produces the raw material for synthesis |
| [deep-research](../deep-research/SKILL.md) | Deep research requires rigorous synthesis methods |
| [reporting](../reporting/SKILL.md) | Synthesis output feeds into report writing |
