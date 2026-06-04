---
name: design-principles
description: "UI/UX design fundamentals including visual hierarchy, Gestalt principles, affordances, design heuristics, composition, and usability principles for non-CLI agents. Use when evaluating UI designs, understanding design decisions, applying design principles, critiquing layouts, or creating design-guided content."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Design Principles

Foundational UI/UX design principles that govern effective visual communication and user interaction. Essential knowledge for evaluating, creating, and critiquing designs.

## Core Design Principles

### 1. Visual Hierarchy

Control what users see first, second, third through deliberate emphasis.

```
HIERARCHY TOOLS (strongest to weakest):
──────────────────────────────────────
1. SIZE         — Larger = more important
2. COLOR        — Vivid/saturated = more attention
3. CONTRAST     — High contrast draws eye
4. POSITION     — Top-left (in LTR) = primary position
5. WHITESPACE   — More space = more importance
6. TYPOGRAPHY   — Bolder/larger = more important
7. PROXIMITY    — Grouped items = related

HIERARCHY LEVELS:
├── PRIMARY:   Page title, key action button, hero image
├── SECONDARY: Section headings, key content, secondary actions
├── TERTIARY:  Body text, supporting details
└── QUATERNARY: Footer, legal text, fine print
```

### 2. Gestalt Principles

How humans perceive and group visual elements:

| Principle | Rule | Design Application |
|-----------|------|-------------------|
| **Proximity** | Objects close together are perceived as a group | Group related controls; separate unrelated ones |
| **Similarity** | Similar objects are perceived as a group | Consistent styling for same-type elements |
| **Continuity** | Eye follows smooth paths | Guide eye flow through content |
| **Closure** | Mind completes incomplete shapes | Icons, logos can be simplified |
| **Figure/Ground** | Elements perceived as either foreground or background | Card elevations, overlays, modals |
| **Common Fate** | Objects moving together are grouped | Animation of related elements together |
| **Symmetry** | Symmetrical elements form a group | Balanced layouts feel stable |
| **Uniform Connectedness** | Connected elements are grouped | Lines between nodes, border containers |

### 3. Affordances & Signifiers

```
AFFORDANCE:    What an object can do (action possibility)
SIGNIFIER:     How the user discovers the affordance (visual clue)

Examples:
┌──────────────────┬──────────────────┬──────────────────┐
│ Affordance       │ Good Signifier   │ Bad Signifier    │
├──────────────────┼──────────────────┼──────────────────┤
│ Clickable        │ Raised button    │ Flat text        │
│ Scrollable       │ Scrollbar/cut-off│ No visual cue    │
│ Draggable        │ Grip handle      │ Nothing          │
│ Input field      │ Inset box        │ Flat line        │
│ Expandable       │ Chevron/arrow    │ No indicator     │
│ Destructive      │ Red color        │ Same as normal   │
└──────────────────┴──────────────────┴──────────────────┘

RULE: Every interactive element must have a visible signifier.
```

### 4. Design Heuristics (Nielsen's 10)

| # | Heuristic | Key Points |
|---|-----------|------------|
| 1 | **System status** | Show what's happening (loading, progress, feedback) |
| 2 | **Real-world match** | Use familiar language and concepts |
| 3 | **User control** | Undo, redo, clear escape hatches |
| 4 | **Consistency** | Same patterns throughout, follow platform conventions |
| 5 | **Error prevention** | Better than good error messages |
| 6 | **Recognition over recall** | Make options visible, don't make users remember |
| 7 | **Flexibility** | Shortcuts for advanced users, guidance for beginners |
| 8 | **Aesthetic & minimal** | Every element serves a purpose |
| 9 | **Error recovery** | Clear, actionable error messages |
| 10 | **Help & documentation** | Available but not required |

## Layout Principles

### Grid Systems

```
COMMON GRIDS:
─────────────
8-POINT GRID:   Spacing multiples of 8px (8, 16, 24, 32, 48, 64)
                 Most popular, works well with common screen sizes

12-COLUMN GRID:  For page layouts
                 Flexible: can use 1-12 columns per section
                 Gutters: 16-32px between columns
                 Margins: 16-64px on sides

BASELINE GRID:   Typography alignment
                 Text sits on consistent horizontal lines
                 Improves readability and visual rhythm
```

### White Space (Negative Space)

```
TYPES:
├── Micro whitespace: Between lines, letters, small elements
├── Macro whitespace: Between sections, around content blocks
└── Active whitespace: Deliberately used to create emphasis

RULES:
- More whitespace = more perceived quality
- Whitespace is not wasted space
- Cramped layouts feel cheap and overwhelming
- Generous whitespace in headers and between sections
- Tighter whitespace within related groups (proximity)

SPACING SCALE (8pt grid):
4px  → Tight (between related inline elements)
8px  → Close (within components)
16px → Standard (between related components)
24px → Comfortable (between sections)
32px → Spacious (between major sections)
48px → Generous (page-level breaks)
64px → Expansive (hero sections, major breaks)
```

### The F-Pattern and Z-Pattern

