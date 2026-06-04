# Intake & Discovery Reference

## Table of Contents
1. [Client Intake Form](#intake-form)
2. [Brand Strategy Framework](#strategy)
3. [Competitive Analysis](#competitive)
4. [Name Generation Method](#naming)

---

## Client Intake Form

```yaml
brand_basics:
  company_name: ""
  brand_name: ""
  tagline: ""
  mission_statement: ""
  vision_statement: ""
  brand_story: ""

industry_context:
  primary_industry: ""
  sub_sector: ""
  competitors:
    - name: ""
      website: ""
      visual_notes: ""
  differentiators: []

target_audience:
  primary_demographic:
    age_range: ""
    occupation: ""
    technical_level: ""       # Beginner, Intermediate, Expert
  psychographics:
    values: []
    pain_points: []
    aspirations: []

visual_preferences:
  style_direction: ""         # Minimalist, Bold, Classic, Modern, Technical
  avoid: []
  colour_preferences:
    pantone_references: []    # Existing Pantone colours if known
    liked_colours: []         # Descriptive (e.g., "sage green", "warm amber")
    disliked_colours: []
    print_requirements: true  # Does the brand need CMYK/Pantone for print?
  typography_mood: ""
  inspiration_references: []

technical_requirements:
  framework: ""               # Next.js, React, Vue
  styling: ""                 # Tailwind v3/v4
  component_library: ""       # ShadCN, Radix, MUI
  icon_library: ""            # react-icons/ri, lucide-react
  animation_library: ""       # framer-motion, CSS-only
  accessibility_target: "AA"  # WCAG level
  dark_mode: true
  light_mode: true            # UK/EU best practice: both required
  existing_codebase: false
  region: ""                  # UK, EU, AU, US — affects compliance requirements
```

---

## Brand Strategy Framework

### Positioning Statement

```
For [TARGET AUDIENCE],
[BRAND NAME] is the [CATEGORY]
that [KEY BENEFIT]
because [REASON TO BELIEVE].
```

### Brand Personality (4 Attributes)

| Slot | Purpose | Example |
|------|---------|---------|
| Primary | Core identity | Precise |
| Secondary | Supporting quality | Grounded |
| Tertiary | Differentiator | Capable |
| Avoid | What we're NOT | Hype |

### Voice Guidelines

Always provide a Do/Don't pair with concrete examples.

---

## Competitive Analysis

For each competitor (3-5), document:

| Field | What to Record |
|-------|----------------|
| URL | Competitor website |
| Primary colour | HEX + closest Pantone |
| Typography | Font families |
| Layout style | Card grid, editorial, dashboard |
| Tone | Professional, playful, technical |
| Differentiator | Visual identity strength |
| Gap | What we could do differently |

---

## Name Generation Method

### Compound Word Names (Preferred)

1. List 8-10 **action verbs** from the product domain
2. List 8-10 **output nouns** from the product domain
3. Cross-reference for natural compounds
4. Filter: ≤9 chars, uppercase-friendly, no awkward phonetics

### Evaluation Criteria

| Criterion | Weight |
|-----------|--------|
| Phonetic clarity | High |
| Uppercase readability | High |
| Domain fit | High |
| Memorability | Medium |
| Domain availability | Medium |
| No negative associations | Low |

### Presentation

Present 3-4 options with: name in uppercase, etymology (X + Y), one-line framing, mood descriptor.
