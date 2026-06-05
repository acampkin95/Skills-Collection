---
name: brand-creativebuilder
description: End-to-end brand identity builder with Pantone colour systems, SVG logos, favicons.
---

# Brand Creative Builder

End-to-end brand identity system builder. The primary deliverable is a **single self-contained interactive HTML brand guide** (~2500–3000 lines) with Pantone-specified colours, SVG logos, live animation demos, production code, and AI prompt libraries.

**This skill enforces three research gates.** No design decisions are made from memory or assumption alone — every phase is informed by targeted web research into the product's market, audience, design landscape, and current trends.

## Reference Files

```
references/intake-discovery.md        — Intake form, naming, strategy
references/visual-identity.md         — Pantone, type, SVG logo, favicon, UK/EU 2026
references/dashboard-ui-guide.md      — Anti-patterns, layout zones, states/motion
references/brand-guide-template.md    — HTML template, Pantone swatch CSS, code patterns
references/ai-prompt-library.md       — Recraft SVG + ElevenLabs video prompts
references/library-matrix.md          — 3rd party stack per vertical
references/svg-icon-visual-library.md — Inline SVG icons, interactive demos, component snippets
```

Read the relevant reference file BEFORE executing each phase. Don't work from memory.

---

## Enforced Research Gates

Three research stages are **mandatory**. They are not optional enhancements. The build process halts at each gate until research is completed and findings are documented.

### Research Gate Overview

| Gate | When | Type | Searches | Purpose |
|------|------|------|----------|---------|
| **R1** | After audit, before questions | Broad scan | 5-8 web searches | Understand market, competitors, audience expectations |
| **R2** | After brief confirmed, before visual system | Deep research | 1 deep research + 5-7 searches | Design trends, colour psychology, typography, localisation |
| **R3** | After HTML guide built, before delivery | Refinement scan | 5-6 web searches | Validate copywriting, check competitor drift, verify trend currency |

### Research Rules

1. **Use `web_search` for targeted queries** — short, specific, 1-6 words each
2. **Use `web_fetch` to read full articles** when search snippets are insufficient
3. **Never skip a gate** — even if you think you know the answer, search to verify
4. **Document findings** — summarise key insights from each gate before proceeding
5. **Research informs, doesn't dictate** — findings shape recommendations but the user's confirmed preferences always override
6. **Adapt queries to the brand's region** — if UK/EU, search with UK/EU context; if AU, search with AU context
7. **Search in the user's language/locale** when researching copywriting and localisation

---

## Process: Exact Build Sequence

### Phase 0: Audit & Intake

**0.1 — Silent audit (before asking anything)**

If a live product or codebase exists, read these files first:
1. `package.json` → framework, dependencies, icon library, animation library
2. `globals.css` / `tailwind.config` → current colours, fonts, radii, shadows
3. `layout.tsx` → metadata, font imports, body classes
4. `Navbar.tsx` or equivalent → brand text, logo, active indicator patterns
5. `AnimatedBackground` or equivalent → wireframe/mesh colours
6. Screenshot the running app if browser tools available

Document: current font family, primary hex, background hex, accent colours, border treatments, component library, animation library.

---

### ◆ RESEARCH GATE 1: Market & Competitor Scan

**MANDATORY — 5-8 web searches before presenting any questions to the user.**

Execute these searches, adapting queries to the product domain:

| # | Query Pattern | What You're Looking For |
|---|---------------|------------------------|
| 1 | `[product category] brand design 2026` | Current visual trends in the product's sector |
| 2 | `[product category] competitor websites` | Who the visual competitors are, what palette/type/layout they use |
| 3 | `[product category] target audience demographics` | Age, tech literacy, device usage, expectations |
| 4 | `[product category] UI UX trends 2026` | Specific interaction patterns popular in this space |
| 5 | `best [product category] website design examples` | Inspiration and quality benchmarks |
| 6 | `[product category] colour psychology branding` | Which colours convey the right meaning for this domain |
| 7 | `[region] web design preferences [year]` | Regional expectations (UK users expect dark mode, etc.) |
| 8 | `[product category] naming conventions brands` | How competitors name themselves, linguistic patterns |

