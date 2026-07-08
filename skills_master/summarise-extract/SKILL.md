---
name: summarise-extract
description: Summarise long documents, extract key points, compare texts. Use when the user shares a document, PDF, article, or text and asks to "summarise", "extract key points", "what are the main points", "TL;DR", or "compare these".
user-invocable: true
---

# Summarise & Extract — Document Condensation

Use this skill when the user provides text, a document, or a link and wants it condensed, key points extracted, or compared against something else.

## When to Use

- User pastes a long article, email, document, or transcript
- "TL;DR", "summarise", "what are the main points"
- "Extract the key information from..."
- "Compare this to..."
- "What did [document] say about [topic]"
- Long conversations that need condensing

## Summarisation Strategies

### Executive Summary (Best for Decisions)

```python
def executive_summary(text: str, max_words: int = 150) -> str:
    """
    Returns: 1-sentence conclusion + 3-5 key points + context
    Use when: user needs to make a decision or brief someone
    """
    # 1. First sentence = what this is about
    # 2. 3-5 bullets = most important facts, figures, decisions
    # 3. 1 sentence = what to do with this information
```

### Key Points Extraction (Best for Research)

```python
def key_points(text: str, n_points: int = 7) -> list:
    """
    Returns: list of standalone insights
    Use when: user is researching, learning, or gathering information
    """
    # Extract: definitions, rules, exceptions, numbers, dates, names
    # Each point should be self-contained (understandable alone)
    # Prioritise: first mention of concepts, exceptions, numbers
```

### Comparison Summary (Best for Analysis)

```python
def compare_texts(text_a: str, text_b: str) -> dict:
    """
    Returns: {similarities: [], differences: [], verdict: str}
    Use when: user wants to know how two things stack up
    """
    # Side-by-side comparison of key dimensions
    # Highlight conflicts, confirm alignment, note gaps
```

### Quote Extraction (Best for Evidence)

```python
def extract_quotes(text: str, topic: str) -> list:
    """
    Returns: list of exact quotes relevant to topic
    Use when: user needs to cite or reference the original text
    """
    # Include: exact quote, page/section reference, context
    # Never paraphrase as a quote
```

## Document Size Routing

| Length | Strategy |
|--------|----------|
| < 500 words | Full read, complete summary |
| 500–2,000 words | Section headers, key paragraphs |
| 2,000–10,000 words | Chunk by headings, extract per section |
| > 10,000 words | Auto-summarise (LLM), then key extraction |
| PDF/image | Use OCR/DeepInfra first, then summarise |

## Extraction Framework

```python
def extract_from_document(text: str, doc_type: str) -> dict:
    """Domain-specific extraction patterns."""
    
    if doc_type == "legal":
        return {
            "parties": extract_parties(text),
            "dates": extract_dates(text),
            "legislation": extract_citations(text),
            "outcomes": extract_orders_outcomes(text),
            "deadlines": extract_time_limits(text)
        }
    
    elif doc_type == "financial":
        return {
            "amounts": extract_currency_amounts(text),
            "dates": extract_dates(text),
            "entities": extract_organisations(text),
            "clauses": extract_key_provisions(text)
        }
    
    elif doc_type == "technical":
        return {
            "requirements": extract_requirements(text),
            "dependencies": extract_dependencies(text),
            "steps": extract_steps_procedures(text),
            "errors": extract_error_conditions(text)
        }
    
    elif doc_type == "academic":
        return {
            "claims": extract_main_arguments(text),
            "methods": extract_methodology(text),
            "data": extract_data_results(text),
            "sources": extract_citations(text)
        }
}
```

## Summary Output Formats

### Bullet Summary (Default)

```markdown
## Summary

**What this is:** [1 sentence]

**Key points:**
- [Point 1 — specific and actionable]
- [Point 2 — includes any numbers, names, dates]
- [Point 3 — includes exceptions or conditions]
- [Point 4 — consequence or next step]
- [Point 5 — what this means for the user]

**Bottom line:** [1 sentence recommendation or conclusion]
```

### Table Summary (Comparisons)

```markdown
## Comparison: [A vs B]

| Aspect | [A] | [B] |
|--------|-----|-----|
| [Aspect 1] | [A detail] | [B detail] |
| [Aspect 2] | [A detail] | [B detail] |

**Verdict:** [Which wins for what use case]
```

### Quote Bank (Evidence)

```markdown
## Key Quotes on [Topic]

> **"Exact quote from source."**
> — [Document name], [section/page], [date if relevant]

> **"Second relevant quote."**
> — [Source], ...
```

## Length Calibration

| User said | Output target |
|-----------|--------------|
| "TL;DR" | 2-3 sentences |
| "quick summary" | 3-5 bullet points |
| "summarise" | 1 paragraph + key points |
| "detailed summary" | Full structure with all sections |
| "key points" | List of standalone insights |
| "main takeaways" | Action-oriented conclusions |

## Anti-Summarisation Failure Rules

1. **Don't lose specifics** — numbers, names, dates, and rules must survive
2. **Preserve nuance** — "may" stays "may", not "will"
3. **Keep exceptions** — qualifications and conditions are key
4. **Don't invent structure** — use the document's own headings as guide
5. **Flag completeness** — if you couldn't read the full document, say so