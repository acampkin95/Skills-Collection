---
name: fact-check
description: Verify claims, check facts, assess truthfulness. Use when user asks "is this true", "verify", "check if", "how do I know", "can I trust this", "is this accurate", or needs to assess the reliability of information.
user-invocable: true
---

# Fact-Check — Verify & Assess Truth

Use this skill when the user needs to verify information, assess reliability of sources, check if a claim is accurate, or understand the credibility of something they've read or heard.

## When to Use

- "Is this true?"
- "Can I trust this source?"
- "Check if this is accurate"
- "How do I know this is right?"
- "What does the evidence say?"
- "Is this claim verified?"
- "Who should I believe?"
- "What's the evidence for this?"
- "Fact-check this for me"
- "Is this reliable?"

## Fact-Checking Workflow

```
CLAIM → IDENTIFY → LOCATE SOURCE → ASSESS → VERDICT
```

### Step 1 — Identify the Claim

```python
def parse_claim(claim: str) -> dict:
    """Break down the claim for verification."""
    
    return {
        "claim": claim,
        "type": classify_claim_type(claim),
        "specificity": assess_specificity(claim),
        "key_facts_to_verify": extract_facts(claim),
        "confidence_needed": determine_verification_level(claim)
    }

def classify_claim_type(claim: str) -> str:
    """Categorise the type of claim for appropriate verification."""
    
    if "all" in claim.lower() or "never" in claim.lower():
        return "absolute_claim"  # Highest scrutiny needed
    elif any(kw in claim.lower() for kw in ["percent", "%", "1 in", "1 out of"]):
        return "statistical"  # Need source + methodology
    elif any(kw in claim.lower() for kw in ["study", "research", "found", "showed"]):
        return "scientific"  # Need peer review status
    elif any(kw in claim.lower() for kw in ["law", "legal", "right", "must"]):
        return "legal"  # Need legislation + jurisdiction
    elif any(kw in claim.lower() for kw in ["always", "everyone", "no one", "every"]):
        return "overgeneralisation"  # Flag for specificity
    else:
        return "factual"  # Standard verification
```

### Step 2 — Locate Original Source

```python
def find_source(claim: str) -> dict:
    """Find the original source of a claim."""
    
    sources = {
        "government": ["gov.au", "ato.gov.au", "austlii.edu.au", "health.gov.au"],
        "academic": ["doi.org", "jstor.org", "nature.com", "sciencedirect.com", "arxiv.org"],
        "news": ["abc.net.au", "theguardian.com", "smh.com.au", "theage.com.au"],
        "fact_checks": ["abc.net.au/verification", "snopes.com", "factcheck.org.au"],
        "data": ["abs.gov.au", "data.gov.au", "worldbank.org", "oecd.org"]
    }
    
    # Check if claim matches known fact-check sites
    # Check primary sources
    # Assess recency
    
    return {"source_found": bool, "url": str, "date": str, "type": str}
```

### Step 3 — Source Credibility Assessment

```python
def assess_source_credibility(source_url: str) -> dict:
    """Evaluate the credibility of a source."""
    
    credibility_factors = {
        "authoritative_domain": {
            "gov.au": 10,  # Government
            "edu.au": 9,   # Education
            "org.au": 7,   # Non-profit
            "com.au": 5,   # Commercial
            "blogspot": 3, # Unverified
            "unknown": 1   # Low credibility
        },
        "has_author": {
            "named_author": 2,
            "organisation_only": 1,
            "anonymous": -1
        },
        "has_date": {
            "recent (< 2yr)": 2,
            "dated": 1,
            "undated": -1
        },
        "has_sources": {
            "cited": 2,
            "mentioned": 1,
            "uncited": -1
        },
        "peer_reviewed": {
            "yes": 3,
            "no": 0
        }
    }
    
    score = 0
    factors_found = {}
    
    for factor, value in credibility_factors.items():
        # Assess and add to score
        ...
    
    return {
        "score": score,
        "max_score": 20,
        "grade": grade_credibility(score),
        "factors": factors_found
    }

def grade_credibility(score: float) -> str:
    grades = {
        (16, 20): "HIGH — Very credible, can rely on this",
        (11, 15): "MEDIUM — Credible, verify key claims independently",
        (6, 10): "LOW — Verify carefully, may have bias",
        (0, 5): "VERY LOW — Do not rely on without verification"
    }
    for (low, high), verdict in grades.items():
        if low <= score <= high:
            return verdict
    return "UNKNOWN"
```

