# Research Methodology Guide

This document outlines the research methodology standards and practices for the Multi-Agent Planner system. All research activities should follow these guidelines to ensure quality, reproducibility, and reliability.

## Table of Contents

1. [Research Planning](#research-planning)
2. [Source Evaluation](#source-evaluation)
3. [Citation Standards](#citation-standards)
4. [Bias Detection](#bias-detection)
5. [Data Verification](#data-verification)
6. [Research Workflow](#research-workflow)
7. [Quality Metrics](#quality-metrics)

---

## Research Planning

### Defining Research Objectives

Before starting any research, clearly define the scope and objectives:

```
Research Planning Checklist:
  [ ] State the primary research question
  [ ] Identify key sub-questions or hypotheses
  [ ] Define the target audience and use case
  [ ] Set boundaries (what's in scope, what's out of scope)
  [ ] Estimate time and resource requirements
  [ ] Identify required expertise domains
```

### Research Question Framework

Use the PICO framework for structured research questions:

| Component | Description | Example |
|-----------|-------------|---------|
| **P** - Population | Who or what is being studied? | Software developers using AI tools |
| **I** - Intervention | What action or treatment? | Claude Code CLI implementation |
| **C** - Comparison | What is the alternative? | Traditional development workflows |
| **O** - Outcome | What results are expected? | Productivity improvements, error reduction |

### Research Scope Matrix

| Scope Level | Description | Use Case |
|-------------|-------------|----------|
| **Quick Lookup** | Single query, under 2 minutes | Fact verification, definitions |
| **Standard Search** | 3-5 queries, 10-30 minutes | Topic overview, comparison |
| **Deep Research** | 10+ queries, 1-4 hours | Comprehensive analysis, reports |
| **Extended Investigation** | Multi-day, multiple sources | Academic research, white papers |

---

## Source Evaluation

### Source Credibility Assessment

Evaluate each source using the CRAAP test:

| Criterion | Questions to Ask | Weight |
|-----------|------------------|--------|
| **Currency** | When was it published? Is it recent enough? | 20% |
| **Relevance** | Does it directly address the research question? | 25% |
| **Authority** | Who is the author/organization? Are they expert? | 20% |
| **Accuracy** | Is it supported by evidence? Peer-reviewed? | 20% |
| **Purpose** | Is there bias? Educational, commercial, political? | 15% |

### Source Hierarchy

```
TIER 1: Primary Sources (Highest Value)
  - Original research papers
  - Official documentation
  - Government/statistical data
  - Expert firsthand accounts

TIER 2: Secondary Sources (High Value)
  - Academic reviews/meta-analyses
  - Industry analysis reports
  - Documentation from major projects
  - Expert interviews/quotes

TIER 3: Tertiary Sources (Medium Value)
  - News articles
  - Blog posts
  - Wikipedia (as starting point only)
  - Social media discussions

TIER 4: User-Generated Content (Lower Value)
  - Forum posts
  - Comments/reviews
  - Q&A sites (verify with primary sources)
```

### Source Validation Checklist

```markdown
Source Validation Criteria:
  [ ] Verify author credentials and expertise
  [ ] Check publication date and relevance
  [ ] Look for citations and references
  [ ] Cross-reference with other sources
  [ ] Check for peer review or editorial process
  [ ] Assess funding sources and potential conflicts
  [ ] Evaluate methodology if applicable
  [ ] Note any corrections or retractions
```

---

## Citation Standards

### Citation Format Requirements

All research must include citations in the following format:

```json
{
  "source_id": "unique-identifier",
  "url": "https://example.com/source",
  "title": "Source Title",
  "author": "Author Name(s)",
  "publication": "Publication Name",
  "date_published": "YYYY-MM-DD",
  "accessed_at": "YYYY-MM-DD",
  "content_type": "type (web, academic, report, etc.)",
  "relevance_score": 0.0-1.0,
  "snippet": "Brief quote or summary (max 200 chars)",
  "verification_status": "verified|pending|uncertain"
}
```

### Citation Numbering System

Use sequential numbering for inline citations:

- **[1]** - First source cited
- **[2]** - Second source cited
- **[1-3]** - Multiple consecutive sources

### Bibliography Format

```
APA Style for References:

Author, A. A. (Year). Title of article. Title of Journal, volume(issue), page range. DOI

Example:
Smith, J. D. (2024). AI-assisted software development. Journal of DevOps, 12(3), 45-67.

Web Source:
Author, A. A. (Year, Month Day). Page title. Site Name. URL
```

### Citation Quality Rules

1. **Primary Citation Requirement**: At least 60% of citations must be from Tier 1 or Tier 2 sources
2. **Recency Requirement**: At least 70% of sources should be from the last 3 years
3. **Diversity Requirement**: Include at least 3 different publication types
4. **Verification Requirement**: Mark all citations as verified or explain why verification is pending

---

## Bias Detection

### Types of Bias to Watch For

| Bias Type | Description | Detection Method |
|-----------|-------------|------------------|
| **Confirmation Bias** | Favoring information that confirms existing beliefs | Check for balanced viewpoint coverage |
| **Selection Bias** | Non-random sample selection | Examine methodology and participant selection |
| **Publication Bias** | Positive results more likely published | Look for null/negative results |
| **Commercial Bias** | Industry-funded research | Check funding sources and disclosures |
| **Geographic Bias** | Over-representation of certain regions | Assess global perspective |
| **Temporal Bias** | Overemphasis on recent events | Balance historical and current sources |
| **Linguistic Bias** | English-language dominance | Include non-English sources when relevant |

### Bias Assessment Framework

```
Bias Detection Checklist:
  [ ] Does the source present multiple viewpoints?
  [ ] Are counterarguments addressed?
  [ ] Is funding/affiliation disclosed?
  [ ] Are statistics presented with context?
  [ ] Is emotional language used appropriately?
  [ ] Are limitations acknowledged?
  [ ] Can you identify the target audience?
```

### Mitigation Strategies

1. **Multi-source triangulation**: Use 3+ independent sources
2. **Adversarial sourcing**: Actively seek contradictory evidence
3. **Blind review**: Have another agent review sources
4. **Source diversity audit**: Check for demographic/ideological diversity
5. **Temporal balance**: Include historical and recent perspectives

---

## Data Verification

### Verification Hierarchy

```
VERIFICATION LEVELS:

Level 1: Self-Verification
  - Cross-reference with 2+ additional sources
  - Check official documentation
  - Verify with primary data when possible

Level 2: Expert Verification
  - Consult subject matter experts
  - Review by qualified professionals
  - Check with authoritative institutions

Level 3: Empirical Verification
  - Reproduce experiments/data analysis
  - Test claims with practical implementation
  - Collect primary data

Level 4: Consensus Verification
  - Check for community agreement
  - Review meta-analyses and systematic reviews
  - Assess consensus in scientific literature
```

### Fact-Checking Protocol

```python
def verify_fact(claim: str, sources: list[Citation]) -> VerificationResult:
    """
    Verify a factual claim against sources.

    Args:
        claim: The statement to verify
        sources: List of citations supporting the claim

    Returns:
        VerificationResult with status and confidence
    """
    verified_sources = []
    conflicting_sources = []

    for source in sources:
        if claim_in_source(claim, source):
            if source.relevance_score > 0.7:
                verified_sources.append(source)
        else:
            conflicting_sources.append(source)

    if len(verified_sources) >= 3:
        return VerificationResult(status="VERIFIED", confidence=0.95)
    elif len(verified_sources) >= 1:
        return VerificationResult(status="PARTIALLY_VERIFIED", confidence=0.6)
    else:
        return VerificationResult(status="UNVERIFIED", confidence=0.0)
```

### Data Quality Indicators

| Indicator | Good | Poor |
|-----------|------|------|
| **Sample Size** | n > 100 or clearly justified | n < 30 without justification |
| **Methodology** | Clearly described, replicable | Vague or missing |
| **Statistical Significance** | p-values reported, CI given | Claims without statistics |
| **Peer Review** | Published in peer-reviewed venue | Preprint without review |
| **Reproducibility** | Code/data available | Not shared |

---

## Research Workflow

### Standard Research Process

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: INITIALIZATION                                         │
│  ├── Define research question                                    │
│  ├── Identify key terms and search strategy                      │
│  └── Set success criteria                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: DISCOVERY                                              │
│  ├── Execute initial Perplexity search                           │
│  ├── Gather broad range of sources                               │
│  └── Screen sources for relevance                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: EVALUATION                                             │
│  ├── Apply source hierarchy assessment                           │
│  ├── Evaluate credibility (CRAAP test)                           │
│  ├── Detect potential biases                                     │
│  └── Mark sources as verified/pending                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: VERIFICATION                                           │
│  ├── Cross-reference claims                                      │
│  ├── Verify critical facts                                       │
│  └── Document verification status                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: SYNTHESIS                                              │
│  ├── Organize findings by theme/topic                            │
│  ├── Identify consensus and conflicts                            │
│  └── Generate synthesis report                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 6: OUTPUT                                                 │
│  ├── Generate final report with citations                        │
│  ├── Include confidence levels                                   │
│  ├── Document limitations                                        │
│  └── Archive sources and methodology                             │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow State Tracking

```yaml
research_state:
  phase: "synthesis"
  progress: 0.75
  sources_collected: 25
  sources_verified: 18
  sources_pending: 7
  citations_generated: 32
  quality_score: 0.85
  estimated_completion: "2024-01-15T16:00:00Z"
```

---

## Quality Metrics

### Research Quality Score

Calculate overall quality score:

```
Quality Score = (C * 0.3) + (V * 0.3) + (B * 0.2) + (D * 0.2)

Where:
  C = Citation Quality (0-1)
  V = Verification Coverage (0-1)
  B = Bias Management (0-1)
  D = Data Quality (0-1)
```

### Quality Thresholds

| Score Range | Rating | Action Required |
|-------------|--------|-----------------|
| 0.90-1.00 | Excellent | None |
| 0.75-0.89 | Good | Minor improvements |
| 0.60-0.74 | Fair | Significant revisions |
| 0.40-0.59 | Poor | Major rework |
| 0.00-0.39 | Unacceptable | Reject and restart |

### Quality Checklist

```markdown
Final Review Checklist:
  [ ] Research question clearly defined and answered
  [ ] Minimum 5 high-quality sources cited
  [ ] All critical claims verified
  [ ] Bias assessment completed
  [ ] Sources properly documented
  [ ] Limitations acknowledged
  [ ] Confidence levels stated
  [ ] Recommendations actionable
  [ ] Quality score > 0.75
```

---

## Tool Integration

### Perplexity Integration

Use Perplexity AI for:
- Initial broad searches
- Deep research on complex topics
- Quick fact verification
- Literature discovery

### Web Fetch Integration

Use Web Fetch for:
- Retrieving full source documents
- Accessing paywalled content
- Gathering quantitative data
- Direct documentation access

### Citation Management

Store all citations in:
```
/aistore/research/citations/
  ├── citations_index.json
  ├── by_topic/
  │   ├── topic_a.json
  │   └── topic_b.json
  └── verification_status.json
```

---

## Summary

This methodology ensures that all research conducted by the Multi-Agent Planner system meets high standards of quality, reliability, and reproducibility. By following these guidelines, agents can produce research outputs that are:

- **Credible**: Based on authoritative, verified sources
- **Transparent**: Fully documented methodology and citations
- **Balanced**: Multiple perspectives, bias-aware
- **Actionable**: Clear recommendations with confidence levels
- **Reproducible**: Others can verify and extend the work

---

**Last Updated**: January 2025
**Version**: 1.0