**After completing R1, document a brief (5-10 bullet points):**
- What visual patterns dominate the sector
- Colour palettes used by top 3-5 competitors
- Typography trends in the space
- Audience expectations and device usage
- Regional/cultural design norms
- Gaps and opportunities for visual differentiation

**Use R1 findings to tailor the structured questions** — the aesthetic options you offer should be informed by what you've found, not generic defaults. If the sector is dominated by blue tech palettes, offer a sage/green alternative as a differentiator.

---

**0.2 — Structured questions (max 3 via ask_user_input)**

Only ask about gaps not answered by the audit or conversation history. **Tailor options based on R1 findings.**

Question 1 — Name direction (if naming needed): Generate 3-4 compound-word options informed by naming conventions found in R1.

Question 2 — Visual aesthetic: Offer 4 directions. At least one should be a **differentiator** identified in R1 (e.g., if competitors are all dark/blue, offer warm/earthy as an option).

Question 3 — Colour mood: Offer 4 palettes. Reference what R1 found about colour psychology in this sector.

**0.3 — Open-ended preferences** (one prose question):
> "Any design preferences? Existing Pantone references, fonts you love or hate, reference brands, print requirements, directions to avoid?"

**0.4 — Confirm brief** (5-8 lines) before proceeding. Include a 1-2 line "research insight" noting the key finding from R1 that shaped the recommendations.

---

### Phase 1: Brand Identity Definition

With confirmed brief, define ALL of these before touching HTML:
- Brand name (always UPPERCASE for wordmark)
- Tagline (sentence case, ≤6 words)
- Positioning statement: `For [audience], [brand] is the [category] that [benefit]`
- Personality: 3 traits + 1 "avoid" (use info-card grid)
- Voice: Do/Don't pair with concrete examples

Read `references/intake-discovery.md` for templates.

---

### ◆ RESEARCH GATE 2: Deep Design Research

**MANDATORY — 1 deep research phase + 5-7 web searches after brief is confirmed, before any visual system decisions.**

This is the most important research gate. It directly shapes every visual decision.

#### Deep Research Phase

If the `deep_research` tool is available, use it with a query like:
> "Current [year] design trends for [product category] targeting [audience] in [region]. Include colour systems, typography trends, layout patterns, animation approaches, glassmorphism usage, accessibility requirements, and competitive visual positioning for [specific competitors if known]."

If deep research is not available, execute 8-10 focused web searches to cover the same ground.

#### Targeted Searches (5-7 minimum)

| # | Query Pattern | What You're Looking For |
|---|---------------|------------------------|
| 1 | `design trends 2026 [product vertical]` | Specific visual patterns for this year |
| 2 | `best fonts [product category] 2026 variable` | Typography recommendations with variable font options |
| 3 | `Pantone colour of the year 2026 [mood]` | Current Pantone trends matching the chosen direction |
| 4 | `[competitor name] website design analysis` | Specific competitor deep-dive (repeat 2-3 times) |
| 5 | `[region] accessibility requirements web 2026` | Latest compliance standards (EU Accessibility Act, WCAG 2.2) |
| 6 | `[product category] copywriting tone voice examples` | How the best brands in this space write |
| 7 | `[target audience] design preferences expectations` | What this audience responds to visually |

#### Additional Searches (if needed)

| # | Query Pattern | Purpose |
|---|---------------|---------|
| 8 | `glassmorphism neumorphism 2026 best practices` | Current state of depth/glass trends |
| 9 | `micro interaction patterns [product category]` | Animation patterns specific to this space |
| 10 | `[language/locale] brand localisation tips` | Localisation for non-English or multi-region brands |

#### Document R2 Findings

Before proceeding to visual system design, compile:

