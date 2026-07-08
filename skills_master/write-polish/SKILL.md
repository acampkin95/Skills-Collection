---
name: write-polish
description: Improve writing clarity, tone, and structure. Use when user asks to "improve this", "make it clearer", "fix grammar", "rewrite this", "make it more professional", "polish this email".
user-invocable: true
---

# Writing Polish — Clarity, Tone, Structure

Use this skill when the user wants to improve written text — make it clearer, more professional, fix grammar, adjust tone, or restructure for impact.

## When to Use

- "Improve this", "make it clearer", "rewrite this"
- "Fix my grammar/spelling"
- "Make this more professional/personal/friendly"
- "Polish this email/draft/document"
- "Is this clear? Does this sound right?"
- "Shorten this", "simplify this"
- "Make it more persuasive/professional"

## The FOSS Method

```
F — Facts first (lead with the point, not the explanation)
O — One idea per sentence (one verb, one main clause)
S — Short sentences (under 25 words for clarity, 40 max)
S — Specific over vague ("3 days" not "a few days")
```

## Tone Calibration

```python
def match_tone(text: str, target: str) -> str:
    """Rewrite text to match target tone."""
    
    tones = {
        "professional": {
            "avoid": ["gonna", "wanna", "cool", "awesome", "stuff", "things"],
            "prefer": ["regarding", "therefore", "subsequently", "please note"],
            "structure": "clear subject-verb-object, passive appropriate",
            "jargon": "use industry terms for technical audiences"
        },
        "friendly": {
            "avoid": ["hereby", "pursuant to", "kindly", "aforementioned"],
            "prefer": ["sure", "great", "happy to help", "let me know"],
            "structure": "short sentences, direct, conversational"
        },
        "empathetic": {
            "avoid": ["unfortunately", "regrettably" (too formal), "you should"],
            "prefer": ["I understand", "that sounds difficult", "here's how"],
            "structure": "acknowledge feelings first, then solution"
        },
        "persuasive": {
            "avoid": ["maybe", "perhaps", "might", "could", "I think"],
            "prefer": ["will", "clearly", "research shows", "evidence indicates"],
            "structure": "problem → solution → call to action"
        },
        "clear": {
            "avoid": ["utilize", "commence", "prior to", "subsequent to"],
            "prefer": ["use", "start", "before", "after"],
            "structure": "active voice, short sentences, concrete terms"
        }
    }
    
    return rewrite_with_tone(text, tones[target])
```

## Structural Patterns

### Email Opening Options

| Situation | Opener |
|-----------|--------|
| **Requesting something** | "I'm writing to ask..." / "I need your help with..." |
| **Responding** | "Thank you for..." / "In response to your..." |
| **Bad news** | "Unfortunately..." / "I'm sorry to inform you that..." |
| **Good news** | "Great news..." / "I'm pleased to let you know..." |
| **Urgent** | "I need to flag..." / "Urgent: ..." (subject line only) |
| **Follow-up** | "Following up on..." / "Just checking in on..." |

### Email Closing Options

| Situation | Closer |
|-----------|--------|
| **Need a response** | "Please let me know by [date]." |
| **No response needed** | "Let me know if you have any questions." |
| **After bad news** | "I'm happy to discuss this further." |
| **Formal** | "Kind regards" |
| **Friendly** | "Thanks!" / "Talk soon!" |
| **Escalating** | "If I don't hear back by [date], I'll [action]." |

## Grammar & Clarity Fixes

```python
grammar_fixes = {
    # Passive voice → Active
    "was decided by the committee": "the committee decided",
    "it has been determined that": "we determined",
    
    # Nominalisations → Verbs
    "make a decision": "decide",
    "provide assistance": "help",
    "conduct an investigation": "investigate",
    "take into consideration": "consider",
    
    # Hedging → Direct
    "I think we should": "We should",
    "It might be good to": "Let's",
    "Perhaps you could": "Please",
    
    # Wordy → Concise
    "at this point in time": "now",
    "in order to": "to",
    "due to the fact that": "because",
    "for the purpose of": "to",
    "in the event that": "if",
    "at the present time": "now",
    "a large number of": "many",
    "the vast majority of": "most",
    
    # Vague → Specific
    "soon": "by Friday" or "within 2 business days",
    "some": "3 of the 10", "about 20%",
    "things": "items", "documents", "tasks",
    "stuff": specific noun
}
```

## Rewrite Templates

### Professional Email

```markdown
**Subject:** [Clear, specific — 8 words max]

[Opening — 1 sentence, state purpose]

[Body — key information in order of importance]

[Call to action — what you need and by when]

[Closing]
[Your name]
```

### Complaint/Escalation

```markdown
**Subject:** [Brief description of issue — reference number if applicable]

I am writing regarding [specific issue].

What happened:
- [Fact 1]
- [Fact 2]
- [Fact 3]

What I have done:
- [Step taken to resolve]

What I am requesting:
- [Specific outcome wanted]

I would appreciate a response by [date]. If I don't receive a 
satisfactory response, I intend to [next step].
```

### Request

```markdown
**Subject:** [What + why + deadline]

Hi [Name],

I need [specific request] by [date/time] for [reason/context].

[Key details:
- What exactly is needed
- Any constraints or preferences
- Why it's needed
- What happens if not delivered]

Please let me know if you have any questions or if this isn't possible.
```

## Structure Improvement Checklist

```markdown
## Editing Checklist

☐ Lead with the point (topic sentence first)
☐ One idea per paragraph
☐ One idea per sentence (no comma-chains)
☐ Active voice ("We did X" not "X was done by us")
☐ Specific over vague ("3 days" not "a few days")
☐ Jargon removed or explained for audience
☐ No filler words ("basically", "actually", "just", "simply")
☐ Positive framing (what IS possible, not what isn't)
☐ Numbers and names where possible
☐ Appropriate length (not padded, not compressed)
☐ Consistent tense throughout
☐ Correct grammar and spelling
```

## Output Format for Polish Requests

```markdown
## Original Text
[User's text]

## Improved Version
[Rewritten text]

## Changes Made
| What Changed | Why |
|--------------|-----|
| [Before] → [After] | [Reason] |
| ... | ... |

## Alternative Tones Available
- [Brief version — if user wants shorter]
- [More formal version — if needed]
- [More friendly version — if appropriate]
```