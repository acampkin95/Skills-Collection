---
name: information-architecture
description: "Information architecture, content organization, navigation design, findability, taxonomy design, and content modeling for non-CLI agents. Use when organizing content, designing navigation, creating taxonomies, structuring information, or improving content findability."
version: "1.0.0"
metadata:
  category: reporting-documentation
  scope: non-cli
---

# Information Architecture

Organizing, structuring, and labeling content for findability and usability.

## Core IA Principles

```
1. ORGANIZATION: Group content logically
2. LABELING: Name things as users expect
3. NAVIGATION: Provide clear paths to content
4. SEARCH: Help users find what they need
5. HIERARCHY: Structure from broad to specific
```

## Content Organization Patterns

### Common Structures

```
HIERARCHICAL (most common):
├── Home
│   ├── Products
│   │   ├── Category A
│   │   └── Category B
│   ├── Solutions
│   │   ├── By Industry
│   │   └── By Use Case
│   └── Resources
│       ├── Documentation
│       ├── Blog
│       └── Support

HUB-AND-SPOKE (task-based):
├── Dashboard (hub)
│   ├── Task A (spoke)
│   ├── Task B (spoke)
│   └── Task C (spoke)

FLAT (small sites):
├── Home
├── About
├── Services
├── Contact
└── Blog

DAISY-CHAIN (linear):
├── Step 1 → Step 2 → Step 3 → Step 4
(wizards, onboarding, checkout)
```

### Card Sorting for Organization

```
OPEN SORT:               CLOSED SORT:
Users create groups      Users sort into your groups
and name them            (validates existing IA)
(generates new IA)

PROCESS:
1. List all content items (50-100 cards)
2. Recruit representative users (15-20)
3. Users group items logically
4. Analyze patterns across participants
5. Build IA from consensus

ANALYSIS:
├── Items frequently grouped together → same section
├── Items rarely grouped together → separate sections
├── Common group names → section labels
└── Outlier items → may need cross-linking
```

### Content Modeling

```
CONTENT TYPE MODEL:
───────────────────
Type: Article
├── Title (text, required)
├── Author (reference → Person)
├── Date (datetime)
├── Category (reference → Category)
├── Tags (reference[] → Tag)
├── Body (rich text)
├── Featured image (reference → Image)
├── Related articles (reference[] → Article)
└── SEO: description, keywords

RELATIONSHIPS:
Article ──belongs to──► Category
Article ──written by──► Person
Article ──tagged with──► Tag[]
Article ──related to──► Article[]
Category ──has many──► Article[]
Person ──writes──► Article[]
Tag ──applied to──► Article[]
```

## Navigation Design

### Navigation Types

| Type | Location | Use For |
|------|----------|---------|
| **Global nav** | Top of every page | Primary site sections |
| **Local nav** | Sidebar/left | Section sub-pages |
| **Breadcrumbs** | Top of content | Location in hierarchy |
| **Footer nav** | Bottom | Utility links, legal |
| **Contextual** | Within content | Related content |
| **In-page** | TOC, jump links | Long page sections |

### Navigation Best Practices

```
GLOBAL NAVIGATION:
├── 5-7 items maximum (Miller's Law: 7±2)
├── Use clear, familiar labels
├── Highlight current section
├── Include search access
├── Mobile: hamburger menu acceptable
└── Sticky on scroll for long pages

BREADCRUMBS:
├── Show full path: Home > Section > Page
├── Current page: not linked, just text
├── Clickable ancestors
├── Separator: > or / (consistent)
└── Hide on mobile if space constrained

MOBILE NAVIGATION:
├── Bottom tab bar (3-5 primary destinations)
├── Hamburger for secondary items
├── Swipe for back navigation
├── Large touch targets (48x48dp)
└── Visual feedback on tap
```

### URL Structure

```
GOOD URLs:
├── /products/category/item-name
├── /blog/2025/how-to-do-thing
├── /docs/api/authentication
├── Readable, predictable, hackable
├── Lowercase, hyphens not underscores
└── No parameters for content pages

BAD URLs:
├── /p?id=12345&cat=3
├── /page.asp?cid=7
├── /products/ITEM_NAME
├── /blog/2025/01/15/23/59/a8x9k2
└── Unreadable, unpredictable
```

## Taxonomy & Tagging

### Taxonomy Design

```
TAXONOMY TYPES:
├── Flat: No hierarchy (tags, keywords)
├── Hierarchical: Parent-child (categories)
├── Polyhierarchical: Multiple parents (facets)
└── Network: Related terms (see also)

DESIGN RULES:
├── Mutually exclusive categories (if hierarchical)
├── Collectively exhaustive (cover all content)
├── 3-12 categories per level
├── Maximum 3 levels deep
├── Clear, user-facing labels
└── Consistent granularity (don't mix broad and narrow)
```

### Tagging Strategy

