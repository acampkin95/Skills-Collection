---
name: summarization
description: "Summarization techniques for non-CLI agents. Covers extractive vs abstractive methods, progressive summarization levels, chain-of-density compression, key point extraction, executive summary patterns, multi-document synthesis, and adaptive compression strategies. Use when condensing content, creating executive summaries, extracting key points, or synthesizing multiple sources."
version: "1.0.0"
metadata:
  category: structured-thinking
  scope: non-cli
---

# Summarization

Techniques for condensing content while preserving essential meaning, structure, and intent. Covers extraction strategies, compression methods, and output formats.

## Core Principles

1. **Preserve intent** — The summary must reflect the author's original purpose
2. **Retain key claims** — Every significant assertion should survive compression
3. **Maintain hierarchy** — Major points remain major, supporting details condense
4. **Signal compression level** — Always indicate what was compressed and why
5. **Verify fidelity** — Check that the summary doesn't distort the source

---

## Summarization Approaches

### Extractive vs. Abstractive

| Dimension | Extractive | Abstractive |
|-----------|-----------|-------------|
| **Method** | Select and combine exact sentences from source | Generate new sentences that capture meaning |
| **Fidelity** | High — uses source's own words | Variable — risk of distortion |
| **Fluency** | May be choppy or repetitive | Naturally flowing |
| **Compression** | Limited to existing sentences | Can be much more compact |
| **Best for** | Legal, technical, or sensitive content | General content, articles, reports |
| **Risk** | May miss implied meaning | May introduce inaccuracies |

### When to Use Each

| Scenario | Recommended Approach |
|----------|---------------------|
| Legal/regulatory documents | Extractive (fidelity critical) |
| Research papers | Extractive for abstracts, abstractive for synthesis |
| News articles | Abstractive (readability important) |
| Meeting transcripts | Hybrid — extract key quotes, abstract discussion themes |
| Technical documentation | Extractive (precision matters) |
| Educational content | Abstractive (comprehension focus) |

---

## Progressive Summarization

### Five Levels of Compression

```
LEVEL 0 — ORIGINAL
├── Full source text, untouched
└── Use: Source material, verification

LEVEL 1 — BOLD HIGHLIGHTS
├── Key phrases and sentences bolded in original text
├── ~100% of original length, but scannable
└── Use: First pass, identifying what matters

LEVEL 2 — KEY POINTS
├── Bullet points of main ideas in your own words
├── ~20-30% of original length
└── Use: Quick reference, meeting notes, article summaries

LEVEL 3 — EXECUTIVE SUMMARY
├── 3-5 sentence paragraph capturing essence
├── ~5-10% of original length
└── Use: Briefings, overviews, decision support

LEVEL 4 — ONE-LINER
├── Single sentence distillation
├── ~1% of original length
└── Use: Headlines, tags, quick categorization
```

### Level Selection Guide

| Need | Level | Typical Length |
|------|-------|---------------|
| Detailed reference | Level 1 | Same as source |
| Meeting notes, article notes | Level 2 | 20-30% |
| Briefing, quick read | Level 3 | 5-10% |
| Headline, categorization | Level 4 | 1 sentence |

---

## Chain-of-Density (CoD)

### Method

Iteratively compress while tracking information density:

```
ROUND 1: Initial Summary
├── Length: ~200 words
├── Focus: Capture all key points
└── Missing: [note what was lost]

ROUND 2: Denser Summary  
├── Length: ~100 words (50% compression)
├── Focus: Merge related points, remove qualifiers
├── Merge candidates: [points that can combine]
└── Missing: [note additional losses]

ROUND 3: Maximum Density
├── Length: ~50 words (75% compression)
├── Focus: Only essential claims and data
├── Remaining structure: [core argument skeleton]
└── Trade-offs: [what was sacrificed and why]
```

### Density Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Information ratio** | Key facts per 100 words | Higher = denser |
| **Claim preservation** | % of original claims retained | >80% for good summary |
| **Distortion rate** | Claims changed or misrepresented | 0% target |
| **Redundancy reduction** | Repeated ideas collapsed | All redundancy removed |

---

## Key Point Extraction

### What to Extract

| Category | What to Look For | Priority |
|----------|-----------------|----------|
| **Thesis/Claim** | Main argument or conclusion | Critical |
| **Key Findings** | Results, data points, statistics | Critical |
| **Methodology** | How conclusions were reached | High |
| **Definitions** | Domain-specific terms defined | High |
| **Counter-arguments** | Limitations and objections addressed | Medium |
| **Implications** | What the findings mean in practice | Medium |
| **Resources** | Tools, references, or further reading | Low |

### Extraction Template

```
SUMMARY METADATA:
├── Source: [title/URL]
├── Author: [if available]
├── Date: [publication date]
├── Content type: [article/paper/report/transcript]
├── Original length: [word count]
└── Compression ratio: [summary/source as %]

KEY POINTS:
1. [Primary thesis/claim]
2. [Supporting finding or data point]
3. [Supporting finding or data point]
4. [Important caveat or limitation]
5. [Practical implication or next step]

NOTABLE DETAILS:
- [Specific statistic]: "[exact figure and context]"
- [Critical quote]: "[verbatim if impactful]"
- [Definition]: "[term] = [definition]"

OMITTED (with reason):
- [Topic]: [why omitted — detail level, tangential, etc.]
```

---

## Executive Summary Patterns

### Business Report Summary

```
EXECUTIVE SUMMARY

SITUATION: [1 sentence — what prompted this analysis]

KEY FINDINGS:
- [Finding 1 with specific data point]
- [Finding 2 with specific data point]
- [Finding 3 with specific data point]

RECOMMENDATION: [1-2 sentences — what to do next]

RISK: [1 sentence — key caveat or uncertainty]
```

