---
name: compare-decide
description: Compare options, weigh trade-offs, make decisions. Use when user asks to "compare", "pros and cons", "which is better", "help me decide", "should I choose A or B", "what are the trade-offs", or needs to evaluate alternatives.
user-invocable: true
---

# Compare & Decide — Evaluate Options, Choose Action

Use this skill when the user needs to compare options, weigh trade-offs, make a decision between alternatives, or understand the pros and cons of different choices.

## When to Use

- "Compare A and B"
- "What are the pros and cons of X vs Y?"
- "Which should I choose?"
- "Help me decide"
- "Is A or B better for me?"
- "What are the trade-offs?"
- "How do these options stack up?"
- "Should I do X or Y?"
- "What would you recommend?"

## Decision Framework: DECIDE

```
D — Define the decision (what exactly are you choosing?)
E — Enumerate options (what are all the choices?)
C — Criteria (what matters most to you?)
I — Investigate (gather information on each option)
D — Decide (score options against criteria)
E — Execute (commit and act)
```

## Step 1 — Define the Decision

```python
def define_decision(decision_question: str) -> dict:
    """Frame the decision clearly."""
    
    return {
        "question": decision_question,
        "what_exactly": extract_decision_type(decision_question),
        "who_decides": identify_decider(decision_question),
        "time_horizon": identify_time_horizon(decision_question),
        "stakes": assess_stakes(decision_question),
        "reversibility": assess_reversibility(decision_question)
    }

def assess_stakes(question: str) -> str:
    if any(kw in question.lower() for kw in ["life", "death", "permanent", "irreversible"]):
        return "HIGH — Take time, get expert advice"
    elif any(kw in question.lower() for kw in ["major", "large", "significant", "lots of money"]):
        return "MEDIUM — Consider carefully, gather information"
    elif any(kw in question.lower() for kw in ["small", "minor", "easy to change"]):
        return "LOW — Decide quickly, can adjust later"
    else:
        return "MEDIUM-LOW — Default to thorough consideration"
```

## Step 2 — Criteria Weighting

```python
def get_decision_criteria(options: list) -> list[dict]:
    """Identify key decision criteria and relative importance."""
    
    # Common criteria with default weights
    common_criteria = {
        "cost": {"weight": 1.0, "question": "How much does it cost?"},
        "time": {"weight": 1.0, "question": "How long does it take?"},
        "effort": {"weight": 0.8, "question": "How much work is it?"},
        "quality": {"weight": 1.0, "question": "How good is the outcome?"},
        "risk": {"weight": 1.0, "question": "How likely is failure?"},
        "reversibility": {"weight": 0.7, "question": "Can I undo this?"},
        "speed": {"weight": 0.8, "question": "How fast do I need it?"},
        "longevity": {"weight": 0.7, "question": "How long does the solution last?"},
        "support": {"weight": 0.6, "question": "Is help available if needed?"},
        "simplicity": {"weight": 0.5, "question": "How complex is this?"}
    }
    
    return common_criteria
```

## Step 3 — Option Comparison

```python
def compare_options(options: list[dict], criteria: dict) -> list[dict]:
    """
    Compare options across weighted criteria.
    Output: scored and ranked options.
    """
    
    scored_options = []
    
    for option in options:
        total_score = 0
        total_weight = 0
        scores = {}
        
        for criterion, info in criteria.items():
            score = rate_option(option, criterion)  # 1-5 scale
            weight = info.get("weight", 1.0)
            weighted_score = score * weight
            
            scores[criterion] = {
                "raw_score": score,
                "weight": weight,
                "weighted_score": round(weighted_score, 2)
            }
            
            total_score += weighted_score
            total_weight += weight
        
        option["scores"] = scores
        option["total_score"] = round(total_score, 2)
        option["normalised_score"] = round((total_score / total_weight) * 100, 1)
        
        scored_options.append(option)
    
    return sorted(scored_options, key=lambda x: x["total_score"], reverse=True)

def rate_option(option: dict, criterion: str) -> int:
    """Rate an option on a single criterion (1-5 scale)."""
    # 5 = excellent, 1 = poor
    # Implementation depends on criterion type
```

## Comparison Output Formats

### Pros and Cons

