---
name: web-research
description: "Systematic web research methodology for non-CLI agents. Covers search strategies, query formulation, multi-source triangulation, evidence chains, iterative refinement, and research workflow management. Use this skill when conducting web research, systematic information gathering, multi-source analysis, literature review, or any task requiring structured knowledge acquisition from the web."
version: "1.0.0"
metadata:
  category: search-research
  scope: non-cli
---

# Web Research Methodology

Systematic approach to acquiring, evaluating, and synthesizing information from web sources. Designed for agents that research without terminal access.

## Core Principles

1. **Triangulate everything** - Never rely on a single source for factual claims
2. **Search breadth before depth** - Cast wide, then narrow
3. **Trace to primary sources** - Find the original, not the summary
4. **Time-aware sourcing** - Recent events need recent sources; established facts accept older ones
5. **Document the chain** - Every claim should trace back to its source

## Research Workflow

### Phase 1: Scoping

Define what you need before searching:

```
RESEARCH SCOPE TEMPLATE
───────────────────────
Topic:          [What you're researching]
Questions:      [Specific questions to answer]
Constraints:    [Time period, geography, domain]
Output:         [What format the answer needs]
Depth:          [Quick answer | Standard report | Deep dive]
```

### Phase 2: Broad Discovery

Start with wide searches to map the landscape:

| Strategy | When to Use | Approach |
|----------|-------------|----------|
| **Wide net** | Unfamiliar topic | 3-5 broad queries, scan top results |
| **Known entity** | Specific company/tool/person | Direct search, official sources first |
| **Comparison** | Evaluating options | Search for each option + "vs" queries |
| **How-to** | Learning a process | Search for tutorials, docs, guides |
| **Current events** | Breaking news | Time-filtered search, multiple outlets |

### Phase 3: Query Formulation

Craft effective queries using these patterns:

```
BAD:  "javascript frameworks"
GOOD: "best JavaScript framework for enterprise SPA 2025 comparison"

BAD:  "how to do auth"
GOOD: "Next.js 15 authentication best practices server components"

BAD:  "python fast"
GOOD: "Python web framework performance benchmark 2024 2025"
```

**Query modifiers for precision:**
- Add year/date for currency: `"2025"` or `"2024 2025"`
- Use quotes for exact phrases: `"exact phrase match"`
- Add context words: `"production"`, `"best practices"`, `"guide"`
- Combine with operators: `AND`, `OR`, `-exclude`

### Phase 4: Source Triage

Evaluate sources in order of priority:

```
SOURCE HIERARCHY (descending authority)
────────────────────────────────────────
1. Official documentation / primary sources
2. Peer-reviewed papers / established references
3. Reputable publishers (MDN, official blogs, established media)
4. Well-cited community content (Stack Overflow, GitHub)
5. Individual blogs / opinion pieces
6. Social media / forums (verify independently)
```

**Quick credibility check:**
- Does the source cite its own references?
- Is the author identifiable with relevant expertise?
- Is the publication date current for the topic?
- Does the URL suggest authority (official domain, .edu, .gov)?

### Phase 5: Deep Dive

For each relevant source found:

1. **Extract key claims** - What assertions does this source make?
2. **Identify evidence** - What supports those claims?
3. **Note contradictions** - Where does this disagree with other sources?
4. **Flag assumptions** - What does this source take for granted?
5. **Rate confidence** - How certain is this source?

### Phase 6: Synthesis

Combine findings into coherent output:

```
SYNTHESIS FRAMEWORK
───────────────────
Consensus:     [What most sources agree on]
Disagreement:  [Where sources diverge and why]
Gaps:          [What no source adequately addresses]
Confidence:    [Overall certainty level: High/Medium/Low]
Recommendation:[What the evidence supports]
```

## Search Strategy Patterns

### Iterative Refinement

```
Round 1: Broad topic queries → identify key concepts and terminology
Round 2: Refined queries with discovered terminology → deeper results
Round 3: Targeted queries for specific gaps → fill holes
Round 4: Verification queries → confirm key claims
```

### Multi-Engine Strategy

Different search tools surface different results:

| Tool | Strengths | Use For |
|------|-----------|---------|
| General search | Breadth, speed | Initial discovery |
| Academic search | Peer-reviewed, citations | Scientific claims |
| Code search | Implementations, patterns | How things are actually built |
| News search | Current events | Recent developments |
| Social search | Opinions, discussions | Community sentiment |

### The "Five Source Rule"

For any significant claim, aim to find it confirmed by at least:
- 2 independent primary/authoritative sources
- 1 secondary source with its own citations
- 1 source from a different perspective or domain
- 1 recent source confirming currency

## Research for Different Output Types

### Quick Answer (5-10 minutes)
- 2-3 targeted searches
- Top 3-5 results per search
- Single-pass synthesis
- Confidence: Medium

### Standard Report (30-60 minutes)
- 5-8 searches across different angles
- 10-15 sources evaluated
- Multi-round refinement
- Triangulated claims
- Confidence: Medium-High

