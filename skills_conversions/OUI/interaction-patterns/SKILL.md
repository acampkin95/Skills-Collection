---
name: interaction-patterns
description: "UI interaction patterns, micro-interactions, transitions, state management, loading states, error states, empty states, and feedback patterns for non-CLI agents. Use when designing interactions, creating transition effects, handling loading/error/empty states, or building feedback mechanisms."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Interaction Patterns

UI interaction patterns, micro-interactions, state handling, transitions, and feedback mechanisms for creating responsive, intuitive interfaces.

## Interaction Design Principles

### Feedback Hierarchy

```
IMMEDIATE (< 100ms):
├── Button press state (color change, scale)
├── Hover effects (desktop only)
├── Focus indicators
└── Toggle switches

QUICK (100ms - 1s):
├── Form field validation
├── Toggle/switch completion
├── Dropdown open/close
├── Accordion expand
└── Checkbox/radio state change

MODERATE (1s - 5s):
├── Form submission
├── Content save
├── Search results loading
├── File upload progress
└── Page transition

LONG (> 5s):
├── Large file processing
├── Report generation
├── Data import
└── Background sync
```

## State Management Patterns

### The Eight States of UI

```
EVERY COMPONENT CAN BE IN THESE STATES:

1. NOTHING (initial)     → Nothing has happened yet
2. LOADING               → Waiting for data
3. EMPTY                 → Data loaded but nothing there
4. IDEAL (happy path)    → Everything works perfectly
5. PARTIAL               → Some data missing
6. ERROR                 → Something went wrong
7. EDITABLE              → User can modify
8. TOO MUCH              → Overwhelming amount of data

DESIGN ALL EIGHT. Skip none.
```

### Loading Patterns

```
SKELETON (preferred for content):
┌──────────────────────────┐
│ ████████████              │  ← Title placeholder
│ ████████                  │  ← Subtitle
│ █████████████████████████ │  ← Text line
│ ███████████████████       │  ← Text line
│ ██████████████████████    │  ← Text line
└──────────────────────────┘
Use when: Loading structured content (cards, lists, articles)

SPINNER (for short waits):
┌──────────────────────────┐
│                          │
│        ⟳ Loading...     │
│                          │
└──────────────────────────┘
Use when: Action-based loading (save, submit), < 5 seconds

PROGRESS BAR (for known duration):
┌──────────────────────────┐
│ ████████░░░░░░░░  47%    │
└──────────────────────────┘
Use when: Known progress (file upload, processing)

LAZY PROGRESS (for unknown duration):
┌──────────────────────────┐
│ ████████████░░░░░░░░░░░  │  ← Indeterminate animation
└──────────────────────────┘
Use when: Unknown duration but want to show activity

RULES:
├── Skeleton for initial page load (perceived performance)
├── Spinner for user-initiated actions
├── Progress bar when % completable is known
├── Always provide text context ("Loading articles...")
└── Never show empty state during loading
```

### Error State Patterns

```
INLINE ERROR (form validation):
┌──────────────────────────┐
│ Email:                   │
│ ┌──────────────────────┐ │
│ │ abc@notemail         │ │
│ └──────────────────────┘ │
│ ⚠ Please enter a valid   │
│   email address          │
└──────────────────────────┘

ERROR BANNER (page-level):
┌──────────────────────────────────┐
│ ⚠ Something went wrong           │
│ Unable to save changes.           │
│ [Try Again] [Dismiss]             │
└──────────────────────────────────┘

FULL PAGE ERROR:
┌──────────────────────────────────┐
│                                  │
│         ⚠                        │
│   Page Not Found                 │
│   The page you're looking for    │
│   doesn't exist.                 │
│                                  │
│   [Go Home] [Go Back]            │
│                                  │
└──────────────────────────────────┘

ERROR MESSAGE RULES:
├── Say what happened (not "Error 500")
├── Say what to do about it (actionable)
├── Be human, not technical
├── Include retry mechanism
├── Preserve user's work
├── Distinguish: User error vs System error
└── Log technical details, show friendly message
```

### Empty State Patterns

```
FIRST-TIME EMPTY (never had data):
┌──────────────────────────────────┐
│                                  │
│        📝                        │
│   No articles yet                │
│   Create your first article      │
│   to get started.                │
│                                  │
│   [+ New Article]                │
│                                  │
└──────────────────────────────────┘

FILTERED EMPTY (data exists but filtered out):
┌──────────────────────────────────┐
│                                  │
│        🔍                        │
│   No matching articles           │
│   Try adjusting your filters     │
│   or search terms.               │
│                                  │
│   [Clear Filters]                │
│                                  │
└──────────────────────────────────┘

CLEARED EMPTY (user deleted everything):
┌──────────────────────────────────┐
│                                  │
│        ✅                        │
│   All articles archived          │
│   Your workspace is empty.       │
│                                  │
│   [Create New] [View Archive]    │
│                                  │
└──────────────────────────────────┘

RULES FOR EMPTY STATES:
├── Explain WHY it's empty
├── Provide next action (CTA button)
├── Use illustration or icon (not just text)
├── Keep tone positive/encouraging
├── Don't use for error states
└── Distinguish between first-time and filtered
```

## Micro-Interactions

### Button States