1. **Colour recommendation** — which Pantone families align with the trend research + user's chosen mood, with reasoning
2. **Typography recommendation** — 2-3 font pairings with rationale based on trend research
3. **Layout recommendation** — which layout patterns (bento, asymmetric focal, editorial) best fit the product and audience
4. **Copywriting tone** — specific vocabulary, sentence length, and register based on competitor analysis and audience research
5. **Localisation notes** — spelling conventions (UK/AU/US), date formats, currency, measurement units, cultural design norms
6. **Accessibility requirements** — which specific WCAG level + any regional legal obligations
7. **Differentiation opportunities** — where the brand can visually stand apart from what R2 found competitors doing

**Present the R2 summary to the user** as a brief set of recommendations (not a wall of text). Frame as: "Based on research into [sector] trends and [competitor] landscape, I'd recommend..." Let the user confirm or adjust before committing to the visual system.

---

### Phase 2: Visual System Design

**Informed by R2 findings.** Every decision here should trace back to a research insight.

**Colours** — read `references/visual-identity.md`
- Select Pantone anchor colours justified by R2 colour research
- Derive 11-step digital scales (50–950) from each anchor
- Define semantic colours with Pantone refs
- Define surface colours (glass, border, hover as rgba)
- Test all text/bg pairs against WCAG 2.2 AA

**Typography** — select 3 families justified by R2 font research
- Display (headings): justify choice with trend data
- Body (text): justify choice with readability research
- Mono (data): JetBrains Mono or Geist Mono

**Logo** — stroked SVG, 1.5-2px, no fills, works at 24px-512px

**Favicon** — ICO, SVG, PNG set, apple-touch-icon, manifest

**Copywriting** — apply R2 tone/voice findings to:
- Tagline wording
- Positioning statement language
- Do/Don't voice examples
- Section descriptions in the guide
- Empty state copy, error messages, UI labels

---

### Phase 3: Build the HTML Guide

This is the primary deliverable. **Single self-contained HTML file.**

Read `references/brand-guide-template.md` for the template structure.

#### Construction Order (follow this sequence)

1. **Head** — charset, viewport, Google Fonts link, open `<style>` tag
2. **CSS Design Tokens** — `:root` block with all colour scales, surfaces, fonts, spacing, radii
3. **CSS Base** — reset, html/body, ::selection, heading hierarchy, paragraph defaults
4. **CSS Navigation** — fixed left nav (256px), brand lockup, sections, links, active state
5. **CSS Components** — scale strips, Pantone swatches, info cards, logo showcase, blueprint bg, type samples, code blocks, copy buttons, do/don't grid, stage rows, toast
6. **CSS Responsive** — 768px breakpoint
7. **CSS Agent Guide** — principle cards, pattern cards, rule rows, agent callouts
8. **CSS Systems** — Pantone grid, icon grid, pipeline demo, glass card demo, contrast demo, animation demos, library matrix tables
9. **Close style, open body**
10. **Nav HTML** — brand lockup with inline SVG, section groups, links, version
11. **20 content sections** in order (see Nav Section Groups below)
12. **Toast div**
13. **Script** — copyHex(), copyBlock(), IntersectionObserver, nav handlers

#### Component Density Targets

| Component | Count | Purpose |
|-----------|-------|---------|
| Pantone swatch cards | 8-12 | Brand + semantic colours |
| Scale strip steps | 22 (2 × 11) | Primary + neutral |
| Visual SVG icons | 15-20 | Browsable icon reference |
| Info cards | 40-60 | Brand facts, personality, principles |
| Rule rows | 50-70 | Dashboard, a11y, formatting rules |
| Principle cards | 6 | Dashboard convictions |
| Pattern cards (good/bad) | 4-8 | Visual comparisons |
| Animation demos | 6 | Live CSS keyframes |
| Pipeline demo stages | 5 | Horizontal progress |
| Glass card demos | 2 | Hoverable job rows |
| Contrast pairs | 5 | WCAG pass/fail |
| Library matrix tables | 3 | Foundation + vertical + comparison |
| Code blocks with copy | 10-15 | Config, patterns |
| Do/Don't grids | 3-5 | Voice, logo, dashboard |

### Phase 4: Populate Supporting Content

- **AI prompt library** — `references/ai-prompt-library.md`
- **Library/stack matrix** — `references/library-matrix.md`
- **Dashboard UI guide** — `references/dashboard-ui-guide.md`
- **SVG icon reference** — `references/svg-icon-visual-library.md`