### Deep Research (2+ hours)
- 15-25 systematic searches
- 25-50 sources evaluated
- Full iterative refinement
- Primary source tracing
- Contradiction mapping
- Confidence: High

## Advanced Search Techniques

### Search Operator Reference

```
OPERATOR          EFFECT                           EXAMPLE
─────────────────────────────────────────────────────────────────
"exact phrase"    Match exact phrase                "serverless architecture"
-site:domain      Exclude a site                    -site:wikipedia.org
site:domain       Restrict to site                  site:github.com
filetype:ext      Find specific file types          filetype:pdf "annual report"
intitle:word      Word must be in title             intitle:"best practices"
inurl:word        Word must be in URL               inurl:docs react
related:domain    Find similar sites                related:mdn.mozilla.org
before:YYYY-MM-DD  Results before date             before:2025-01-01
after:YYYY-MM-DD   Results after date              after:2025-06-01
OR                Boolean OR                        react OR vue OR angular
-cache:url        Google's cached version           cache:example.com
*                 Wildcard in phrase                "how to * a website"
AROUND(X)         Terms within X words of each     "react" AROUND(3) "performance"
```

### Research Planning Matrix

```
TOPIC DIMENSION → SEARCH STRATEGY
───────────────────────────────────
Technical accuracy  → Official docs, GitHub issues, changelogs
Market landscape    → Analyst reports, competitor comparison, news
User sentiment      → Reddit, HN, Twitter, product reviews
Historical context  → Archives, Wayback Machine, academic papers
Legal/regulatory    → Government sites, legal databases, court records
Statistical data    → Census, WHO, World Bank, Pew Research, Statista
Security/advisory   → CVE databases, vendor advisories, NIST
```

### Citation Chaining

```
FORWARD CHAINING (who cited this?):
  Found good paper → Search for papers that cite it → Newer research

BACKWARD CHAINING (what did this cite?):
  Found good paper → Read its references → Foundational sources

LATERAL CHAINING (who else works on this?):
  Found good author → Search their other work → Related research group

PRACTICAL TECHNIQUE:
  1. Start with one high-quality source
  2. Extract its key citations
  3. Search for those citations + newer work citing the original
  4. Map the knowledge graph of the topic
```

### Research for Specialized Domains

| Domain | Priority Sources | Key Databases |
|--------|-----------------|---------------|
| **Medical** | PubMed, Cochrane, WHO, CDC | PubMed Central, ClinicalTrials.gov |
| **Legal** | Court records, legislation, law reviews | Google Scholar, court databases |
| **Technical** | Official docs, RFCs, W3C specs | MDN, GitHub, Stack Overflow |
| **Financial** | SEC filings, central banks, IMF | EDGAR, World Bank Open Data |
| **Academic** | Peer-reviewed journals, dissertations | Google Scholar, arXiv, SSRN |

## Common Pitfalls

| Pitfall | Detection | Fix |
|---------|-----------|-----|
| **Echo chamber** | Multiple sources repeat same claim without independent verification | Trace to original source; find independent confirmation |
| **Recency bias** | Only recent results considered | Check if older sources have foundational insights |
| **Authority bias** | Over-weighting official sources | Cross-check official claims with independent sources |
| **Confirmation bias** | Only finding sources that support initial hypothesis | Deliberately search for opposing views |
| **Source conflation** | Treating opinion as fact | Classify each source by type (fact, opinion, analysis, advertisement) |
| **Lost in the weeds** | Spending too long on minor details | Set time limits per sub-topic; return to scope document |

## Quality Checklist

Before delivering research output:

- [ ] Every factual claim has at least one source citation
- [ ] Controversial claims have multiple independent sources
- [ ] Sources span different domains/perspectives
- [ ] Recent claims use recent sources
- [ ] Contradictions between sources are acknowledged
- [ ] Confidence level is stated for key findings
- [ ] Limitations and gaps are identified
- [ ] The original research questions are all addressed


## When to Use

- Conducting web research or systematic information gathering
- Multi-source analysis and triangulation
- Literature review or state-of-the-art surveys
- Preparing background research before making recommendations
- Answering questions that require up-to-date web knowledge

## Limitations

- Cannot execute searches directly — relies on agent's available search tools
- Quality of output depends on search tool capabilities and source accessibility
- Paywalled or gated content may be inaccessible
- Real-time data (stock prices, breaking news) may have latency

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [source-evaluation](../source-evaluation/SKILL.md) | Evaluate credibility and bias of sources found during research |
| [deep-research](../deep-research/SKILL.md) | Extended multi-phase research requiring gap analysis and knowledge mapping |
| [data-synthesis](../data-synthesis/SKILL.md) | Combine findings from multiple research sources into coherent output |
| [web-fetching](../web-fetching/SKILL.md) | Retrieve specific URLs identified during research |
| [content-extraction](../content-extraction/SKILL.md) | Extract structured data from pages found during research |
