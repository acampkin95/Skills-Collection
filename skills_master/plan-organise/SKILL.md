---
name: plan-organise
description: Break down tasks, create plans, organise projects. Use when user asks to "plan this", "break this down", "what are the steps", "make a todo list", "how should I organise", "help me prioritise", or needs a structured approach to work.
user-invocable: true
---

# Plan & Organise — Structured Task Management

Use this skill when the user needs to break down work, create a plan, organise a project, prioritise tasks, or figure out the steps to get something done.

## When to Use

- "Help me plan..."
- "Break this down into steps"
- "What do I need to do first?"
- "How should I organise this?"
- "What's the best order?"
- "Help me prioritise"
- "I have too much to do"
- "Where do I start?"
- Project kickoff, event planning, multi-step tasks

## Planning Framework: SCOPE

```
S — Scope: What exactly is being planned? What's in/out?
C — Components: Break into major work areas
O — Order: Sequence (dependencies, priorities)
P — People: Who does what, when
E — Estimate: How long each component takes
```

## Task Breakdown Method

### Step 1 — Identify the End Goal

```markdown
## Planning: [Goal]

**What does success look like?**
[1-2 sentences describing the finished state]

**What's in scope:**
- [Included item 1]
- [Included item 2]

**What's out of scope:**
- [Excluded item 1]
- [Excluded item 2]
```

### Step 2 — Decompose into Work Packages

```python
def decompose_task(goal: str) -> list[dict]:
    """Break goal into discrete work packages."""
    
    work_packages = []
    
    # Phase 1: Foundation (must come first)
    work_packages.append({
        "phase": "Foundation",
        "tasks": [
            "Define scope and acceptance criteria",
            "Identify stakeholders and requirements",
            "Assess current state / research",
            "Create initial plan and get sign-off"
        ],
        "depends_on": []
    })
    
    # Phase 2: Core work
    work_packages.append({
        "phase": "Core Work",
        "tasks": [
            "Main deliverable 1",
            "Main deliverable 2",
            "Main deliverable 3"
        ],
        "depends_on": ["Foundation"]
    })
    
    # Phase 3: Integration / Review
    work_packages.append({
        "phase": "Review & Refine",
        "tasks": [
            "Review against requirements",
            "Refine and polish",
            "Test / validate",
            "Final sign-off"
        ],
        "depends_on": ["Core Work"]
    })
    
    return work_packages
```

### Step 3 — Sequence with Dependencies

```python
def sequence_tasks(tasks: list[dict]) -> list:
    """
    Order tasks accounting for dependencies.
    Output: ordered list with timing estimates.
    """
    
    # Sort by:
    # 1. External dependencies (wait for outside input first)
    # 2. Foundation tasks (must precede dependent work)
    # 3. Parallelisable (can do simultaneously)
    # 4. Priority (impact × urgency)
    
    ordered = []
    ready = []
    blocked = []
    
    for task in tasks:
        if task.get("blocked_by"):
            blocked.append(task)
        else:
            ready.append(task)
    
    # Process ready tasks, then move blocked tasks to ready as dependencies clear
    
    return ordered
```

## Prioritisation Matrix

```markdown
## Priority Matrix

              High Impact
                  │
     DO FIRST     │    SCHEDULE
     (Do this     │    (Plan for
     week)        │    this month)
  ────────────────┼────────────────
     DELEGATE     │    ELIMINATE
     (Who can     │    (Skip or
     do this?)    │    cut this)
                  │
              Low Impact
    High Urgency  Low Urgency
```

### Priority Scoring