---

### ◆ RESEARCH GATE 3: Refinement & Validation Scan

**MANDATORY — 5-6 web searches after the HTML guide is built, before delivery.**

This gate catches stale recommendations, validates copy quality, and ensures the brand doesn't accidentally mirror a competitor's recent rebrand.

| # | Query Pattern | Purpose |
|---|---------------|---------|
| 1 | `[brand name] trademark search` | Check the chosen name doesn't conflict with existing marks |
| 2 | `[competitor 1] rebrand 2025 2026` | Check if top competitors have recently rebranded (avoid accidental similarity) |
| 3 | `[chosen font name] web font performance 2026` | Verify the font choice is well-supported and performant |
| 4 | `[product category] tagline examples best` | Benchmark the tagline against industry best practice |
| 5 | `[chosen Pantone colour] brand associations` | Verify the colour doesn't have unintended cultural associations |
| 6 | `[target audience] [region] digital behaviour 2026` | Final check on audience expectations |

#### R3 Actions

After completing the searches:

1. **Trademark check** — if the brand name has conflicts, flag to the user with alternatives
2. **Competitor drift** — if a competitor recently adopted a similar palette/aesthetic, note the overlap and suggest a differentiating adjustment
3. **Font validation** — confirm the font is available on Google Fonts, has good CWV scores, and supports the required character sets (Latin Extended for EU, etc.)
4. **Tagline polish** — if the research surfaces stronger phrasing patterns, suggest an alternative (present both options)
5. **Colour association check** — if the Pantone choice has problematic associations in the target region, flag and recommend an alternative
6. **Copywriting localisation** — verify spelling conventions match the target region (colour vs color, organisation vs organization, etc.)

**Apply R3 findings** — make any final adjustments to the guide before packaging. If changes are significant, highlight them in the delivery summary.

---

### Phase 5: Package & Deliver

#### 5.1 Primary Deliverables

1. **Interactive HTML Brand Guide** → `/mnt/user-data/outputs/{brand}-brand-guide.html`
2. **brand-creativebuilder Skill** → `/mnt/user-data/outputs/brand-creativebuilder.skill` (if skill was updated)

#### 5.2 Research & Decisions Report (MANDATORY)

Generate a formal research report as the final output. This documents every decision and its research backing, serving as the audit trail for the brand identity. **The report is not optional — it is a core deliverable.**

**Format:** DOCX generated via `docx` (npm), then converted to PDF via LibreOffice.

**Report Structure (9 sections):**

1. **Executive Summary** — product, name, tagline, Pantone anchor, typography
2. **Product Audit** — table of files audited with key findings
3. **Research Gate 1** — R1 search queries + findings table, how R1 shaped questions
4. **User Intake** — questions, options, selections, confirmed brief
5. **Research Gate 2** — R2 search queries + findings, recommendations confirmed
6. **Visual System Decisions** — colour table (Pantone+CMYK+HEX+usage), typography table, logo description
7. **Research Gate 3** — R3 validation checks + results, actions taken
8. **Deliverables** — component inventory with exact counts
9. **Migration Plan** — find-and-replace table, package changes, pending tasks

**Generation:** Use `docx` npm library → validate with `validate.py` → convert to PDF via `soffice.py --headless --convert-to pdf`. Use A4 for AU/UK (11906 × 16838 DXA), US Letter for US (12240 × 15840 DXA). Brand accent colour for table header rows. Arial font throughout.

**Output files:**
- `/mnt/user-data/outputs/{BRAND}-Brand-Research-Report.docx`
- `/mnt/user-data/outputs/{BRAND}-Brand-Research-Report.pdf`

#### 5.3 Delivery

1. Use `present_files` to deliver all outputs (HTML guide first, then report)
2. Provide concise summary including:
   - What's defined
   - Key research insights that shaped the recommendations
   - Migration steps (if rebrand)
   - Next steps (apply config, generate assets with prompts)
   - Any R3 flags (trademark concerns, competitor overlap, etc.)

