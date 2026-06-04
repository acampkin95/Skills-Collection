# OUI — Open UI Framework Skills

> **27 comprehensive skills** across **8 categories** for non-CLI agents covering search, research, web interaction, structured thinking, reporting, data skills, AI interaction, content planning, and design.

## Architecture

```
.maintenance/OUI/
├── README.md                    ← You are here
│
├── SEARCH & RESEARCH ────────────────────────────────────
│   ├── web-research/            Systematic web research methodology
│   ├── source-evaluation/       Credibility assessment & fact-checking
│   └── deep-research/           Long-form systematic research
│
├── WEB INTERACTION ──────────────────────────────────────
│   ├── web-fetching/            HTTP patterns, auth, rate limiting
│   ├── web-crawling/            Ethical scraping & content extraction
│   ├── content-extraction/      Readability, boilerplate removal, normalization
│   ├── api-patterns/            REST/GraphQL, pagination, error handling
│   └── firecrawl-web-crawling/  Firecrawl API: scrape, crawl, extract, map, agent
│
├── THINKING & REASONING ─────────────────────────────────
│   ├── structured-thinking/     MECE, first principles, decision matrices
│   ├── data-synthesis/          Multi-source combination, evidence grading
│   ├── critical-thinking/       Fallacies, biases, Socratic questioning, Bayesian reasoning
│   └── summarization/           Extractive/abstractive, progressive, chain-of-density
│
├── REPORTING & DOCUMENTATION ────────────────────────────
│   ├── technical-writing/       Diátaxis framework, writing standards
│   ├── reporting/               Report templates, data presentation
│   └── information-architecture/ Content organization, navigation, findability
│
├── DATA SKILLS ──────────────────────────────────────────
│   ├── data-visualization/      Chart selection, color palettes, perception principles
│   └── regex-text-processing/   Regex syntax, extraction recipes, text transformation
│
├── AI INTERACTION ───────────────────────────────────────
│   └── prompt-engineering/      Prompt architecture, few-shot, CoT, tool use, caching
│
├── CONTENT & PLANNING ───────────────────────────────────
│   ├── content-strategy/        SEO, content planning, governance
│   └── tapestry/                Content extraction & action planning
│
├── DESIGN & VISUAL ──────────────────────────────────────
│   ├── design-principles/       UI/UX fundamentals, Gestalt, hierarchy
│   ├── visual-design/           Color (OKLCH), typography, spacing, layout
│   ├── accessibility-knowledge/ WCAG 2.2, ARIA, inclusive design
│   ├── modern-web-standards/    HTML5, CSS4, Web APIs, progressive enhancement
│   ├── web-performance/         Core Web Vitals, optimization
│   ├── responsive-design/       Mobile-first, breakpoints, container queries
│   └── interaction-patterns/    Micro-interactions, state management, transitions
```

## Skill Matrix

### By Category

| Category | Skills | Tier |
|----------|--------|------|
| **Search & Research** | web-research, source-evaluation, deep-research | Core |
| **Web Interaction** | web-fetching, web-crawling, content-extraction, api-patterns, firecrawl-web-crawling | Core |
| **Thinking & Reasoning** | structured-thinking, data-synthesis, critical-thinking, summarization | Core |
| **Reporting & Documentation** | technical-writing, reporting, information-architecture | Core |
| **Data Skills** | data-visualization, regex-text-processing | Core |
| **AI Interaction** | prompt-engineering | Core |
| **Content & Planning** | content-strategy, tapestry | Core |
| **Design & Visual** | design-principles, visual-design, accessibility-knowledge, modern-web-standards, web-performance, responsive-design, interaction-patterns | Core |

### By Use Case

| I need to... | Skills to use |
|-------------|---------------|
| Research a topic on the web | `web-research` → `source-evaluation` → `deep-research` |
| Evaluate claims and arguments | `critical-thinking` → `source-evaluation` → `data-synthesis` |
| Fetch data from an API | `web-fetching` → `api-patterns` |
| Crawl a website for content | `web-crawling` → `content-extraction` |
| Summarize a document or article | `summarization` → `content-extraction` |
| Extract insights from a video or URL | `tapestry` → `content-extraction` → `summarization` |
| Create a visual data presentation | `data-visualization` → `reporting` |
| Design effective prompts | `prompt-engineering` → `structured-thinking` |
| Write a report from research findings | `data-synthesis` → `summarization` → `reporting` |
| Analyze a complex problem | `structured-thinking` → `critical-thinking` → `data-synthesis` |
| Understand modern web capabilities | `modern-web-standards` → `web-performance` |
| Plan content strategy | `content-strategy` → `information-architecture` |
| Design responsive layouts | `responsive-design` → `interaction-patterns` |
| Verify information quality | `source-evaluation` → `critical-thinking` → `data-synthesis` |
| Create accessible content | `accessibility-knowledge` → `design-principles` |
| Extract and transform text data | `regex-text-processing` → `content-extraction` |
| Crawl sites with Firecrawl API | `firecrawl-web-crawling` → `content-extraction` → `deep-research` |
| Build RAG knowledge base from web | `firecrawl-web-crawling` → `web-crawling` → `data-synthesis` |
| Synthesize multiple sources | `summarization` → `data-synthesis` → `critical-thinking` |

## Skill Cross-References

