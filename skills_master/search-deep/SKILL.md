---
name: search-deep
description: Deep research and source-grounded answers. Use when the user asks for "research", "find out", "look up", "what's the latest", or needs verified factual information with sources.
user-invocable: true
---

# Deep Research — Verified, Source-Grounded Answers

Use this skill when the user needs factual, verified information rather than a guess. Every claim should trace back to a named source.

## When to Use

- User asks for research, facts, or verification
- Claims need to be substantiated (legal, medical, technical, financial)
- "What does the research say about...", "Find out...", "Look up..."
- Decision-making information (not just general knowledge)
- Australian context (ATO, law, health, government)

## Research Stack (Escalation Order)

```
1. Browser / Knowledge (default) → General knowledge, no verification needed
2. fetch_content → Known URLs, authoritative sources (docs, government, academic)
3. web_search → Discovery, multiple perspectives, recent information
4. Crawl4AI → Bulk content from complex sites, structured extraction
5. Knowledge-based writing → Well-established domain knowledge (trained data)
```

## Research Protocol

### Step 1 — Scope the query

```python
# Parse the user's information need
query_type = {
    "factual": "Australian tax law, ATO rules, legislation",
    "academic": "Research papers, studies, datasets",
    "product": "Documentation, API references, tutorials",
    "news": "Recent developments, current events",
    "opinion": "Multiple perspectives, expert views"
}

# Pick strategy based on type
```

### Step 2 — Find sources (web_search first)

```
Query structure:
- "site:gov.au [topic]" for Australian government
- "site:austlii.edu.au [topic]" for Australian law
- "site:ato.gov.au [topic]" for tax
- "site:health.gov.au OR site.servicesaustralia.gov.au [topic]"
- "site:huggingface.co OR site:github.com [topic]" for tech
```

### Step 3 — Fetch authoritative content

```bash
# Fetch from known authoritative URLs
fetch_content --url "https://www.ato.gov.au/..." --prompt "Extract rules about [topic]"
fetch_content --url "https://www.austlii.edu.au/cgi/view/legis/wa_show_repts" --prompt "..."
```

### Step 4 — Synthesize with citations

```
Format:
## Answer
[concise, direct answer to the question]

## Sources
1. [Source name](URL) — [what it says about this topic]
2. [Source name](URL) — [additional source]

## Caveats
- [Any limitations, conflicting information, or uncertainty]
```

### Step 5 — Verify before claiming

```
Checklist:
☐ Source is authoritative (gov.au, austlii, academic, major organisation)
☐ Source date is current (within 2 years for fast-moving topics)
☐ Information is consistent across multiple sources
☐ Limitations/caveats are stated
☐ Claims are attributed, not paraphrased as fact
```

## Source Quality Tiers

| Tier | Examples | Use For |
|------|---------|---------|
| **Primary** | ATO, AustLII, government agencies, peer-reviewed | Legal, financial, health decisions |
| **Secondary** | Major organisations (RACGP, ASIC, Law Society) | Professional guidance |
| **Tertiary** | News, blogs, community forums | Context, not decisions |
| **Unknown** | Generic web, anonymous sources | Verify or discard |

## Australian Context Traps

- Legislation changes frequently — always verify date
- State vs Commonwealth law — jurisdiction matters
- "Information" vs "advice" — distinguish clearly
- ATO rulings vs tax law — rulings can change
- Medical information vs clinical advice

## Output Template for Research

```markdown
## Research: [Question]

**Scope:** [What was searched and why]
**Date:** [Today's date]
**Confidence:** [High/Medium/Low — based on source quality]

### Answer
[Direct answer, no hedging on facts]

### Key Sources
- [Source 1](URL) — [relevant detail from source]
- [Source 2](URL) — [relevant detail]

### Important Caveats
- [Limitation 1]
- [Limitation 2]

### Further Research Needed
- [If applicable, what wasn't found]
```

## Anti-Hallucination Rules

1. **Never fabricate citations** — only cite what you actually retrieved
2. **Use attribution markers** — "According to the ATO...", "The legislation states..."
3. **Distinguish knowledge from retrieval** — "My training data suggests X, but let me verify" → then fetch
4. **Flag uncertainty** — "This may have changed since my training data" for time-sensitive topics
5. **Default to search** when the user asks for "current", "latest", "recent", or "what's the rule now"