---
name: reporting
description: "Structured report generation, data presentation, executive summaries, report templates, and effective communication of findings for non-CLI agents. Use when creating reports, presenting research findings, writing executive summaries, building data dashboards, or communicating analysis results."
version: "1.0.0"
metadata:
  category: reporting-documentation
  scope: non-cli
---

# Reporting & Data Presentation

Structuring findings, writing reports, creating executive summaries, and presenting data effectively.

## Report Types & When to Use

| Report Type | Purpose | Length | Audience |
|-------------|---------|--------|----------|
| **Executive Brief** | Quick decision support | 1 page | Leadership |
| **Research Report** | Detailed findings | 5-20 pages | Stakeholders |
| **Technical Report** | Implementation details | 10-50 pages | Technical team |
| **Status Update** | Progress tracking | 0.5-1 page | Team/management |
| **Incident Report** | Post-incident analysis | 2-5 pages | Engineering/leadership |
| **Comparison Report** | Option evaluation | 3-10 pages | Decision makers |
| **Audit Report** | Compliance/quality review | 5-30 pages | Compliance/security |

## Report Structure Templates

### Executive Brief

```markdown
# [Title]

**Date:** YYYY-MM-DD | **Author:** [Name] | **Status:** Draft/Final

## Bottom Line (3 sentences max)
[The key finding or recommendation that the reader must know]

## Key Findings
1. [Finding 1 — one sentence each]
2. [Finding 2]
3. [Finding 3]

## Recommendation
[What should be done, with confidence level]

## Evidence Summary
| Finding | Evidence Strength | Source Count |
|---------|------------------|-------------|
| Finding 1 | Strong (A) | 5 sources |
| Finding 2 | Moderate (B) | 3 sources |

## Risks & Caveats
- [Key risk or limitation]
- [Important caveat]
```

### Research Report

```markdown
# [Research Title]

**Date:** YYYY-MM-DD | **Author:** [Name] | **Version:** 1.0

## Executive Summary
[1-2 paragraph overview: what was researched, key findings, recommendations]

## Research Questions
1. [Primary question]
2. [Secondary question]
3. [Tertiary question]

## Methodology
- Sources consulted: [count and types]
- Search period: [date range]
- Evaluation criteria: [brief description]

## Findings

### [Finding 1 Title]
**Confidence:** High/Medium/Low

[Detailed finding with evidence]

### [Finding 2 Title]
**Confidence:** High/Medium/Low

[Detailed finding with evidence]

## Analysis
[Cross-cutting analysis, patterns, contradictions]

## Conclusions
[Synthesized conclusions answering research questions]

## Recommendations
1. [Recommendation with rationale]
2. [Recommendation with rationale]

## Open Questions
- [What remains unknown]
- [What needs further research]

## References
[Numbered reference list with evidence grades]
```

### Comparison / Evaluation Report

```markdown
# Evaluation: [What's Being Compared]

## Evaluation Criteria
| Criterion | Weight | Description |
|-----------|--------|-------------|
| Performance | 30% | Speed, scalability |
| Cost | 25% | Total cost of ownership |
| Ecosystem | 20% | Community, libraries |
| Learning curve | 15% | Time to productivity |
| Support | 10% | Commercial/community support |

## Options Overview
| | Option A | Option B | Option C |
|-|----------|----------|----------|
| Type | [brief] | [brief] | [brief] |
| License | | | |
| Maturity | | | |

## Detailed Comparison

### Performance
[Data and analysis for each option]

### Cost
[Data and analysis for each option]

## Scoring Matrix
| Criterion (weight) | Option A | Option B | Option C |
|---------------------|----------|----------|----------|
| Performance (30%) | 8/10 | 7/10 | 9/10 |
| Cost (25%) | 6/10 | 9/10 | 5/10 |
| ... | ... | ... | ... |
| **Weighted Total** | **7.2** | **7.8** | **7.0** |

## Recommendation
[Recommended option with rationale]

## Risks
[Per-option risks and mitigations]
```

## Data Presentation

### Choosing the Right Visualization

```
WHAT TO SHOW          → BEST CHART TYPE
──────────────────────────────────────────
Comparison (few)      → Bar chart
Comparison (many)     → Horizontal bar
Trend over time       → Line chart
Composition           → Stacked bar or donut
Distribution          → Histogram or box plot
Correlation           → Scatter plot
Geographic            → Choropleth map
KPI vs target         → Gauge or bullet chart
Ranking               → Ordered bar
Flow/progress         → Funnel or Sankey
Part-to-whole         → Treemap or donut
```

