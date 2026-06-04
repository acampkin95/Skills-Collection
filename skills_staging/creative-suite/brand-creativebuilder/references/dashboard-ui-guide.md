# Dashboard UI Guide for AI Agents

## Table of Contents
1. [Core Convictions](#convictions)
2. [Layout System](#layout)
3. [Data Display](#data)
4. [States & Motion](#states)
5. [Anti-Pattern Catalogue](#anti-patterns)
6. [UK/EU Dashboard Compliance](#compliance)
7. [Self-Check Checklist](#checklist)

---

## Core Convictions

These six principles override generic dashboard patterns from training data.

### 1. Asymmetry Over Grids
No rows of identically-sized cards. Every layout has a clear visual anchor — one element obviously more important than the rest. Use 2fr/1fr grid, not 1fr/1fr/1fr/1fr.

### 2. Typography Is the Interface
Dramatic type scale contrast: 3rem stat next to 0.75rem label. Mono for data values, display for titles, body for descriptions. Numbers are instruments — precise, large, undecorated.

### 3. Earned Colour
Brand palette mostly at 4-12% opacity for surfaces/borders. Full saturation only on active states, CTAs, running indicators. If removing a colour doesn't reduce clarity, remove it.

### 4. Glass Hierarchy, Not Box Hierarchy
Background → glass surface → elevated glass. Three levels maximum. Group with spacing and borders, not nested card containers.

### 5. Show the Pipeline, Not a Dashboard
Progress is the primary data type. Mental model: engineering control panel, not business analytics platform.

### 6. Dense Where It Counts, Spacious Where It Breathes
Pipeline status: dense, data-rich. Hero stats and empty states: spacious, typographic. Contrast in density creates rhythm.

---

## Layout System

### Layout Zones (mandatory before writing JSX)

| Zone | Purpose | Weight |
|------|---------|--------|
| Focal | Most important element | Largest |
| Supporting | Contextualises the focal | Smaller |
| Ambient | Nav, filters, meta | Minimal |

### Layout Rules

1. Max 3 items in a horizontal row
2. Job cards span full width horizontally
3. Filters edge-aligned, not centred
4. One full-bleed element per page
5. Content max-width: 960px

---

## Data Display

### Stats: Type-First
Numbers large (2rem+ mono), small label underneath. Dividers between stats, not card wrappers. No icons next to numbers.

### Pipeline Progress: Inline Timeline
Always horizontal. Connected dots with lines. Active stage pulses with brand glow. Stage names: uppercase mono xs.

### Job Cards: Rows, Not Tiles
Structure: `[Name + Meta] [Stage Timeline] [Actions]` — horizontal glass cards.

### Data Formatting
- Numbers: `font-mono tabular-nums`
- Dimensions: `142.3 × 89.7 × 45.1mm`
- Timestamps: relative ("2m ago"), tooltip for ISO
- File sizes: "14.2 MB"
- Stage names: UPPERCASE mono xs

---

## States & Motion

### Empty States
Left-aligned, typographic. No icon, no illustration. Display font heading + muted description + CTA.

### Loading States
Skeleton shimmer matching content shapes. Active pipeline stage uses `animate-stage-pulse`. Inline spinners (16px) only for micro-actions.

### Error States
Inline, not modal. Small coloured dot + specific message + actionable suggestion.

### Motion Choreography
- Page load: stagger 50ms between zones
- Hover: border-color + translateY(-2px), NEVER scale
- Route: 200ms fade + 4px slide
- Status change: layoutId morphing
- SSE data: INSTANT, no animation
- Max 1 glow element per screen

---

## Anti-Pattern Catalogue

### Layout
| ✗ Ban | ✓ Alternative |
|-------|---------------|
| 4 stat cards in a row | Inline typographic stats with dividers |
| Sidebar nav for ~5 routes | Top navbar horizontal |
| Alternating-row tables | Glass cards with gap |
| Everything centred | Left-align (except hero headlines) |

### Visual
| ✗ Ban | ✓ Alternative |
|-------|---------------|
| Gradient backgrounds on cards | `var(--color-glass)` flat |
| Icon circles next to stats | Colour on the number itself |
| Avatar circles (single-user tool) | Remove entirely |
| Decorative icons in headings | Typography carries headings |
| Charts with default colours | Brand palette, inline labels |

### Interaction
| ✗ Ban | ✓ Alternative |
|-------|---------------|
| Confirm modal for non-destructive | Only for delete/cancel |
| Toast for everything | Background completions/errors only |
| Numbered pagination | Infinite scroll + sticky filters |

### Typography
| ✗ Ban | ✓ Alternative |
|-------|---------------|
| Body font for everything | Three fonts, three roles |
| All same size/weight | Aggressive scale contrast |
| Sentence case for system IDs | Uppercase mono |

---

## UK/EU Dashboard Compliance

### WCAG 2.2 AA (EU Accessibility Act)
- All interactive elements keyboard-accessible
- Visible focus ring on all focusable elements
- Colour never sole information carrier
- `prefers-reduced-motion` respected
- Touch targets ≥ 44×44px

### UK GDPR
- Cookie consent as first-class UI, not popup afterthought
- Data collection forms with clear consent language
- Settings page with data management options

### Both Dark and Light Mode
- Toggle in navbar (mandatory for UK/EU audiences)
- Both themes fully designed, not auto-inverted

---

## Self-Check Checklist

- [ ] Clear focal element, not everything same size
- [ ] Three fonts in correct roles (display / body / mono)
- [ ] Numbers in mono with tabular-nums
- [ ] No single values wrapped in cards
- [ ] Colour earned — status, CTAs, active states only
- [ ] Would another AI generate this layout? If yes, redesign
- [ ] Pipeline control panel feel, not business dashboard
- [ ] Empty/loading/error states fully designed
- [ ] Focus rings and keyboard access on all interactive elements
- [ ] Motion respects prefers-reduced-motion
- [ ] Pantone-derived colours with full spec (CMYK, HEX, RGB)
- [ ] Dark + light mode both functional