```
web-research
  └── Uses: source-evaluation, data-synthesis
  └── Produces: input for reporting, summarization

source-evaluation
  └── Used by: web-research, deep-research, data-synthesis, critical-thinking

deep-research
  └── Uses: web-research, source-evaluation, data-synthesis, critical-thinking
  └── Produces: input for reporting, summarization

web-fetching
  └── Used by: web-crawling, api-patterns
  └── Complements: content-extraction

web-crawling
  └── Uses: web-fetching, content-extraction
  └── Informs: data-synthesis

content-extraction
  └── Used by: web-crawling, web-research, tapestry, summarization
  └── Produces: input for data-synthesis

api-patterns
  └── Uses: web-fetching
  └── Complements: web-crawling (API vs HTML extraction)

structured-thinking
  └── Used by: all analytical skills
  └── Applied in: data-synthesis, reporting, deep-research, critical-thinking

data-synthesis
  └── Uses: structured-thinking, source-evaluation, critical-thinking
  └── Produces: input for reporting, data-visualization

critical-thinking
  └── Uses: structured-thinking, source-evaluation
  └── Used by: deep-research, data-synthesis, web-research
  └── Evaluates: all claims and arguments

summarization
  └── Uses: content-extraction, critical-thinking
  └── Used by: reporting, deep-research, tapestry
  └── Produces: compressed outputs at multiple levels

prompt-engineering
  └── Uses: structured-thinking, web-research
  └── Complements: all skills (improves interaction quality)

tapestry
  └── Uses: content-extraction, summarization, web-crawling
  └── Produces: action plans, implementation roadmaps

data-visualization
  └── Uses: visual-design, accessibility-knowledge
  └── Consumes: output from data-synthesis

regex-text-processing
  └── Used by: content-extraction, data-visualization, summarization
  └── Supports: text cleaning and normalization

design-principles
  └── Applies to: visual-design, accessibility-knowledge, interaction-patterns
  └── Informs: responsive-design, data-visualization

visual-design
  └── Uses: design-principles
  └── Pairs with: modern-web-standards, data-visualization

accessibility-knowledge
  └── Applies across: design-principles, visual-design, interaction-patterns, data-visualization
  └── Validates: modern-web-standards implementation

modern-web-standards
  └── Implements: visual-design, responsive-design
  └── Enables: web-performance, interaction-patterns

web-performance
  └── Measures: modern-web-standards, visual-design
  └── Informs: responsive-design decisions

technical-writing
  └── Uses: information-architecture
  └── Produces: input for reporting, summarization

reporting
  └── Uses: data-synthesis, technical-writing, summarization
  └── Consumes: output from all research skills

information-architecture
  └── Guides: content-strategy, technical-writing
  └── Organizes: reporting structure

content-strategy
  └── Uses: information-architecture, technical-writing
  └── Informs: SEO and content planning

responsive-design
  └── Uses: design-principles, visual-design
  └── Implements: modern-web-standards

interaction-patterns
  └── Uses: design-principles, accessibility-knowledge
  └── Implements: modern-web-standards (animations/transitions)
```

## Usage Guide

### Loading a Skill

Each skill is a self-contained SKILL.md file following the Agent Skills specification:

```
Skill location: .maintenance/OUI/<skill-name>/SKILL.md
Load: Read the SKILL.md file before working on related tasks
Format: YAML frontmatter + Markdown body
```

### Combining Skills

Skills are designed to compose. Typical workflows combine 2-4 skills:

**Research & Evaluate Workflow:**
1. `web-research` — Plan and execute searches
2. `source-evaluation` — Assess credibility of findings
3. `critical-thinking` — Evaluate arguments and detect fallacies
4. `data-synthesis` — Combine and grade evidence
5. `reporting` — Structure and deliver findings

**Content Extraction Workflow:**
1. `tapestry` — Detect source type and extract content
2. `content-extraction` — Apply extraction techniques
3. `summarization` — Compress to appropriate level
4. `reporting` — Deliver in requested format

**Data Analysis Workflow:**
1. `regex-text-processing` — Clean and normalize raw data
2. `data-synthesis` — Combine multiple data sources
3. `critical-thinking` — Evaluate claims in the data
4. `data-visualization` — Select appropriate chart types
5. `reporting` — Present findings

**AI System Design Workflow:**
1. `prompt-engineering` — Design prompts and tool interfaces
2. `structured-thinking` — Decompose complex tasks
3. `source-evaluation` — Validate training data quality
4. `technical-writing` — Document the system

**Design Review Workflow:**
1. `design-principles` — Apply fundamental principles
2. `accessibility-knowledge` — Check WCAG compliance
3. `visual-design` — Evaluate color, typography, layout
4. `web-performance` — Check performance implications

**Content Creation Workflow:**
1. `information-architecture` — Structure content
2. `technical-writing` — Apply writing standards
3. `content-strategy` — Optimize for audience and SEO
4. `responsive-design` — Ensure multi-device presentation

### Skill Depth Levels

| Level | Description | Typical Size |
|-------|-------------|-------------|
| **Overview** | Quick reference, tables, decision trees | 50-100 lines |
| **Standard** | Full patterns, examples, checklists | 150-270 lines |
| **Deep** | Comprehensive reference with all edge cases | 270-410 lines |

All OUI skills are at the **Standard** to **Deep** level (265–405 lines each).

Every skill includes three standardized tail sections:
- **When to Use** — Trigger conditions for activating the skill
- **Limitations** — Known boundaries and caveats
- **Cross-References** — Links to related OUI skills with relationship descriptions

## Maintenance

- **Review cycle**: Quarterly review of all skills
- **Update triggers**: New web standards, WCAG updates, CSS specification changes, AI model updates
- **Quality check**: Each skill must pass the Agent Skills specification validator
- **Dependencies**: Skills reference each other via cross-references section