```
CONTROLLED VOCABULARY:
├── Pre-defined list of tags
├── Synonyms mapped (car → automobile → vehicle)
├── Prevents fragmentation
└── Better for search and filtering

FOLKSONOMY (free tagging):
├── Users create their own tags
├── More flexible
├── Risk of duplication/synonyms
└── Works for user-generated content

HYBRID (recommended):
├── Controlled categories (broad organization)
├── Free tags within categories (granular findability)
├── Periodic tag consolidation (merge synonyms)
└── Suggested tags from existing vocabulary
```

## Findability

### Search Design

```
SEARCH UX PATTERNS:
├── Prominent search bar (top-right or top-center)
├── Placeholder text: "Search for..."
├── Auto-suggest after 2-3 characters
├── Recent searches available
├── Clear results with highlighted matches
├── Faceted filters on results page
├── "No results" with helpful suggestions
└── Search scoped to current section when appropriate

RESULTS PAGE:
├── Result count: "Showing 1-20 of 342 results"
├── Sort options: Relevance, Date, Popularity
├── Filter facets: Type, Category, Date range
├── Snippet with highlighted search terms
├── Clear "x" to reset search
└── Pagination or infinite scroll (choose one)
```

### Cross-Linking Strategy

```
LINK TYPES:
├── Contextual: Related content links within body text
├── See also: Manually curated related items
├── Tag-based: "More like this" sections
├── Series: Previous/Next in sequence
├── Breadcrumb: Upward navigation
└── Sitemap: Complete overview

RULES:
├── Link don't duplicate (link to source, don't copy)
├── Anchor text should describe destination
├── Internal links help SEO and findability
├── 3-5 related links per article
├── Check links periodically (no 404s)
└── Open external links in new tab (controversial — be consistent)
```

## Content Audit

```
AUDIT PROCESS:
──────────────
1. INVENTORY
   └── List every content item (URL, title, type, date)

2. EVALUATE
   └── Per item: accuracy, relevance, quality, traffic, freshness

3. ANALYZE
   └── Gaps: what's missing?
   └── Overlap: what's duplicated?
   └── Orphans: what's unlinked?
   └── Stale: what's outdated?

4. ACTION
   ┌── Keep: Accurate and useful
   ├── Update: Useful but outdated
   ├── Merge: Duplicated content
   ├── Archive: No longer relevant
   └── Create: Identified gaps

5. GOVERNANCE
   └── Content calendar for regular reviews
   └── Ownership assignment per section
   └── Review frequency: quarterly minimum
```

## User Journey Mapping

```
JOURNEY MAPPING FOR IA:
────────────────────────
1. IDENTIFY USER GOALS
   └── What tasks do users come to accomplish?
   └── Rank by frequency and importance

2. MAP CURRENT PATHS
   └── Entry points (search, direct, referral, nav)
   └── Click paths to goal completion
   └── Drop-off points (where users leave)
   └── Dead ends (pages with no forward path)

3. IDENTIFY FRICTION
   └── Too many clicks to reach goal (>3 for common tasks)
   └── Confusing labels (user language ≠ site language)
   └── Missing wayfinding (no breadcrumbs, unclear location)
   └── Content gaps (user needs info that doesn't exist)

4. OPTIMIZE PATHS
   └── Reduce steps to high-value destinations
   └── Surface popular content in navigation
   └── Add cross-links at decision points
   └── Create landing pages for common journeys
```

### Progressive Disclosure Strategy

```
PRINCIPLE: Show only what's needed at each level of interest

LEVEL 1 — AWARENESS (homepage, category pages)
├── Headline + brief description
├── Clear call-to-action
├── 1-2 key benefits
└── Link to learn more

LEVEL 2 — UNDERSTANDING (listing pages, overview pages)
├── Expanded description
├── Key features/specs summary
├── Comparison highlights
├── Social proof (ratings, testimonials)
└── Links to details

LEVEL 3 — DECISION (detail pages, documentation)
├── Full specifications
├── Pricing/options
├── In-depth documentation
├── Case studies
└── Action buttons (buy, sign up, download)

LEVEL 4 — DEPTH (technical docs, API reference, tutorials)
├── Complete reference material
├── Advanced configurations
├── Troubleshooting guides
└── Community/discussion links
```


## When to Use

- Organizing content hierarchies and navigation structures
- Designing taxonomies, tagging systems, and categorization schemes
- Auditing existing content for structural issues
- Planning site maps and URL structures
- Improving content findability and discoverability

## Limitations

- IA decisions require user research to validate assumptions
- Organizational politics can constrain IA choices
- Taxonomy maintenance is ongoing — content evolves
- Large-scale IA changes require migration planning

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [content-strategy](../content-strategy/SKILL.md) | IA is a core component of content strategy |
| [technical-writing](../technical-writing/SKILL.md) | Documentation structure follows IA principles |
| [design-principles](../design-principles/SKILL.md) | Hierarchy and grouping apply Gestalt principles |
| [responsive-design](../responsive-design/SKILL.md) | Navigation IA must adapt to mobile viewports |
