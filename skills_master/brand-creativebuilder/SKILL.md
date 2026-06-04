---
name: brand-creativebuilder
description: End-to-end brand identity builder with Pantone colours, SVG logos, HTML guidelines, Tailwind v4 config, and Recraft/ElevenLabs prompt libraries.
version: 2.0.0
reviewed: "2026-06-04"
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

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.