### Step 4 — Verdict

```markdown
## Fact-Check: [Claim]

**Verdict:** [VERIFIED / PARTIALLY VERIFIED / UNVERIFIABLE / FALSE / MISLEADING]

### Evidence
- [Evidence 1] — [Source]
- [Evidence 2] — [Source]
- [Evidence 3] — [Source]

### Context
[Any context that changes the meaning of the claim]

### What They Got Right
- [Correct element]

### What They Got Wrong / Misleading
- [Incorrect or misleading element]

### Source Quality
- [Source 1]: [Grade] — [Why]
- [Source 2]: [Grade] — [Why]

### Bottom Line
[1-sentence verdict with nuance]
```

## Common Misinformation Patterns

```python
misinformation_patterns = {
    "cherry_picking": {
        "definition": "Selecting data that supports your point while ignoring contradictory data",
        "how_to_check": "Ask 'What data might contradict this?'",
        "example": "Citing one study while ignoring the 10 that say otherwise"
    },
    "false_equivalence": {
        "definition": "Presenting two sides as equally valid when evidence favours one",
        "how_to_check": "Ask 'Does the evidence actually support both sides equally?'",
        "example": "'Some say vaccines work, some say they don't' — when evidence overwhelmingly supports one side"
    },
    "anecdote_as_evidence": {
        "definition": "Using one personal story to prove a general claim",
        "how_to_check": "Ask 'Is this typical or exceptional?'",
        "example": "'My neighbour smoked and lived to 100, so smoking isn't harmful'"
    },
    "causation_confusion": {
        "definition": "Assuming because two things correlate, one caused the other",
        "how_to_check": "Ask 'Is there proof of causation, not just correlation?'",
        "example": "'Schools with more library books have better results' — but better-resourced schools buy more books"
    },
    "outdated_information": {
        "definition": "Citing facts that were true but have since changed",
        "how_to_check": "Check the date of the information and verify if it's still current",
        "example": "Using 2019 tax rates to advise on 2026 tax obligations"
    },
    "strawman": {
        "definition": "Refuting a weaker version of the argument rather than the actual one",
        "how_to_check": "Ask 'Is this what the original claim actually said?'",
        "example": "'Critics say we should ban all computers' — when critics actually said regulate data collection"
    },
    "appeal_to_authority": {
        "definition": "Citing an authority in a field unrelated to the claim",
        "how_to_check": "Ask 'Is this person an expert in the relevant field?'",
        "example": "A famous actor giving medical advice"
    }
}
```

## Fact-Check Output Levels

| Request | Output |
|---------|--------|
| "Is this true?" | Short verdict + evidence |
| "Verify this claim" | Full fact-check with sources |
| "What does the evidence say?" | Literature summary + sources |
| "Can I trust this source?" | Source credibility analysis |
| "Fact-check this for me" | Comprehensive verification |

## Anti-Fact-Check Failure Rules

1. **Distinguish facts from opinions** — verify facts, acknowledge opinions
2. **Don't over-claim verification** — "I couldn't verify this" not "it's false"
3. **Check recency** — outdated information is still misinformation if presented as current
4. **Consider jurisdiction** — Australian law ≠ US law, WA law ≠ NSW law
5. **Distinguish correlation from causation** — common analytical error
6. **Be willing to say "I don't know"** — better than guessing