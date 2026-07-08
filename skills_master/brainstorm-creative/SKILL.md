---
name: brainstorm-creative
description: Generate ideas, solutions, and creative alternatives. Use when user asks "what are some ideas", "brainstorm", "what if", "alternatives", "options", or needs to explore multiple approaches to a problem.
user-invocable: true
---

# Brainstorm & Creative — Idea Generation

Use this skill when the user needs ideas, alternatives, creative solutions, or wants to explore multiple approaches to a problem rather than one answer.

## When to Use

- "What are some ideas for..."
- "What are my options?"
- "What if I did X instead?"
- "How could I solve this differently?"
- "What are the alternatives?"
- "What would you do?"
- "Brainstorm solutions"
- "Generate options"
- "Help me think through this"

## Brainstorming Framework: DEEP

```
D — Define the problem (correctly)
E — Explore wildly (quantity first)
E — Evaluate practically (quality second)
P — Prioritise and pick (commit to action)
```

## Step 1 — Reframe the Problem

Before generating ideas, make sure you're solving the right problem.

```python
def reframe_problem(user_problem: str) -> dict:
    """Turn a complaint into a solvable question."""
    
    # Common reframes
    reframes = {
        "I don't have enough time": 
            "How can I either save time, reduce scope, or prioritise better?",
        "It's too expensive":
            "How can I reduce cost, increase value, or find alternatives?",
        "It won't work":
            "What conditions would make it work? What would need to change?",
        "I'm stuck":
            "What would I do if I had unlimited resources? What would I do if I had none?",
        "I don't know what to do":
            "What information would help me decide? What have others done?"
    }
    
    # Extract the root problem
    for pattern, reframe in reframes.items():
        if pattern in user_problem.lower():
            return {
                "original": user_problem,
                "reframed": reframe,
                "why": "This turns a statement into a question we can answer"
            }
    
    return {
        "original": user_problem,
        "reframed": f"How could I solve this: {user_problem}?",
        "why": "Open questions generate more options"
    }
```

## Step 2 — Generate Ideas (Quantity First)

```python
def generate_options(problem: str, n: int = 7) -> list[dict]:
    """Generate diverse solution options."""
    
    options = []
    
    # Category 1: Direct solutions (solve the problem as stated)
    options.append({
        "approach": "Direct solution",
        "description": "Address the problem head-on with the obvious approach",
        "when": "Problem is well-defined and resources are available"
    })
    
    # Category 2: Alternative approaches (different path to same goal)
    options.append({
        "approach": "Alternative method",
        "description": "Same goal, different way of achieving it",
        "when": "Direct solution is blocked or expensive"
    })
    
    # Category 3: Reduce the problem (make it smaller)
    options.append({
        "approach": "Simplify or reduce scope",
        "description": "Reduce the problem so a smaller solution works",
        "when": "Full solution is too complex or expensive"
    })
    
    # Category 4: Avoid entirely (skip the problem)
    options.append({
        "approach": "Avoid or sidestep",
        "description": "Find a way that doesn't require solving this problem",
        "when": "Problem is optional or can be bypassed"
    })
    
    # Category 5: Buy the solution (outsource)
    options.append({
        "approach": "Outsource or buy",
        "description": "Pay someone else to handle it",
        "when": "You don't have the time or skills"
    })
    
    # Category 6: Automate (remove human effort)
    options.append({
        "approach": "Automate",
        "description": "Build a system that handles it without you",
        "when": "Problem recurs and follows patterns"
    })
    
    # Category 7: Combination (mix approaches)
    options.append({
        "approach": "Hybrid",
        "description": "Combine elements of multiple approaches",
        "when": "No single approach is sufficient"
    })
    
    return options[:n]
```

## Step 3 — Evaluate Options