### Data Presentation Rules

```
TABLES:
├── Align numbers to the right
├── Align text to the left
├── Use consistent decimal places
├── Bold the key numbers
├── Add units in headers, not cells
├── Use zebra striping for long tables
└── Keep column count ≤ 7

CHARTS:
├── Always label axes
├── Include units in axis labels
├── Use consistent color scheme
├── Start y-axis at zero (for bar charts)
├── Don't use 3D effects (distorts data)
├── Annotate key data points
├── Include source citation
└── Prefer horizontal labels over legends

NUMBERS IN TEXT:
├── Round appropriately (2 significant figures for prose)
├── Use comparisons ("3x faster" > "300% faster")
├── Provide context ("2.5s, which is 30% below our target")
├── Order from most to least important
└── Highlight the number that matters most
```

### Executive Summary Writing

```
FORMULA:
────────
1. HOOK (1 sentence): Why this matters right now
2. FINDING (2-3 sentences): What you discovered
3. RECOMMENDATION (1-2 sentences): What should be done
4. CONFIDENCE (1 sentence): How certain are you

EXAMPLE:
"User engagement dropped 23% last quarter, correlating with 
the homepage redesign (HIGH confidence, 4 independent data sources). 
The new layout buries the primary CTA below the fold. We recommend 
reverting to the above-fold CTA placement and A/B testing alternatives."

RULES:
├── No jargon
├── Lead with the impact
├── Include a number
├── State confidence level
├── Keep to 3-5 sentences
└── Write it LAST (after all analysis is done)
```

## Report Quality Standards

### Before Delivery Checklist

```
CONTENT:
├── [ ] Research questions all addressed
├── [ ] Every claim has a source
├── [ ] Contradictions acknowledged
├── [ ] Confidence levels stated
├── [ ] Limitations identified
├── [ ] Clear recommendation provided

STRUCTURE:
├── [ ] Executive summary is self-contained
├── [ ] Logical flow from overview to detail
├── [ ] Headings are descriptive and scannable
├── [ ] Data visualizations are clear and labeled
├── [ ] References are complete and formatted

CLARITY:
├── [ ] No undefined jargon
├── [ ] Active voice used
├── [ ] Technical terms explained
├── [ ] Sentences under 30 words average
├── [ ] No unnecessary qualifiers ("somewhat", "arguably")

INTEGRITY:
├── [ ] Data not cherry-picked
├── [ ] Alternative viewpoints included
├── [ ] Methodology described
├── [ ] Sources are recent enough for topic
└── [ ] No conflicts of interest
```

### Confidence Level Communication

```
HOW TO EXPRESS UNCERTAINTY:
───────────────────────────
HIGH CONFIDENCE:
"Analysis confirms..." / "Evidence strongly supports..."
"Based on [N] independent sources..."

MEDIUM CONFIDENCE:
"Evidence suggests..." / "Data indicates..."
"While not conclusive, the pattern..."

LOW CONFIDENCE:
"Initial findings hint at..." / "Limited evidence suggests..."
"This requires further investigation before conclusions"

NEVER:
"Proof that..." (proof is for math)
"Everyone knows..." (unsubstantiated)
"Studies prove..." (cite specific studies)
```


## When to Use

- Creating executive summaries, research reports, or comparison analyses
- Presenting findings from research or evaluation work
- Building decision-support documents with scoring matrices
- Formatting data for stakeholder consumption
- Writing status reports, post-mortems, or incident reports

## Limitations

- Template structures should be adapted to organizational expectations
- Data visualization quality depends on available rendering tools
- Executive audiences need tailored framing that technical audiences do not
- Recommendations require domain expertise to be actionable

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [technical-writing](../technical-writing/SKILL.md) | Reports follow technical writing best practices |
| [data-synthesis](../data-synthesis/SKILL.md) | Reports synthesize data into structured narratives |
| [visual-design](../visual-design/SKILL.md) | Table and chart formatting applies visual design principles |
| [structured-thinking](../structured-thinking/SKILL.md) | Decision frameworks inform recommendation logic |
