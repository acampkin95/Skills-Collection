---
name: source-evaluation
description: "Source credibility assessment, bias detection, fact-checking workflows, and evidence quality grading for non-CLI agents. Use when evaluating source reliability, detecting misinformation, cross-referencing claims, grading evidence quality, or assessing information integrity."
version: "1.0.0"
metadata:
  category: search-research
  scope: non-cli
---

# Source Evaluation & Evidence Grading

Assess the credibility, reliability, and quality of information sources. Essential for agents that must distinguish reliable information from misinformation, opinion, and low-quality content.

## Evidence Quality Framework

### Source Credibility Matrix

| Dimension | High (3) | Medium (2) | Low (1) |
|-----------|----------|------------|---------|
| **Authority** | Recognized expert, official org | Some expertise, known publisher | Anonymous, no credentials |
| **Accuracy** | Verifiable facts, cited sources | Mostly accurate, some gaps | Unsupported claims, errors |
| **Objectivity** | Balanced, discloses perspective | Mild bias, still useful | One-sided, manipulative |
| **Currency** | Published recently, updated | Recent enough for topic | Outdated for the subject |
| **Coverage** | Comprehensive, thorough | Adequate for the question | Superficial, incomplete |

**Credibility Score** = Average of all dimensions (1.0 - 3.0)
- 2.5-3.0: High confidence source
- 1.5-2.4: Use with caution, verify claims independently
- 1.0-1.4: Unreliable, do not use for factual claims

### Evidence Strength Scale

```
LEVEL A — CONCLUSIVE
├── Primary source (official docs, raw data, court records)
├── Multiple independent confirmations
└── Peer-reviewed research

LEVEL B — STRONG
├── Reputable secondary source with citations
├── 2+ independent sources agree
└── Official statements from authorities

LEVEL C — MODERATE
├── Single reputable source
├── Expert opinion with reasoning
└── Consistent with established knowledge

LEVEL D — WEAK
├── Single unverified source
├── Opinion without supporting evidence
└── Anonymous or unidentified source

LEVEL E — UNRELIABLE
├── No verifiable source
├── Contradicted by stronger evidence
└── Known misinformation vector
```

## Bias Detection

### Types of Bias to Check

| Bias Type | Indicators | Weight |
|-----------|------------|--------|
| **Financial** | Sponsored content, affiliate links, ads | High |
| **Political** | Loaded language, selective facts, framing | High |
| **Confirmation** | Only presents one side, cherry-picked data | Medium |
| **Recency** | Ignores historical context, novelty bias | Medium |
| **Availability** | Focuses on vivid/memorable examples | Medium |
| **Authority** | Over-relies on single expert/source | Low |
| **Survivorship** | Only shows successes, hides failures | Medium |

### Bias Detection Checklist

For each source, evaluate:

1. **Who benefits?** - Does the source gain from you believing this?
2. **What's omitted?** - What perspective or data is missing?
3. **Language check** - Emotional, loaded, or neutral language?
4. **Source diversity** - Does it cite opposing views?
5. **Self-correction** - Does the source correct its own errors?
6. **Financial ties** - Are there disclosed or apparent conflicts?
7. **Repetition pattern** - Is this just repeating other sources without original reporting?

### Language Analysis Patterns

```
RED FLAGS (suggests bias or low quality)
────────────────────────────────────────
- "Everyone knows that..."
- "Studies prove..." (without citing which studies)
- "Some people say..." (unattributed claims)
- Exclamation marks in factual content
- ALL CAPS for emphasis in serious content
- Clickbait headlines disconnected from content
- Absolute statements without qualification

GREEN FLAGS (suggests reliability)
──────────────────────────────────
- Specific citations and references
- "According to [source]..."
- Hedging language where appropriate ("may", "suggests")
- Acknowledgment of limitations
- Correction/updates noted
- Author identified with credentials
- Publication date clearly shown
```

## Fact-Checking Workflow

### Step-by-Step Process

```
CLAIM RECEIVED
      │
      ▼
┌──────────────┐
│ 1. DECOMPOSE │  Break claim into testable assertions
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 2. IDENTIFY  │  What type of claim? (fact, prediction, opinion, statistic)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 3. TRACE     │  Find the original source of the claim
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 4. VERIFY    │  Check against independent sources
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 5. GRADE     │  Assign evidence strength level
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 6. CONTEXT   │  Add nuance, conditions, caveats
└──────────────┘
```

### Claim Type Assessment

| Claim Type | Verification Method | Example |
|------------|-------------------|---------|
| **Statistical** | Find original study, check methodology | "90% of users prefer..." |
| **Historical** | Cross-reference established records | "The law was passed in..." |
| **Scientific** | Check peer review, replication | "Studies show that..." |
| **Predictive** | Assess track record, base rates | "Will grow by 200%..." |
| **Opinion** | Identify as opinion, assess reasoning | "Is the best approach..." |
| **Anecdotal** | Note as anecdote, don't generalize | "In my experience..." |

## Cross-Reference Patterns

### Triangulation Matrix

For key claims, verify from multiple angles:

```
                    Source A    Source B    Source C
Claim: "X is true"
  - Supports           ✓          ✓          ✗
  - Contradicts                             ✓
  - Neutral            ○                     ○
  - Strength           B          A          C
  
VERDICT: Likely true (2/3 support, strongest source agrees)
CAVEAT: Source C disagrees — investigate their reasoning
```