```markdown
## [Option A] vs [Option B]

### [Option A]
**Best for:** [When to choose this]

**Pros:**
- [Advantage 1]
- [Advantage 2]
- [Advantage 3]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Estimated cost:** $[amount]
**Time to implement:** [duration]
**Risk level:** [Low/Medium/High]

### [Option B]
**Best for:** [When to choose this]

**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

**Estimated cost:** $[amount]
**Time to implement:** [duration]
**Risk level:** [Low/Medium/High]

### Comparison Summary

| Factor | [A] | [B] |
|--------|-----|-----|
| [Factor 1] | ★★★★☆ | ★★★☆☆ |
| [Factor 2] | ★★★☆☆ | ★★★★★ |
| [Factor 3] | ★★★★☆ | ★★★★☆ |

### My Recommendation
[Based on stated priorities, I recommend...]
**Why:** [1-2 sentence reasoning]
```

### Decision Matrix

```markdown
## Decision Matrix: [Topic]

**Decision:** [What you're choosing]
**Priority:** [What's most important to you]

### Weighted Criteria

| Criterion | Weight | Why It Matters |
|-----------|--------|----------------|
| [Criterion 1] | [High/Med/Low] | [Reason] |
| [Criterion 2] | [High/Med/Low] | [Reason] |

### Scoring (1-5)

| Option | [Criterion 1] | [Criterion 2] | [Criterion 3] | Total | Recommendation |
|--------|--------------|--------------|--------------|-------|----------------|
| [A] | 4 | 3 | 5 | **12** | ✅ Recommended |
| [B] | 2 | 5 | 3 | **10** | Consider |
| [C] | 3 | 2 | 2 | **7** | Not recommended |

### Recommended: [Option]
**Confidence:** [High/Medium/Low — based on how clear the choice is]

### What could change my recommendation
- If [factor] changes significantly → [alternative]
- If [factor] is more important → [alternative]
```

## Common Decision Types

```python
decision_patterns = {
    "buy_vs_rent": {
        "criteria": ["affordability", "flexibility", "maintenance", "investment", "stability"],
        "key_question": "How long will you stay there?",
        "rule_of_thumb": "Buy if staying >5-7 years in stable area"
    },
    "keep_vs_replace": {
        "criteria": ["cost", " reliability", "efficiency", "maintenance_history", "sentiment"],
        "key_question": "What's the repair cost vs replacement cost?",
        "rule_of_thumb": "Replace if repair >50% of replacement cost"
    },
    "stay_vs_leave": {
        "criteria": ["growth", "culture", "management", "development", "compensation", "location"],
        "key_question": "What would need to change to make staying worthwhile?",
        "rule_of_thumb": "Leave if issues are systemic, not fixable"
    },
    "build_vs_buy": {
        "criteria": ["cost", "time", "control", "maintenance", "uniqueness"],
        "key_question": "Is this our core competency?",
        "rule_of_thumb": "Build what differentiates, buy what's commodity"
    }
}
```

## Decision Traps to Avoid

```python
traps = {
    "sunk_cost": "You've invested X, so you should continue → Wrong. Past costs don't predict future value.",
    "status_quo": "Keep the current option → Wrong. New options should be evaluated independently.",
    "availability_bias": "S容易想起的选项更安全 → Wrong. Easy to remember ≠ best choice.",
    "anchoring": "第一个价格锚定了你的判断 → Wrong. Evaluate independently of first impression.",
    "confirmation_bias": "只找支持你观点的证据 → Wrong. Actively seek disconfirming evidence.",
    "groupthink": "Everyone agrees → Wrong. Silence ≠ agreement. Ask for dissent.",
    "analysis_paralysis": "永远在分析，从不决定 → Wrong. Good enough now beats perfect later."
}
```

## Anti-Comparison Failure Rules

1. **Make the criteria explicit** — what matters to YOU specifically
2. **Score against criteria, not gut feel** — gut feel can be biased
3. **Consider reversibility** — low-stakes reversible decisions = decide fast
4. **Account for confidence** — if you're unsure, the recommendation is weaker
5. **Name the trade-off** — if you're choosing A over B, say why the benefit outweighs the cost
6. **Set a decision deadline** — avoid analysis paralysis