### Research Summary

```
RESEARCH BRIEF

QUESTION: [What was investigated]

METHOD: [How it was studied — 1 sentence]

KEY FINDINGS:
1. [Primary result with confidence level]
2. [Secondary result]
3. [Tertiary result]

IMPLICATIONS: [What this means for the field/practice]

LIMITATIONS: [Key caveats that affect interpretation]

GAPS: [What remains unknown]
```

### Technical Document Summary

```
TECHNICAL SUMMARY

PURPOSE: [What this document covers]

KEY DECISIONS:
- [Decision 1]: [Rationale in 1 sentence]
- [Decision 2]: [Rationale in 1 sentence]

ARCHITECTURE: [1-2 sentence description of approach]

TRADE-OFFS:
- [Trade-off 1]: [Pro] vs [Con]
- [Trade-off 2]: [Pro] vs [Con]

ACTION ITEMS:
- [ ] [Required next step]
- [ ] [Required next step]
```

---

## Multi-Document Synthesis

### Combining Multiple Sources

```
SYNTHESIS PROCESS:
1. Summarize each source independently (Level 2)
2. Identify common themes across sources
3. Map agreements and contradictions
4. Note unique insights per source
5. Synthesize into unified summary
```

### Agreement Matrix

| Theme | Source A | Source B | Source C | Consensus? |
|-------|----------|----------|----------|-----------|
| [Theme 1] | Supports | Supports | Neutral | Yes (2/3) |
| [Theme 2] | Supports | Contradicts | Supports | Split — investigate |
| [Theme 3] | — | Supports | Supports | Emerging consensus |

### Synthesis Output Template

```
SYNTHESIS: [Topic]

OVERVIEW: [2-3 sentences synthesizing the landscape]

CONSENSUS POINTS (sources agree):
- [Point agreed upon by most sources]
- [Point agreed upon by most sources]

DISPUTED POINTS (sources disagree):
- [Point of disagreement]: Source A says X, Source B says Y

UNIQUE INSIGHTS:
- Source A: [insight not found elsewhere]
- Source B: [insight not found elsewhere]

GAPS: [What no source adequately addressed]

RECOMMENDATION: [Based on weight of evidence]
```

---

## Adaptive Compression

### Compression by Content Type

| Content Type | Strategy | Target Compression |
|-------------|----------|-------------------|
| **News article** | Lead paragraph + key facts | 10-15% |
| **Academic paper** | Abstract + key findings + methodology | 5-10% |
| **Legal document** | Key provisions + obligations + dates | 15-20% |
| **Technical docs** | Purpose + procedures + warnings | 10-15% |
| **Meeting transcript** | Decisions + action items + key discussion | 15-25% |
| **Email thread** | Final decision + key context | 10-20% |
| **Video transcript** | Key points + timestamps | 5-10% |

### Compression by Audience

| Audience | Emphasis | Omit |
|----------|----------|------|
| **Executive** | Bottom line, recommendations, ROI | Technical details, methodology |
| **Technical** | Implementation details, specifications | Business context, high-level overview |
| **General** | Key takeaways, practical implications | Jargon, detailed statistics |
| **Expert** | Novel findings, methodology nuances | Background, basic definitions |

---

## Quality Verification

### Fidelity Checklist

- [ ] All primary claims from source are represented
- [ ] No claims were added that aren't in the source
- [ ] Relative emphasis matches source (major points remain major)
- [ ] Numbers and statistics are exact (no rounding without noting)
- [ ] Quotes are verbatim or clearly paraphrased
- [ ] Tone is neutral — no editorial bias introduced
- [ ] Context is preserved — claims aren't stripped of caveats

### Common Summarization Errors

| Error | Description | Prevention |
|-------|-------------|------------|
| **Over-simplification** | Nuance lost in compression | Flag qualifiers and caveats explicitly |
| **Cherry-picking** | Only summarize parts you agree with | Systematic extraction from all sections |
| **Distortion** | Subtle meaning change during paraphrase | Compare summary claims against original |
| **Loss of uncertainty** | "May cause X" → "Causes X" | Preserve hedging language explicitly |
| **False synthesis** | Merge incompatible points from different contexts | Note which source each claim comes from |
| **Recency bias** | Overweight later sections over introduction | Extract from all sections proportionally |

---

## When to Use

- Creating executive summaries from reports or research
- Condensing articles, papers, or documents for quick consumption
- Extracting key points from meeting transcripts or conversations
- Synthesizing multiple sources into a unified overview
- Building progressive levels of detail for different audiences
- Compressing content for token-limited contexts

## Limitations

- Extractive summarization may produce choppy output
- Abstractive summarization risks introducing inaccuracies
- Heavy compression inevitably loses nuance — always flag what was omitted
- Multi-document synthesis requires careful source tracking to avoid false synthesis
- Cultural context and implied meaning are easily lost in summarization
- Statistical claims need exact preservation — rounding introduces error

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [content-extraction](../content-extraction/SKILL.md) | Extract clean content before summarizing |
| [reporting](../reporting/SKILL.md) | Structure summaries into formal reports |
| [data-synthesis](../data-synthesis/SKILL.md) | Combine and grade evidence from multiple sources |
| [critical-thinking](../critical-thinking/SKILL.md) | Evaluate claim quality before summarizing |
| [tapestry](../tapestry/SKILL.md) | Extract insights from content and create action plans |
| [deep-research](../deep-research/SKILL.md) | Summarize research findings at each stage |
