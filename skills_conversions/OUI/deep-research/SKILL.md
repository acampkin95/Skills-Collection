---
name: deep-research
description: "Long-form systematic research methodology including literature review, systematic review, research planning, gap analysis, and comprehensive knowledge mapping for non-CLI agents. Use when conducting multi-hour research, literature reviews, systematic reviews, state-of-the-art analysis, or comprehensive topic exploration."
version: "1.0.0"
metadata:
  category: search-research
  scope: non-cli
---

# Deep Research Methodology

Comprehensive research frameworks for multi-hour, multi-source investigations. Covers systematic review, literature analysis, gap identification, and knowledge mapping.

## Research Planning Framework

### Pre-Research Brief

```
DEEP RESEARCH BRIEF
───────────────────
Topic:              [Primary research area]
Sub-questions:      [List specific questions to answer]
Scope boundaries:   [What's in scope / out of scope]
Time period:        [Relevant date range]
Domains:            [Academic, industry, government, community]
Expected depth:     [Number of sources, hours estimated]
Output format:      [Report, summary, comparison, briefing]
Audience:           [Who will consume this research]
```

### Research Phase Timeline

```
Phase 1: SCOPING          (10% of time)
├── Define questions
├── Identify key terminology
├── Map domain boundaries
└── Set success criteria

Phase 2: LANDSCAPING      (20% of time)
├── Broad searches
├── Identify major themes
├── Find key authorities/sources
└── Build initial concept map

Phase 3: TARGETED RESEARCH (40% of time)
├── Deep-dive into each theme
├── Collect and evaluate sources
├── Trace citations and references
└── Build evidence chains

Phase 4: ANALYSIS         (20% of time)
├── Cross-reference findings
├── Identify patterns and contradictions
├── Map agreement/disagreement
└── Synthesize key insights

Phase 5: OUTPUT           (10% of time)
├── Structure findings
├── Write report/summary
├── Include citations and confidence levels
└── Identify gaps for future research
```

## Systematic Search Strategy

### Snowball Search

Start with seed papers/articles, then expand through their references:

```
Seed Source (3-5 high-quality starting points)
    │
    ├──► Forward snowball: Who cited this? (newer work)
    │    └── Search for papers citing the seed
    │
    ├──► Backward snowball: What does this cite? (foundational work)
    │    └── Read the seed's references
    │
    └──► Lateral snowball: Related work by same authors/groups
         └── Search for other work by the same researchers
```

### Matrix Search

Organize searches by dimension:

```
              │ Academic │ Industry │ Community │ Official
──────────────┼──────────┼──────────┼───────────┼─────────
Topic A       │          │          │           │
Topic B       │          │          │           │
Topic C       │          │          │           │
Cross-cutting │          │          │           │
```

Fill each cell with at least 2-3 sources.

### Temporal Search

For topics that evolve over time:

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Origins  │─►│ Early   │─►│ Mature  │─►│ Current │
│ (-2010)  │  │ (10-15) │  │ (15-23) │  │ (24-26) │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
     │             │             │             │
  Foundational   Growth       Consolidation  Latest
  papers/concepts  patterns    best practices  trends
```

## Literature Review Patterns

### Structured Review Template

```markdown
# Literature Review: [Topic]

## Overview
[Brief summary of the research landscape]

## Key Themes