**Complete delivery package:**
```
/mnt/user-data/outputs/
├── {brand}-brand-guide.html              # Interactive brand guide (primary)
├── {BRAND}-Brand-Research-Report.docx    # Research & decisions report
├── {BRAND}-Brand-Research-Report.pdf     # PDF version of report
└── brand-creativebuilder.skill           # Skill package (if updated)
```

---

## Research Integration Examples

### Example: POURFORM (Fabrication Tool)

**R1 searches executed:**
- `photo to mould silicone casting tool brand` → found maker/fabrication space dominated by dark UIs
- `3D printing mould maker competitors` → identified clean technical aesthetic gap
- `maker community design preferences` → audience expects precision, not playfulness
- `fabrication tool UI examples 2026` → pipeline-style UIs common, sage/green uncommon
- `Australia web design trends 2026` → dark mode expected, mobile-first, WCAG AA

**R1 findings shaped questions:** offered "clean technical" and "sage/stone" as options because research showed competitors cluster around blue/dark/neon while the maker audience values natural/material tones.

**R2 deep research:**
- Confirmed Outfit as trending geometric sans for technical tools
- Found Pantone 16-6116 TPX (Shale Green) as closest match to chosen mood
- Verified DM Sans as high-readability body font with good CWV scores
- Identified glassmorphism with sage tint as differentiated from cold-blue glass used by competitors
- Confirmed EU Accessibility Act requires WCAG 2.2 AA

**R3 validation:**
- Verified "POURFORM" has no trademark conflicts in AU/UK
- Confirmed Outfit Variable available on Google Fonts with Latin Extended
- Checked no major competitor rebranded to sage/green recently
- Validated AU English spelling (colour, organisation, behaviour) throughout guide

---

## Process Notes & Learnings

### What Makes a Brand Guide Feel "Designed" vs "Generated"

1. **Pantone cards, not hex swatches** — Pantone name + CMYK + HEX + RGB signals professional specification
2. **Visual SVG icon grid** — 20 icons rendered inline in a hoverable grid
3. **Live animation demos** — 6 minimum: pulse, shimmer, glow, float, hover, stagger
4. **Interactive pipeline demo** — 5-stage horizontal progress with completed/running/pending states
5. **Contrast checker** — 5 live colour pairs with pass/fail badges
6. **Glass card demo** — 2 hoverable job rows with inline pipeline dots
7. **Typography-first stat display** — 2rem mono numbers with dividers, no icon cards
8. **Research-backed recommendations** — every colour, font, and layout choice traceable to a specific search finding

### Common Failure Modes

1. **Building before defining** — complete Phase 0-2 + R1/R2 before any HTML
2. **Fragile str_replace chains** — if >5 edits needed, rebuild the section
3. **Missing role/tabindex** — every clickable element needs keyboard access
4. **Uniform font weights** — guide must demonstrate the type system it documents
5. **Uniform grids** — bento-style, featured primary spanning 2 cols
6. **Missing reduced-motion** — implement in guide CSS AND document in animation section
7. **Missing toast feedback** — every copy action needs visual confirmation
8. **Skipping research gates** — the most common failure. Research catches naming conflicts, competitor overlap, and stale trend assumptions. Never skip.

### Iteration Pattern

The guide grows in 4 layers:
- **Layer 1**: Core identity (brand → logo → colours → type → visual language → Tailwind → components → stages)
- **Layer 2**: Dashboard guide (principles → layout → data → states → anti-patterns)
- **Layer 3**: Systems (iconography → animation → accessibility)
- **Layer 4**: Enhancements (interactive demos → library matrix → Pantone upgrade)

Build, verify, then add next layer. Don't attempt all 4 in one pass.

### Research Report Generation

The report is the final build step — generated AFTER the HTML guide is complete and R3 validation is done. It is a formal DOCX/PDF document serving as the audit trail for every design decision.

**Why it matters:** Proves decisions were research-backed. Prevents "why that colour?" conversations months later. For client work, demonstrates professional rigour. For internal projects, captures institutional knowledge.