```python
def evaluate_options(options: list[dict], criteria: list[str]) -> list[dict]:
    """
    Score each option against key criteria.
    criteria example: ["cost", "time", "effort", "risk", "impact"]
    """
    
    for option in options:
        scores = {}
        for criterion in criteria:
            score = ask_user_or_assess(option, criterion)
            scores[criterion] = score
        
        option["scores"] = scores
        option["total_score"] = sum(scores.values()) / len(scores)
        option["recommendation"] = "consider" if option["total_score"] >= 3 else "revisit"
    
    return sorted(options, key=lambda x: x["total_score"], reverse=True)

def risk_assessment(option: dict) -> dict:
    """Assess risk profile of an option."""
    return {
        "risk_level": "low" if option.get("reversible", True) else "medium" if option.get("time_limited", False) else "high",
        "reversible": option.get("can_undo", True),
        "cost_to_try": option.get("cost", "unknown"),
        "time_to_test": option.get("time", "unknown"),
        "worst_case": option.get("worst_case", "Unknown")
    }
```

## Step 4 — Idea Generation Techniques

### SCAMPER (Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse)

```markdown
### SCAMPER for [Topic]

**S — Substitute:** What if I replaced [X] with [Y]?
**C — Combine:** What if I merged [A] and [B]?
**A — Adapt:** How would this work in [different context]?
**M — Modify:** What if I changed the size/frequency/shape?
**P — Put to other use:** What else could this be used for?
**E — Eliminate:** What if I removed [X]? Would the rest still work?
**R — Reverse:** What if I did the opposite? Flipped the order?
```

### Worst Idea First (WiF)

```markdown
List terrible ideas first — they're easier and break mental blocks:
1. [Terrible idea 1]
2. [Terrible idea 2]
3. [Terrible idea 3]

Now flip the worst parts:
- [Flip 1] → becomes [actually useful idea]
- [Flip 2] → becomes [actually useful idea]
```

### Six Thinking Hats (Edward de Bono)

```markdown
## Six Thinking Hats for [Decision]

🔴 **Red Hat** (Emotions): "I feel [this] about this..."
🔵 **Blue Hat** (Process): "Let's use this approach to structure our thinking..."
⚪ **White Hat** (Facts): "The data shows..."
🟡 **Yellow Hat** (Benefits): "The upside is..."
🟢 **Green Hat** (Creativity): "What if we tried..."
⚫ **Black Hat** (Cautions): "The risk is..."
```

## Idea Output Format

```markdown
## Ideas for: [Problem]

**Reframed question:** [Better question]

### Option 1: [Name]
**What it is:** [1 sentence]
**How it works:** [2-3 sentences]
**Pros:** [Benefit 1], [Benefit 2]
**Cons:** [Risk 1], [Risk 2]
**Best for:** [When to choose this]
**Effort:** [Low/Medium/High]
**Confidence:** [Sure/Maybe/Wild guess]

### Option 2: [Name]
...

### Option 3: [Name]
...

### Recommended: [Option X]
**Why:** [1-2 sentences on why this is the best starting point]

### My suggestion
Start with [Option X], and if that doesn't work, try [Option Y] as a backup.
```

## Creative Problem-Solving Questions

```python
creative_questions = {
    "blocked_on_cost": [
        "What if cost wasn't a factor?",
        "What's the cheapest possible version of this?",
        "Can I try a small version first before committing?",
        "Is there a free or open-source alternative?",
        "Could I trade something instead of paying cash?"
    ],
    "blocked_on_time": [
        "What if I only did 20% that gives 80% of the value?",
        "What's the fastest path to a testable result?",
        "Can I automate any part of this?",
        "Who could help me do this faster?",
        "What's the minimum I need to start?"
    ],
    "blocked_on_knowledge": [
        "Who has done this before? Can I ask them?",
        "What's the simplest version of this I could try?",
        "What would I Google to figure this out?",
        "What's the worst-case if I try and fail?",
        "Could I learn enough to start in 2 hours?"
    ],
    "no_motivation": [
        "What's the smallest possible step I could take?",
        "What would make this interesting or fun?",
        "Who could I do this with (accountability)?",
        "What would I tell a friend in this situation?",
        "If I do nothing, what happens? (Is that actually OK?)"
    ]
}
```

## Anti-Brainstorm Failure Rules

1. **No idea is wrong during generation** — defer judgment, capture everything
2. **Quantity before quality** — 10+ ideas before evaluating
3. **Build on others** — "I like X, but what if we also..." beats "but"
4. **Reframe blockers** — "can't" → "how could I"
5. **Make the problem specific** — vague problems generate vague ideas