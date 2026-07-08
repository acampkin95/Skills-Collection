---
name: translate-explain
description: Explain complex topics simply. Use when user asks "what does X mean", "can you explain", "I don't understand", "what is", "how does it work", or needs a jargon-free explanation of a technical or complex concept.
user-invocable: true
---

# Translate & Explain — Complex Made Simple

Use this skill when the user needs something explained in plain language — technical concepts, jargon, complex processes, or anything that requires making the complex accessible.

## When to Use

- "What does [term] mean?"
- "Can you explain how [thing] works?"
- "I don't understand..."
- "What is [concept] in simple terms?"
- "How does [technical thing] affect me?"
- "What does this legal/medical/technical jargon mean?"
- "Break this down for me"
- "What are the basics of [topic]?"

## The Layers Model

```
LAYER 1 — The One-Liner
The simplest possible explanation — 1 sentence.

LAYER 2 — The Core Concept
What it actually is and why it matters — 1-2 paragraphs.

LAYER 3 — The Mechanics
How it works step by step — for those who want more detail.

LAYER 4 — The Examples
Real-world analogies and examples — makes it stick.

LAYER 5 — The Caveats
What to watch out for, limitations, exceptions — for accuracy.
```

## Translation Patterns

### Technical to Plain

```python
translations = {
    # Legal
    "pursuant to": "according to / following",
    "hereby": "now",
    "notwithstanding": "despite / even though",
    "shall": "must / will",
    "deemed": "considered as / treated as",
    "inter alia": "among other things",
    "prima facie": "at first glance / on the face of it",
    "in loco parentis": "in place of a parent / acting as a guardian",
    
    # Medical
    "benign": "not harmful / non-cancerous",
    "malignant": "harmful / cancerous",
    "acute": "sudden / short-term",
    "chronic": "long-term / ongoing",
    "prognosis": "expected outcome / likely result",
    "contraindicated": "should not be used / risky in this situation",
    
    # Technical
    "API": "a way for programs to talk to each other",
    "latency": "how long it takes to get a response",
    "scalability": "how well it handles more users/data",
    "encryption": "scrambling data so only authorised people can read it",
    "machine learning": "software that learns patterns from data instead of being explicitly programmed",
    "blockchain": "a shared digital record that can't be altered retroactively",
    
    # Financial
    "amortisation": "spreading a cost over time (like a loan repayment)",
    "liquidity": "how easily you can convert an asset to cash",
    "hedge": "an insurance policy against financial loss",
    "leverage": "borrowing money to amplify potential returns (and losses)",
    "equity": "your ownership stake / the value you own in something"
}
```

### Concept Explainer Template

```markdown
## [Concept] Explained Simply

### The One-Liner
[What it is in 10 words or fewer]

### What It Is
[2-3 sentences — what it is, not how it works yet]

### Why It Matters to You
[How this affects the user, in practical terms. What problem does it solve?]

### How It Works (Step by Step)
1. [First step]
2. [Second step]
3. [Third step]

### Real-World Analogy
[Simple analogy that captures the essence]
"Think of it like [analogy]..."

### Quick Example
[Simple numerical or practical example]
"If you [simple scenario], then [result]."

### What to Watch Out For
- [Caveat 1]
- [Caveat 2]

### Related Concepts
- [Related term 1] — [brief connection]
- [Related term 2] — [brief connection]
```

## Jargon Buster Pattern

When the user encounters technical terms:

```python
def explain_jargon(text: str) -> dict:
    """Parse text and explain technical terms."""
    
    # Identify terms to explain
    technical_terms = {
        "API": "Application Programming Interface — a way for software to talk to other software",
        "algorithm": "a step-by-step set of rules for solving a problem",
        "bandwidth": "how much data can be sent at once (like pipe width)",
        "cache": "temporary storage of frequently-used data for faster access",
        "encryption": "converting data into code so only authorised parties can read it",
        "latency": "delay between action and response",
        "protocol": "a standard set of rules for how things communicate",
        "redundancy": "having backup systems so failure of one doesn't break everything",
        "workflow": "the sequence of steps to complete a process",
        "stakeholder": "anyone who has an interest or involvement in something"
    }
    
    found = []
    for term, explanation in technical_terms.items():
        if term.lower() in text.lower():
            found.append({"term": term, "explanation": explanation})
    
    return found
```

## Explaining Processes

```python
def explain_process(steps: list, audience: str = "general") -> str:
    """Turn a process into a plain-language explanation."""
    
    if audience == "general":
        # Remove jargon, use analogies
        template = """
### What's Happening

When you [trigger action], the system does this:

1. [Step 1 — plain language]
2. [Step 2 — plain language]
3. [Step 3 — plain language]

### What You Get

[End result, in practical terms]

### How Long It Takes

[Timeframe]

### What If Something Goes Wrong

[Common issues and how to handle them]
"""
    
    elif audience == "technical":
        # Keep technical terms, add depth
        template = """
### Architecture

[Technical overview]

### Steps
1. [Technical step 1]
2. [Technical step 2]
3. [Technical step 3]

### Failure Modes
[What can go wrong and why]
"""
    
    return template
```

## Analogy Library

```python
analogies = {
    "internet": "Like a post office system — data gets addressed, sent through the network, and delivered to the right address. The protocol (like postal rules) ensures everyone follows the same addressing system.",
    
    "encryption": "Like a locked box — only people with the key (decryption key) can open and read what's inside. Even if someone intercepts the box, they can't open it without the key.",
    
    "database": "Like a very organised filing cabinet — each piece of information has a specific place, indexes help you find things quickly, and rules prevent putting the same file in two places.",
    
    "insurance": "Like betting on the horse — you pay a small premium, and if something bad happens, the company covers the big cost. Most people pay in and never need it; the few who do benefit from everyone else's premiums.",
    
    "compound interest": "Like a snow rolling downhill — each time it rolls, it picks up more snow, which makes it bigger faster, which picks up even more. The growth accelerates over time.",
    
    "healthcare triage": "Like a queue at an emergency room — not who arrived first, but who needs help most urgently. The most critical cases get seen first, even if they arrived later.",
    
    "renting": "Like paying to use someone else's property — you get the benefits of living there, but you don't own it, can't modify it freely, and have to follow the rules in the lease.",
    
    "share market": "Like a market for company ownership — people buy and sell slices of companies. Prices go up when more people want to buy than sell, and down when more want to sell."
}
```

## Avoiding Over-Simplification

```python
# When to simplify vs when to be precise
def explain_with_accuracy(text: str, user_level: str) -> str:
    """Match explanation depth to user sophistication."""
    
    if user_level == "complete_beginner":
        return simplify_fully(text)
    elif user_level == "informed_non_expert":
        return explain_with_analogies(text)
    elif user_level == "semi_technical":
        return explain_with_some_terms(text)
    elif user_level == "technical":
        return explain_with_full_accuracy(text)
```

## Anti-Explanation Failure Rules

1. **Don't over-simplify to the point of inaccuracy** — "essentially" is your warning word
2. **Use the right level** — match to the user's apparent knowledge
3. **Check understanding** — "Does that make sense?" or "Want me to go deeper?"
4. **Analogies are bridges** — use them to connect to known concepts, not as the explanation itself
5. **Name the jargon** — even if you explain it, use the real term so the user can look it up later