### When Sources Disagree

1. **Check methodology** - How did each source reach their conclusion?
2. **Check recency** - Is one source more current?
3. **Check authority** - Which source has deeper expertise?
4. **Check independence** - Are they independently derived or copying each other?
5. **Check scope** - Are they actually making claims about different things?

## Special Source Types

### AI-Generated Content Detection

Signals that content may be AI-generated:
- Perfectly balanced paragraphs of similar length
- Hedging language used uniformly
- Lack of specific personal experience
- Generic examples without concrete details
- No strong opinions or unusual perspectives
- Perfect grammar with no personality

**Rule:** AI-generated content is NOT a primary source. Treat it as a summary that must be verified against original sources.

### Social Media as Sources

| Platform | Credibility Use | Best For |
|----------|-----------------|----------|
| Twitter/X | Low-Medium | Breaking news (verify), expert commentary |
| Reddit | Low-Medium | Community sentiment, first-hand accounts |
| LinkedIn | Medium | Professional opinions, company announcements |
| YouTube | Low-Medium | Tutorials, presentations, interviews |
| Wikipedia | Medium | Overview, finding primary sources via citations |

**Always verify social media claims through independent sources.**

## URL & Domain Credibility Heuristics

```
HIGH CREDIBILITY INDICATORS:
├── .gov, .edu, .mil domains (official, institutional)
├── Well-known publisher domains (reuters.com, nature.com)
├── Official project domains (react.dev, python.org)
├── Academic institution domains with ~/~faculty paths
└── Established API/documentation domains

MEDIUM CREDIBILITY INDICATORS:
├── .org domains (verify it's the real organization)
├── Medium.com, Substack.com (check author credentials)
├── Personal domains with established author history
└── Company blogs (potential financial bias)

LOW CREDIBILITY INDICATORS:
├── Newly registered domains (< 1 year)
├── Domains mimicking real ones (g00gle.com, faceb00k.com)
├── Excessive hyphens or numbers in domain name
├── URL shorteners hiding the real destination
└── domains ending in .tk, .ml, .ga, .cf (often free/abused)
```

## Misinformation Pattern Recognition

### Common Misinformation Patterns

```
HEADLINE PATTERNS:
├── "They don't want you to know..."     → Conspiracy framing
├── "What [GROUP] is hiding..."          → Us-vs-them framing
├── "Scientists hate this one trick..."  → Anti-intellectual framing
├── "SHOCKING truth about..."            → Emotional manipulation
└── "Mainstream media won't report..."   → Anti-institution framing

CONTENT PATTERNS:
├── No author byline or publication date
├── No outbound links to primary sources
├── Emotional language disproportionate to facts
├── Only anonymous sources cited
├── Appeals to "common sense" over evidence
└── False equivalence (presenting fringe view as equal to consensus)

STRUCTURAL PATTERNS:
├── Content farm signals (SEO-optimized, low depth)
├── Content copied verbatim across multiple sites
├── Ads outnumbering actual content
├── Pop-ups demanding email/share before reading
└── No "About" page or editorial policy
```

### Adversarial Source Assessment

```
STATE-SPONSORED MEDIA SIGNALS:
├── Government-funded or government-owned
├── Selective reporting that aligns with state interests
├── Omission of stories unfavorable to the state
├── Amplification of stories favorable to the state
├── Note: state-funded ≠ unreliable (BBC, NPR) — check editorial independence
└── Consult: Press Freedom Index, Media Bias/Fact Check

ASTROTURFING SIGNALS:
├── Coordinated messaging across multiple "independent" accounts
├── Newly created accounts with high posting volume
├── Identical talking points appearing simultaneously
├── Lack of genuine engagement history
└── Template-like responses with slight variations

DEEPFAKE / SYNTHETIC MEDIA:
├── Unnatural lighting or shadow inconsistencies
├── Blurring at face edges or unnatural skin texture
├── Inconsistent audio-visual sync
├── Unusual eye blinking patterns
├── Metadata analysis (EXIF data, creation tools)
└── Reverse image search to find originals
```

## Source Citation Format

When citing sources in output:

```
[CLAIM] → [SOURCE NAME] ([DATE]) — [EVIDENCE GRADE]
Example: "React Server Components reduce bundle size by 40%" 
  → Vercel Blog (Mar 2025) — Level B
  → corroborated by Kent C. Dodds (Apr 2025) — Level B
```


## When to Use

- Evaluating credibility of web sources before citing them
- Detecting bias, misinformation, or outdated information
- Fact-checking claims found during research
- Building evidence chains with rated source quality
- Deciding whether a source is trustworthy enough to reference

## Limitations

- Subjective quality ratings require human judgment for borderline cases
- Cannot verify claims behind paywalls or authentication walls
- Bias detection is probabilistic, not deterministic
- Temporal relevance decays rapidly for fast-moving fields

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-research](../web-research/SKILL.md) | Source evaluation is part of the broader research workflow |
| [data-synthesis](../data-synthesis/SKILL.md) | Source quality ratings inform synthesis confidence levels |
| [deep-research](../deep-research/SKILL.md) | Systematic evaluation of academic and technical literature |
| [reporting](../reporting/SKILL.md) | Cite evaluated sources in report reference sections |