**Implementation:** Use `docx` npm library (not raw XML). Brand accent colour for table headers (`ShadingType.CLEAR`). Dual widths on all tables (`columnWidths` + cell `width`, both `WidthType.DXA`). Validate with `validate.py`. Convert to PDF via `soffice.py`. A4 for AU/UK, US Letter for US.

**9 minimum tables:** Product audit, R1 searches, user intake, R2 searches, colour system (Pantone+CMYK+HEX), typography (family+weights+rationale), R3 validation, component inventory, migration find-and-replace.

### CSS Syntax Highlighting

- `.c` — comments → `var(--text-subtle)`
- `.k` — keys/properties → `var(--sage-400)`
- `.s` — strings/values → `#C4943A`

### Nav Section Groups (20 sections)

1. **Overview**: Brand Identity, Brand Story, Positioning
2. **Visual Identity**: Logo System, Colour Palette, Typography, Visual Language
3. **Implementation**: Tailwind v4 Config, Component Patterns, Pipeline Stages
4. **AI Agent Guide**: Dashboard Principles, Layout System, Data Display, States & Motion, Anti-Patterns
5. **Systems**: Iconography, Animation System, Accessibility, Interactive Demos, Library Matrix

---

## Adaptive Questioning Rules

1. **Detailed brief upfront** → skip questions, confirm inferences, go to Phase 1
2. **"Just rebrand this"** → audit first, R1 scan, ask only direction + colour
3. **Pantone/hex provided** → anchor colours set, skip colour mood question
4. **Reference brand named** → research that brand in R1 before presenting options
5. **Max 3 widget questions per turn**

---

## UK/EU 2026 Compliance Defaults

- WCAG 2.2 AA (EU Accessibility Act), UK GDPR consent-first UI
- Dark + light mode both required, colour never sole information carrier
- Variable fonts, mobile-first, LCP < 2.5s, CLS < 0.1

---

## Quality Checklist

### Research Gates
- [ ] R1 completed: 5-8 searches, findings documented, questions tailored
- [ ] R2 completed: deep research + 5-7 searches, recommendations presented and confirmed
- [ ] R3 completed: 5-6 validation searches, trademark/font/competitor checks done

### Brand Identity
- [ ] Phase 0 brief confirmed by user before design work
- [ ] Brand voice Do/Don't with concrete examples
- [ ] Tagline benchmarked against R2 copywriting research
- [ ] Localisation correct for target region (spelling, date format, units)

### Visual System
- [ ] All colours have Pantone name + code, CMYK, HEX, RGB
- [ ] Colour choices justified by R2 colour psychology/trend research
- [ ] Pantone swatch cards in bento grid (featured primary spans 2 cols)
- [ ] 11-step scale strips for primary + neutral (22 total steps)
- [ ] All text/bg pairs pass WCAG 2.2 AA contrast
- [ ] Three font families defined — justified by R2 typography research
- [ ] SVG logomark in 4 variants
- [ ] Favicon package specified

### Implementation
- [ ] Tailwind @theme block complete and syntactically valid
- [ ] Visual SVG icon grid with 15-20 rendered icons
- [ ] 6 live animation demos with prefers-reduced-motion fallback
- [ ] Interactive demos: pipeline, glass cards, contrast checker, stats
- [ ] Dashboard anti-patterns: 15+ banned with alternatives
- [ ] Library/stack matrix with foundation + vertical tables
- [ ] All interactive elements have role="button", tabindex="0", aria-label
- [ ] Toast notification, IntersectionObserver nav, syntax-highlighted code blocks

### Delivery
- [ ] R3 validation complete (trademark, font, competitor drift, colour associations)
- [ ] Research insights included in delivery summary
- [ ] File self-contained HTML (<3000 lines, no external JS)
- [ ] Migration steps provided (if rebrand)
- [ ] Research & Decisions Report generated as DOCX (9 sections, all R1/R2/R3 tables)
- [ ] DOCX validated via validate.py
- [ ] PDF generated from DOCX via LibreOffice
- [ ] All outputs delivered via present_files (HTML guide + DOCX report + PDF report)