```python
def priority_score(task: dict) -> int:
    """
    Score task on urgency × importance.
    Higher score = do first.
    """
    urgency = task.get("urgency", 3)   # 1-5
    importance = task.get("importance", 3)  # 1-5
    
    score = urgency * importance
    
    # Adjust for deadlines (within 48h = max urgency)
    if task.get("deadline_days", 999) <= 2:
        urgency = 5
    
    # Adjust for dependencies (blocks other work)
    if task.get("blocks_others", False):
        importance = 5
    
    return urgency * importance

# Priority tiers
TIERS = {
    (16, 25): "CRITICAL — Do immediately",
    (10, 15): "HIGH — Do today",
    (6, 9): "MEDIUM — Do this week",
    (3, 5): "LOW — Do when possible",
    (1, 2): "TRIVIAL — Consider skipping"
}
```

## Project Plan Template

```markdown
## Project Plan: [Name]

**Objective:** [1 sentence]
**Start date:** [Date]
**Target completion:** [Date]
**Owner:** [Name]

### Milestones

| Milestone | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| [Milestone 1] | [Date] | Not started | |
| [Milestone 2] | [Date] | Not started | |
| [Milestone 3] | [Date] | Not started | |

### Work Breakdown

#### Phase 1: [Name] ([Start] – [End])
**Goal:** [What this phase achieves]

| Task | Owner | Effort | Deadline | Status |
|------|-------|--------|----------|--------|
| [Task 1] | [Name] | [X hrs] | [Date] | ☐ |
| [Task 2] | [Name] | [X hrs] | [Date] | ☐ |
| [Task 3] | [Name] | [X hrs] | [Date] | ☐ |

#### Phase 2: [Name] ([Start] – [End])
...

### Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | High | Medium | [Plan] |
| [Risk 2] | Medium | Low | [Plan] |

### Dependencies
- [Depends on X] — need X before proceeding
- [Blocking Y] — must finish this before Y can start

### Resources Needed
- [Resource 1]
- [Resource 2]

### Check-ins
- Weekly review: [Day/time]
- Go/no-go: [Date]
```

## Daily Planning Template

```markdown
## Today: [Date]

### Top 3 Must-Do
1. [ ] [Most important task] — [Why it matters]
2. [ ] [Second task] — [Why it matters]
3. [ ] [Third task] — [Why it matters]

### If Time Permits
4. [ ] [Task 4]
5. [ ] [Task 5]

### Boundaries
- [ ] Don't start [distraction 1]
- [ ] Protect [time block] for focused work

### End-of-Day Review
- What got done: [List]
- What didn't: [List — carry forward]
- Tomorrow's priority: [Task]
```

## Organisational Patterns

```python
organisational_patterns = {
    "event_planning": {
        "sequence": [
            "Set date and budget",
            "Define guest list and invite",
            "Plan venue and catering",
            "Arrange entertainment/activities",
            "Send reminders (1 week, 1 day before)",
            "Day-of coordination",
            "Post-event follow-up"
        ],
        "key_questions": [
            "What's the purpose / vibe?",
            "How many people?",
            "What's the budget?",
            "Any dietary/access needs?"
        ]
    },
    "research_project": {
        "sequence": [
            "Define research question",
            "Identify information sources",
            "Gather and read sources",
            "Analyse and synthesise",
            "Draft findings",
            "Review and refine",
            "Format and cite"
        ],
        "key_questions": [
            "What do I need to prove/disprove?",
            "Who has already researched this?",
            "What's the deadline?"
        ]
    },
    "move_or_change": {
        "sequence": [
            "Inventory current state",
            "Define target state",
            "Identify gaps",
            "Plan transition steps",
            "Execute in phases",
            "Validate new state",
            "Decommission old state"
        ],
        "key_questions": [
            "What must survive the change?",
            "What can be replaced?",
            "What's the rollback plan?"
        ]
    }
}
```

## Anti-Planning Failure Rules

1. **Don't plan without scope** — vague planning wastes time
2. **Estimate conservatively** — multiply by 1.5 for real-world accuracy
3. **Identify the blocker** — what's stopping progress right now?
4. **Break down further if stuck** — "do this task" not "do project"
5. **One owner per task** — shared ownership = no ownership
6. **Prioritise ruthlessly** — if everything is priority, nothing is