### Theme 1: [Name]
- **Consensus**: [What sources agree on]
- **Debate**: [Where sources disagree]
- **Key sources**: [List with evidence grades]
- **Gaps**: [What's not covered]

### Theme 2: [Name]
[same structure]

## Evolution Over Time
[How understanding has changed]

## Methodological Notes
[How studies/approaches differ in methodology]

## Synthesis
[Combined findings across all themes]

## Open Questions
[What remains unknown or debated]

## References
[Full source list with grades]
```

### Evidence Mapping

Track claims and their support across sources:

```
CLAIM MAP
─────────
Claim: "Technology X improves performance"
  ├── Study A (2023): +40% improvement (Level A)
  ├── Study B (2024): +25% improvement in specific context (Level B)
  ├── Blog C (2024): Anecdotal improvement (Level D)
  └── Study D (2024): No improvement in enterprise setting (Level B)
  
WEIGHT OF EVIDENCE: Mixed positive (2 positive, 1 negative, 1 anecdotal)
CONTEXT MATTERS: Benefit appears context-dependent
```

## Gap Analysis

### Types of Research Gaps

| Gap Type | Description | How to Identify |
|----------|-------------|-----------------|
| **Knowledge gap** | Something not yet studied | No sources address it |
| **Methodology gap** | Existing studies have weak methods | Critical reviews note limitations |
| **Context gap** | Findings not tested in specific context | Search for context-specific studies comes up empty |
| **Time gap** | Knowledge may be outdated | Last significant study is old |
| **Scale gap** | Only tested at small scale | Studies are prototypes, not production |
| **Population gap** | Only tested with specific group | Limited demographic/scale diversity |

### Gap Priority Matrix

```
HIGH IMPACT + HIGH FEASIBILITY → Priority 1 (address first)
HIGH IMPACT + LOW FEASIBILITY  → Priority 2 (note for future)
LOW IMPACT + HIGH FEASIBILITY  → Priority 3 (quick wins)
LOW IMPACT + LOW FEASIBILITY   → Priority 4 (deprioritize)
```

## Knowledge Mapping

### Concept Relationship Map

```
                    [Central Topic]
                    /      |       \
              [Sub A]   [Sub B]   [Sub C]
              /    \      |         |
          [A.1]  [A.2]  [B.1]    [C.1]
            │              │        │
            └──────┬───────┘        │
                   │                │
            [Cross-cutting theme]   │
                   │                │
                   └────────────────┘
```

### Expertise Mapping

Track who the key voices are:

```
EXPERT MAP
──────────
[Person/Org A]
  ├── Focus area: [specialty]
  ├── Key works: [titles/links]
  ├── Stance: [their position]
  └── Cited by: [who references them]

[Person/Org B]
  [same structure]
```

## Research Quality Assurance

### Confidence Grading for Conclusions

| Grade | Meaning | Criteria |
|-------|---------|----------|
| **Confirmed** | High confidence | 3+ Level A sources agree, no credible contradiction |
| **Probable** | Good confidence | 2+ Level A/B sources agree, minor contradictions |
| **Possible** | Moderate confidence | Some evidence supports, but limited or mixed |
| **Debated** | Uncertain | Significant credible sources on both sides |
| **Insufficient** | Unknown | Not enough quality evidence to assess |

### Research Completeness Checklist

- [ ] All sub-questions have been addressed or marked as gaps
- [ ] Sources span multiple domains (academic, industry, community)
- [ ] Temporal coverage is appropriate for the topic
- [ ] Contradictions between sources are documented and analyzed
- [ ] Each key claim has at least 2 independent sources
- [ ] Methodology of key sources has been evaluated
- [ ] Limitations and biases have been acknowledged
- [ ] Open questions are clearly identified
- [ ] Confidence levels are assigned to all conclusions


## Firecrawl-Driven Research Pipeline

### Crawl-to-Evidence Workflow

```
FIRECRAWL ENHANCED DEEP RESEARCH:
──────────────────────────────────
1. RECON            → /map on seed domains to discover relevant pages
2. SCOPE            → Filter discovered URLs against research questions
3. BULK EXTRACT     → /crawl with formats: ["markdown"] on scoped URLs
4. STRUCTURED PULL  → /extract with schema for key data points
5. EVIDENCE MAP     → Score and categorize extracted content
6. GAP DETECT       → Compare extracted claims against research questions
7. TARGETED FILL    → /agent for open questions requiring new sources
8. SYNTHESIZE       → Combine into research output with evidence grades

ADVANTAGES OVER MANUAL SEARCH:
├── /map discovers pages search engines might miss (sitemap, internal links)
├── /crawl extracts full site content in one async operation
├── /extract provides schema-validated structured data
├── /agent finds sources autonomously for unknown domains
└── All outputs in markdown — ready for LLM analysis
```

### Firecrawl Integration per Research Phase

| Phase | Firecrawl Tool | Use Case |
|-------|---------------|----------|
| **Scoping** | `/map` | Discover site structure, estimate content scope |
| **Landscaping** | `/crawl` (shallow) | Broad extraction with limit: 20-50 pages |
| **Targeted** | `/extract` | Pull specific data fields from known pages |
| **Analysis** | `/scrape` | Deep extraction of individual high-value pages |
| **Gap Fill** | `/agent` | Let AI find sources for unanswered questions |
| **Update** | `/crawl` (incremental) | Re-crawl for content changes since last pass |

### Research-to-Extract Schema Templates

```
COMPETITIVE ANALYSIS EXTRACTION:
  schema:
    products:
      type: array
      items:
        name, pricing, features[], rating, url

LITERATURE REVIEW EXTRACTION:
  schema:
    papers:
      type: array
      items:
        title, authors[], year, abstract, methodology, findings, citations

MARKET RESEARCH EXTRACTION:
  schema:
    market_data:
      type: object
      properties:
        market_size, growth_rate, key_players[], trends[], sources[]
```

## When to Use

- Multi-phase research requiring gap analysis and iterative refinement
- Literature reviews spanning academic, technical, and industry sources
- Building knowledge maps of complex or unfamiliar domains
- Research that requires methodological rigor (systematic reviews, meta-analyses)
- Investigating topics where surface-level search is insufficient

## Limitations

- Time-intensive — may require multiple search iterations and tool calls
- Comprehensive coverage is aspirational; some domains have poor web coverage
- Academic paywalls limit access to peer-reviewed literature
- Requires sustained context window across multiple research phases

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-research](../web-research/SKILL.md) | Deep research extends basic research with planning and gap analysis |
| [source-evaluation](../source-evaluation/SKILL.md) | Evaluate credibility of each source encountered |
| [data-synthesis](../data-synthesis/SKILL.md) | Synthesize deep research findings into coherent knowledge |
| [structured-thinking](../structured-thinking/SKILL.md) | Apply decision frameworks to research planning |
| [reporting](../reporting/SKILL.md) | Format deep research findings into research reports |
| [firecrawl-web-crawling](../firecrawl-web-crawling/SKILL.md) | Firecrawl-driven crawl-to-evidence pipeline for bulk extraction |
