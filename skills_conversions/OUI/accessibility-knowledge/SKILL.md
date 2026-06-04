---
name: accessibility-knowledge
description: "WCAG 2.2 accessibility standards, ARIA patterns, inclusive design principles, assistive technology compatibility, and accessibility evaluation for non-CLI agents. Use when evaluating accessibility, understanding ARIA, ensuring inclusive design, checking WCAG compliance, or creating accessible content."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Accessibility (WCAG 2.2)

Web accessibility standards and inclusive design principles. Essential for creating and evaluating content that works for everyone, including users with disabilities.

## WCAG 2.2 Principles (POUR)

### P — Perceivable

Information must be presentable to all users.

```
TEXT ALTERNATIVES (1.1):
├── Images: Meaningful alt text, empty alt for decorative
├── Icons: aria-label or hidden (aria-hidden) if decorative
├── Charts: Describe trend/data in text
├── Video: Captions, transcripts, audio descriptions
└── Complex images: Long description or data table equivalent

TIME-BASED MEDIA (1.2):
├── Audio: Transcripts required
├── Video: Captions + audio description
├── Live: Real-time captions
└── Prerecorded: Full text alternative

ADAPTIVE (1.3):
├── Semantic HTML: Use correct elements (button, nav, main)
├── Meaningful sequence: DOM order = visual order
├── Instructions: Don't rely solely on sensory characteristics
└── Orientation: Support both portrait and landscape

DISTINGUISHABLE (1.4):
├── Color: Don't use color alone to convey info
├── Audio control: Auto-playing audio must have controls
├── Contrast: 4.5:1 (text), 3:1 (large text/UI)
├── Text resize: Up to 200% without loss
├── Images of text: Use actual text, not images
├── Reflow: 320px width without horizontal scroll
├── Spacing: Adjustable line/paragraph/letter/word spacing
└── Hover/focus: Content on hover must be dismissable/hoverable/persistent
```

### O — Operable

Interface must work with various input methods.

```
KEYBOARD (2.1):
├── All functionality via keyboard
├── No keyboard traps
├── Visible focus indicator (3px minimum outline)
├── No specific timing for key presses
├── Character key shortcuts: Can be remapped/turned off
└── Focus order follows meaningful sequence

ENOUGH TIME (2.2):
├── Timing adjustable: Turn off/extend/extend 20x
├── Pause/stop/hide for moving content
├── No time limits unless essential
└── Interruptions: Postpone/suppress allowed

SEIZURES (2.3):
├── No more than 3 flashes per second
├── Red flashes particularly dangerous
└── Animation from interactions: Can be disabled

NAVIGABLE (2.4):
├── Skip to main content link
├── Page title descriptive and unique
├── Focus order logical
├── Link purpose clear from text (or aria)
├── Multiple ways to find pages
├── Headings and labels descriptive
├── Focus visible at all times
├── Focus appearance: ≥2px, ≥3:1 contrast
└── Breadcrumbs for deep hierarchies

INPUT MODALITIES (2.5):
├── Pointer actions: Can be undone
├── Pointer cancellation: Single pointer events cancelable
├── Label in name: Accessible name contains visible text
├── Motion actuation: Can be operated without device motion
├── Target size: ≥24x24px (minimum), ≥44x44px recommended
└── Dragging: Alternative non-drag interface provided
```

### U — Understandable

Content and interface must be comprehensible.

```
READABLE (3.1):
├── Language of page identified (lang attribute)
├── Language of parts identified
├── Unusual words explained
├── Abbreviations expanded
└── Reading level appropriate (aim for 8th grade)

PREDICTABLE (3.2):
├── On focus: No context change
├── On input: No context change (or warned)
├── Consistent navigation: Same order across pages
├── Consistent identification: Same functionality = same labels
└── Change on request: Changes happen only when requested

INPUT ASSISTANCE (3.3):
├── Error identification: Clear, specific error messages
├── Labels/instructions: All inputs labeled
├── Error suggestion: Suggest corrections when possible
├── Error prevention: Confirm important submissions
├── Help: Context-sensitive help available
└── Validations: Inline + real-time where appropriate
```