```
F-PATTERN (text-heavy pages like articles):
─────────────────────────────────────────
Users scan in F-shaped pattern:
  1. Horizontal scan across top
  2. Horizontal scan lower (shorter)
  3. Vertical scan down left side

Design implications:
  - Put important content left-aligned
  - Use strong headings and paragraphs
  - First two paragraphs are critical

Z-PATTERN (landing pages, simple layouts):
────────────────────────────────────────
Users scan in Z pattern:
  1. Top-left to top-right (logo → primary action)
  2. Diagonal to left side
  3. Left to right along bottom

Design implications:
  - Logo top-left
  - Primary CTA top-right
  - Secondary content along the diagonal
  - Secondary CTA bottom-right
```

## Color Principles

### Color Theory Basics

```
COLOR RELATIONSHIPS:
├── Complementary:   Opposite on wheel (high contrast)
├── Analogous:       Adjacent on wheel (harmonious)
├── Triadic:         Three equally spaced (vibrant)
├── Split-comp:      Complement + adjacent (nuanced)
└── Monochromatic:   Same hue, different values (unified)

COLOR PSYCHOLOGY:
├── Blue:    Trust, stability, professionalism
├── Green:   Growth, health, nature, success
├── Red:     Urgency, energy, danger, passion
├── Orange:  Enthusiasm, creativity, warmth
├── Yellow:  Optimism, attention, caution
├── Purple:  Luxury, creativity, mystery
├── Black:   Elegance, authority, sophistication
├── White:   Clean, simplicity, space
└── Gray:    Neutral, professional, balance
```

### Contrast Requirements

```
WCAG CONTRAST RATIOS:
─────────────────────
Normal text (<18pt):       4.5:1 minimum (AA), 7:1 (AAA)
Large text (≥18pt bold):   3:1 minimum (AA), 4.5:1 (AAA)
UI components & graphics:  3:1 minimum

CHECK: Don't rely on color alone to convey information.
       Always pair with text, icons, or patterns.
```

## Typography Principles

### Type Scale

```
MODULAR SCALE (ratio 1.25 — Major Third):
─────────────────────────────────────────
Display:  3.052rem  (48.83px)  → Hero headings
H1:       2.441rem  (39.06px)  → Page title
H2:       1.953rem  (31.25px)  → Section heading
H3:       1.563rem  (25.00px)  → Subsection
H4:       1.25rem   (20.00px)  → Card heading
Body:     1rem      (16.00px)  → Default text
Small:    0.8rem    (12.80px)  → Captions, labels
Tiny:     0.64rem   (10.24px)  → Legal, badges

LINE HEIGHT:
├── Body text: 1.5 - 1.75
├── Headings:  1.1 - 1.3
└── UI text:   1.3 - 1.5

MAX LINE LENGTH (measure):
├── Optimal: 45-75 characters per line
├── Acceptable: 40-90 characters
└── Set with max-width: 65ch
```

### Font Pairing Guidelines

```
SAFE PATTERNS:
├── 1 sans-serif for everything (simplest)
├── 1 serif + 1 sans-serif (classic contrast)
├── 1 display + 1 workhorse (personality + readability)
└── Maximum 2-3 fonts total

RULES:
- Headings can be more expressive
- Body text must prioritize readability
- Don't mix similar fonts (two sans-serifs, two serifs)
- Match x-heights when pairing
- Test at all sizes before committing
```

## Interaction Design

### Feedback Loops

```
IMMEDIATE (<0.1s):    Visual state change on interaction
                       Button press, hover, focus

QUICK (0.1-1s):       Action acknowledgment
                       Form validation, toggle switch

MODERATE (1-5s):      Progress indication
                       Loading spinner, progress bar

LONG (>5s):           Background processing
                       Progress bar with percentage, estimated time
```

### Fitts's Law

```
Time to reach target = f(distance / size)

DESIGN IMPLICATIONS:
├── Important buttons should be LARGE
├── Buttons near edges/corners are easier to hit
├── Related actions should be close together
├── Minimum touch target: 44x44px (WCAG)
├── Recommended touch target: 48x48dp
└── Mouse targets can be smaller (24x24px minimum)
```


## When to Use

- Evaluating or critiquing visual design work
- Providing design feedback grounded in established principles
- Making layout, color, and typography decisions
- Understanding why certain designs work or don't work
- Applying Gestalt principles, visual hierarchy, and balance to UI work

## Limitations

- Design principles are guidelines, not absolute rules
- Cultural context affects design perception — what works in one market may not in another
- Trends evolve; principles remain but their application changes
- Cannot replace user testing and real-world validation

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [visual-design](../visual-design/SKILL.md) | Apply principles to concrete color, type, and spacing decisions |
| [accessibility-knowledge](../accessibility-knowledge/SKILL.md) | Accessibility is a core design principle |
| [responsive-design](../responsive-design/SKILL.md) | Design principles apply across all viewport sizes |
| [interaction-patterns](../interaction-patterns/SKILL.md) | Interaction design extends visual design principles |