```
BUTTON STATE TRANSITIONS:
─────────────────────────
DEFAULT → HOVER → ACTIVE → FOCUS → LOADING → DISABLED

DEFAULT: Resting state, clear affordance
HOVER:   Subtle feedback (0.15s transition)
         Background darken/lighten, slight shadow
ACTIVE:  Pressed state (scale 0.98, deeper color)
FOCUS:   Visible focus ring (3px, 2:1 contrast minimum)
LOADING: Spinner replaces text, button disabled
DISABLED: Reduced opacity (0.5), no pointer events

TRANSITION:
transition: all 150ms ease

DON'T:
├── Don't use abrupt state changes
├── Don't make hover effects too subtle to notice
├── Don't forget focus states
├── Don't change button size on hover (causes layout shift)
└── Don't use hover states on mobile (no hover)
```

### Transition Patterns

```
ENTER (element appears):
├── Fade in: opacity 0 → 1 (200ms)
├── Slide in: translateY(10px) → 0 (200ms)
├── Scale up: scale(0.95) → 1 (150ms)
└── Combined: fade + slide (most common)

EXIT (element disappears):
├── Fade out: opacity 1 → 0 (150ms, faster than enter)
├── Slide out: translateY(0) → -10px (150ms)
├── Scale down: scale(1) → 0.95 (100ms)
└── Combined: fade + slide

SHARED ELEMENT (element moves between contexts):
├── View Transitions API (page-level)
├── Layout animations (FLIP technique)
├── Container morphing
└── Key: Maintain visual continuity

TIMING:
├── Micro (hover, press): 100-200ms
├── Small (toggle, expand): 200-300ms
├── Medium (modal, page): 300-500ms
├── Large (layout change): 400-600ms
└── Easing: ease-out for enter, ease-in for exit

REDUCED MOTION:
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

## Common Interaction Patterns

### Disclosure / Accordion

```
PATTERN:
┌──────────────────────────┐
│ Section Title        ▼   │  ← Click to expand
├──────────────────────────┤
│ Section Title        ▲   │  ← Expanded
│ Content is now visible   │
│ and accessible.          │
└──────────────────────────┘

RULES:
├── Only one section open, or multiple (decide)
├── Smooth height animation
├── Chevron rotates (▼ ↔ ▲)
├── aria-expanded on trigger
├── aria-controls linking trigger to panel
└── Keyboard: Enter/Space to toggle
```

### Modal / Dialog

```
PATTERN:
┌─────────────────────────────────────┐
│ ░░░░░░░░░░░ Overlay ░░░░░░░░░░░░░░ │
│ ░░░░┌─────────────────────────┐░░░░ │
│ ░░░░│ Title            [✕]    │░░░░ │
│ ░░░░│                         │░░░░ │
│ ░░░░│ Dialog content          │░░░░ │
│ ░░░░│                         │░░░░ │
│ ░░░░│ [Cancel]  [Confirm]     │░░░░ │
│ ░░░░└─────────────────────────┘░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────┘

RULES:
├── Focus trapped inside modal
├── Escape key closes
├── Click outside to close (optional)
├── Focus returns to trigger on close
├── Background page is inert (aria-hidden)
├── Scroll locked on background
├── Entry: Fade in overlay, scale up dialog
└── Exit: Fade out overlay, scale down dialog
```

### Toast / Notification

```
PATTERN:
                                    ┌─────────────────────┐
                                    │ ✓ Saved successfully │
                                    │               [Undo] │
                                    └─────────────────────┘

TYPES:
├── Success (green): Action completed
├── Error (red): Something failed
├── Warning (amber): Attention needed
└── Info (blue): Informational

RULES:
├── Position: Bottom-right or top-center
├── Auto-dismiss: 5-8 seconds
├── Dismissable: Swipe or X button
├── Don't stack more than 3
├── Don't use for critical errors (use inline)
├── Include undo for destructive actions
├── Accessible: aria-live="polite"
└── Entry: Slide in from edge
```

### Pull-to-Refresh (Mobile)

```
PATTERN:
┌───────────────────┐
│     ⟳ Refreshing  │  ← Pull down reveals
├───────────────────┤
│                   │
│  Content          │
│                   │

STATES:
1. Idle: No indicator
2. Pulling: Arrow appears, threshold not met
3. Ready: Arrow rotates, threshold met (release to refresh)
4. Refreshing: Spinner, data loading
5. Complete: Checkmark briefly, then idle

RULES:
├── Clear threshold indicator
├── Provide feedback at each state
├── Auto-dismiss after refresh
└── Don't use for non-refreshable content
```

## Animation Performance

```
PERFORMANT PROPERTIES (GPU-accelerated):
├── transform: translate(), scale(), rotate()
├── opacity
└── filter (some browsers)

AVOID ANIMATING (causes layout/paint):
├── width, height
├── top, left, right, bottom
├── margin, padding
├── border-width
└── font-size

PATTERN:
Instead of animating height: auto →
├── Use max-height with overflow: hidden
├── Use transform: scaleY()
├── Use CSS Grid with grid-template-rows: 0fr → 1fr
└── Use the FLIP technique for layout changes
```


## When to Use

- Designing state management patterns for UI components
- Implementing micro-interactions and animation feedback
- Building form validation, drag-and-drop, and modal patterns
- Optimizing animation performance for smooth 60fps experiences
- Choosing appropriate interaction patterns for a given UI problem

## Limitations

- Animation preferences vary — some users prefer reduced motion
- Pattern applicability depends on framework and platform capabilities
- Over-animation can harm usability and performance
- Accessibility requirements may constrain interaction choices

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [design-principles](../design-principles/SKILL.md) | Interaction design extends visual design principles |
| [accessibility-knowledge](../accessibility-knowledge/SKILL.md) | Interactions must be keyboard-accessible and screen-reader friendly |
| [responsive-design](../responsive-design/SKILL.md) | Interaction patterns must work across device types |
| [web-performance](../web-performance/SKILL.md) | Animation performance directly impacts Core Web Vitals |