### R — Robust

Content works across current and future technologies.

```
COMPATIBLE (4.1):
├── Valid HTML: No parsing errors
├── Name/role/state: All UI has proper ARIA
├── Status messages: Announced to assistive tech
└── ARIA: Use correctly (don't conflict with HTML semantics)
```

## ARIA Patterns

### When to Use ARIA

```
RULE: No ARIA is better than bad ARIA

USE ARIA WHEN:
├── HTML semantics insufficient (custom widgets)
├── Dynamic content updates (live regions)
├── Complex interactive components
└── Communicating state to assistive technology

DON'T USE ARIA WHEN:
├── Semantic HTML already does the job
├── A native element exists (use <button>, not <div role="button">)
├── Adding roles that duplicate native semantics
└── Uncertain about the correct pattern
```

### Essential ARIA Attributes

```
ROLES:
├── role="alert"         → Announce important changes
├── role="dialog"        → Modal dialog
├── role="navigation"    → Navigation landmark
├── role="tablist/tabs"  → Tab interface
├── role="tree"          → Hierarchical list
├── role="grid"          → Data grid
└── role="search"        → Search landmark

STATES & PROPERTIES:
├── aria-expanded         → Element is open/closed
├── aria-selected         → Item is selected
├── aria-checked          → Checkbox/radio state
├── aria-disabled         → Visually disabled, not focusable
├── aria-hidden           → Hidden from assistive tech
├── aria-label            → Accessible name (no visible text)
├── aria-labelledby       → Points to visible label element
├── aria-describedby      → Points to description element
├── aria-live="polite"    → Announce changes when idle
├── aria-live="assertive" → Announce changes immediately
├── aria-atomic           → Announce entire region, not just changes
└── aria-current          → Current item in set (page, step, etc.)
```

### Common Component Patterns

```
MODAL DIALOG:
├── role="dialog" on container
├── aria-modal="true"
├── aria-labelledby → dialog title
├── Focus trapped inside when open
├── Focus returns to trigger on close
├── Escape key closes
└── Background inert (aria-hidden)

TABS:
├── role="tablist" → container
├── role="tab" → each tab button
├── role="tabpanel" → each panel
├── aria-selected → active tab
├── aria-controls → tab→panel link
├── aria-labelledby → panel→tab link
├── Arrow keys navigate between tabs
├── Home/End → first/last tab
└── Tab key moves to panel content

DROPDOWN MENU:
├── aria-haspopup="true" on trigger
├── aria-expanded on trigger (true/false)
├── role="menu" on container
├── role="menuitem" on each item
├── Arrow keys navigate items
├── Escape closes menu
└── Focus returns to trigger on close
```

## Accessibility Testing Checklist

### Quick Audit (5 minutes)

```
KEYBOARD NAVIGATION:
├── [ ] Tab through entire page — logical order?
├── [ ] All interactive elements reachable?
├── [ ] Focus indicator visible on every element?
├── [ ] No keyboard traps?
├── [ ] Escape closes modals/dropdowns?
└── [ ] Skip navigation link works?

VISUAL CHECKS:
├── [ ] Text readable at 200% zoom?
├── [ ] No horizontal scroll at 320px?
├── [ ] Color not the only indicator of information?
├── [ ] Contrast adequate (text/UI elements)?
├── [ ] Form labels visible and connected?
└── [ ] Error messages clear and specific?

CONTENT CHECKS:
├── [ ] Images have meaningful alt text?
├── [ ] Headings form logical hierarchy (h1→h2→h3)?
├── [ ] Links descriptive (not "click here")?
├── [ ] Forms have visible labels?
├── [ ] Page has descriptive title?
└── [ ] Language attribute set on <html>?
```

### ARIA Quality Rules

```
NEVER:
├── Use role="button" on a <div> when you can use <button>
├── Use aria-hidden="true" on focusable elements
├── Duplicate visible text in aria-label
├── Use role="presentation" on interactive elements
├── Change ARIA roles dynamically (change states instead)
└── Use aria-roledescription without testing with screen readers

ALWAYS:
├── Test with actual keyboard navigation
├── Use native HTML elements first
├── Ensure ARIA matches visual behavior
├── Announce dynamic content changes (aria-live)
├── Provide accessible names for interactive elements
└── Maintain focus management in single-page apps
```

## WCAG 2.2 New Criteria (Since 2.1)

```
NEW IN 2.2 (not in 2.1):
├── 2.4.11 Focus Appearance (AAA → AA): Focus indicator ≥ 2px, ≥ 3:1 contrast
├── 2.4.12 Focus Not Obsscured (AA): Focus must not be hidden by sticky headers
├── 2.5.7 Dragging Movements (AA): Actions requiring dragging must have single-pointer alternative
├── 2.5.8 Target Size — Minimum (AA): ≥ 24x24px (was 44x44 in 2.1 AAA, now relaxed at AA)
├── 3.2.6 Consistent Help (A): Help mechanism appears in same relative order across pages
├── 3.3.7 Redundant Entry (A): Don't ask for previously entered information again
├── 3.3.8 Accessible Authentication (AA): Cognitive function tests not required for login
└── 3.3.9 Accessible Authentication (AAA): No object recognition or personal content in auth
```

## Assistive Technology Behavior Reference

| Technology | What It Does | Key Considerations |
|-----------|-------------|-------------------|
| **Screen reader** | Reads page via speech/Braille | Relies on DOM order, ARIA, semantic HTML |
| **Screen magnifier** | Enlarges portion of screen | Layout breaks at 2-20x zoom, CLS critical |
| **Voice control** | Operates by speaking commands | Needs visible labels matching accessible names |
| **Switch access** | Single button scanning navigation | Tab order and focus management critical |
| **Eye tracking** | Gaze-based pointer | Large targets, adequate spacing |
| **Braille display** | Tactile output | Concise text, proper heading structure |
| **Reading assistant** | Simplifies/corrects text | Clear language, short sentences help |

### Common Failure Patterns

```
TOP 10 MOST COMMON A11Y FAILURES:
├── 1. Low contrast text (4.5:1 for normal, 3:1 for large)
├── 2. Missing alt text on informative images
├── 3. Empty or generic link text ("click here", "read more")
├── 4. Missing form labels (placeholder is NOT a label)
├── 5. No keyboard focus indicator
├── 6. Missing document language (<html lang="en">)
├── 7. Improper heading hierarchy (skipping h2, using h1 for style)
├── 8. Autoplay media without controls
├── 9. Timeouts without warning or extension option
└── 10. Captcha without accessible alternative
```

## When to Use

- Ensuring content and UI meet WCAG 2.2 guidelines
- Writing accessible HTML with proper ARIA attributes
- Evaluating color contrast ratios and text readability
- Designing keyboard-navigable interfaces
- Creating accessible forms, tables, and interactive components

## Limitations

- WCAG compliance alone does not guarantee usable experiences
- Screen reader behavior varies across browsers and platforms
- Automated testing catches ~30% of accessibility issues — manual testing is essential
- Cognitive accessibility guidelines are less standardized than physical/sensory

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [design-principles](../design-principles/SKILL.md) | Accessibility is a fundamental design principle |
| [visual-design](../visual-design/SKILL.md) | Color contrast and text sizing directly affect accessibility |
| [responsive-design](../responsive-design/SKILL.md) | Responsive design impacts zoom and reflow accessibility |
| [modern-web-standards](../modern-web-standards/SKILL.md) | Semantic HTML is the foundation of accessibility |
