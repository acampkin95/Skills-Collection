---
name: content-strategy
description: "Content strategy, SEO fundamentals, content governance, information hierarchy, content lifecycle management, and content planning for non-CLI agents. Use when planning content, optimizing for search, creating content calendars, managing content lifecycle, or establishing content governance."
version: "1.0.0"
metadata:
  category: content-planning
  scope: non-cli
---

# Content Strategy

Planning, creating, managing, and optimizing content for maximum impact and findability.

## Content Strategy Framework

### Core Pillars

```
CONTENT STRATEGY = SUBSTANCE + STRUCTURE + WORKFLOW + GOVERNANCE

SUBSTANCE:   What content do we create? For whom? Why?
STRUCTURE:   How is content organized, tagged, connected?
WORKFLOW:    How does content get created, reviewed, published?
GOVERNANCE:  Who decides? What are the standards? How is quality maintained?
```

### Content Audit

```
STEP 1: INVENTORY
├── URL, title, type, word count, author, date
├── Traffic data (views, unique, bounce rate)
├── Engagement (time on page, shares, conversions)
└── SEO data (rank, keywords, backlinks)

STEP 2: EVALUATE
├── Accuracy: Is it still correct?
├── Relevance: Does it serve current audience needs?
├── Quality: Does it meet our standards?
├── Performance: Does it get traffic/engagement?
└── Uniqueness: Does it duplicate other content?

STEP 3: ACTION
┌── KEEP: Accurate, performing well
├── UPDATE: Good topic, needs refresh
├── MERGE: Duplicates, consolidate
├── ARCHIVE: No longer relevant
└── CREATE: Identified gaps
```

## SEO Fundamentals

### On-Page SEO

```
TITLE TAG:
├── 50-60 characters (displays ~55)
├── Primary keyword near the start
├── Brand name at end: "Title | Brand"
└── Unique per page

META DESCRIPTION:
├── 150-160 characters
├── Include primary keyword
├── Include call-to-action
├── Compelling, not stuffed
└── Unique per page

HEADING STRUCTURE:
├── H1: One per page, includes primary keyword
├── H2: Section headings, natural keyword variations
├── H3: Subsections, supporting detail
└── Don't skip levels

URL:
├── Include primary keyword
├── Short and descriptive (3-5 words)
├── Lowercase, hyphens between words
├── No parameters or session IDs
└── Don't change URLs after publishing (use redirects if needed)

IMAGE OPTIMIZATION:
├── Descriptive file names (not IMG_1234.jpg)
├── Meaningful alt text (describe the image + context)
├── Compressed file size (<200KB for most images)
├── WebP format with fallbacks
└── Width/height attributes for CLS prevention
```

### Structured Data (Schema.org)

```
MOST VALUABLE SCHEMA TYPES:
├── Article / BlogPosting → Rich snippet with date, author
├── FAQ → Expandable FAQ in search results
├── HowTo → Step-by-step in search results
├── Product → Price, availability, reviews in results
├── BreadcrumbList → Breadcrumb trail in results
├── Organization → Knowledge panel
└── SearchAction → Sitelinks search box

IMPLEMENTATION:
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "datePublished": "2025-01-15",
  "dateModified": "2025-01-20",
  "author": { "@type": "Person", "name": "Author" },
  "publisher": { "@type": "Organization", "name": "Site" },
  "description": "Meta description here",
  "image": "https://example.com/image.jpg"
}
</script>
```

### Technical SEO Checklist

```
CRAWLABILITY:
├── robots.txt properly configured
├── XML sitemap submitted to search engines
├── No orphan pages (every page linked from somewhere)
├── Clean URL structure
├── Proper canonical tags
└── No duplicate content issues

PERFORMANCE:
├── Core Web Vitals passing (LCP, INP, CLS)
├── Mobile-friendly (responsive design)
├── HTTPS everywhere
├── Fast server response (TTFB < 800ms)
└── No render-blocking resources

INDEXATION:
├── Unique title and description per page
├── Proper heading hierarchy
├── Internal linking between related content
├── No broken links (check regularly)
├── 301 redirects for moved content
├── Custom 404 page
└── Pagination handled correctly (rel=prev/next or load more)
```

## Content Planning

### Content Calendar

```
WEEKLY TEMPLATE:
────────────────
| Day     | Channel   | Content Type  | Topic              | Status   |
|---------|-----------|---------------|--------------------| ---------|
| Monday  | Blog      | Tutorial      | How to use X       | Draft    |
| Tuesday | Newsletter| Curated       | Weekly digest      | Scheduled|
| Wed     | Social    | Tips thread   | 5 tips about Y     | Idea     |
| Thurs   | Blog      | Case study    | Customer story     | Research |
| Friday  | Social    | Engagement    | Poll/question      | Draft    |

CONTENT MIX (per month):
├── 40% Educational (tutorials, guides, how-tos)
├── 25% Thought leadership (opinion, analysis)
├── 20% Case studies / social proof
├── 10% Company news / updates
└── 5% Entertainment / community
```

### Content Types by Funnel Stage

```
AWARENESS (top of funnel):
├── Blog posts (educational)
├── Infographics
├── Social media content
├── Guest posts / PR
└── Videos / podcasts

CONSIDERATION (middle):
├── Comparison guides
├── Webinars
├── Case studies
├── Free tools / templates
└── Email courses

DECISION (bottom):
├── Product demos
├── Pricing pages
├── Testimonials / reviews
├── Free trials
└── ROI calculators

RETENTION:
├── Onboarding guides
├── Help documentation
├── Changelog / release notes
├── Community content
└── Advanced tutorials
```

## Content Governance

### Quality Standards

```
PUBLICATION CHECKLIST:
├── [ ] Title is compelling and includes keyword
├── [ ] Opening paragraph hooks the reader
├── [ ] Structure is scannable (headings, bullets, tables)
├── [ ] All claims have sources
├── [ ] Technical accuracy verified by subject matter expert
├── [ ] Grammar and spelling checked
├── [ ] Images have alt text
├── [ ] Internal links to related content
├── [ ] Meta title and description optimized
├── [ ] Mobile preview looks correct
└── [ ] Call-to-action is clear

REVIEW PROCESS:
├── Self-review (author checks against standards)
├── Peer review (colleague checks for clarity)
├── Expert review (SME checks accuracy)
├── Editorial review (style, brand voice)
└── Final approval → Publish
```

### Content Lifecycle

```
CREATE → PUBLISH → PROMOTE → MEASURE → UPDATE → ARCHIVE

MEASUREMENT METRICS:
├── Traffic: Page views, unique visitors
├── Engagement: Time on page, scroll depth, shares
├── Conversion: Click-through, form fills, sign-ups
├── SEO: Rankings, backlinks, click-through rate
└── Quality: Bounce rate, return visitors

REFRESH CADENCE:
├── High-traffic pages: Review quarterly
├── Standard pages: Review every 6 months
├── Evergreen content: Annual review
├── Time-sensitive: Update as events change
└── All content: Full audit annually
```


## When to Use

- Planning content creation, governance, and lifecycle
- Applying SEO fundamentals to content decisions
- Creating editorial calendars and content roadmaps
- Auditing existing content for quality and coverage gaps
- Defining content governance policies and review workflows

## Limitations

- SEO best practices evolve with search engine algorithm changes
- Content strategy requires organizational buy-in to execute
- Governance policies need enforcement mechanisms to be effective
- Content performance data requires analytics tooling

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [information-architecture](../information-architecture/SKILL.md) | IA provides the structural foundation for content strategy |
| [technical-writing](../technical-writing/SKILL.md) | Content creation follows technical writing standards |
| [reporting](../reporting/SKILL.md) | Content audits and performance reports use reporting templates |
| [structured-thinking](../structured-thinking/SKILL.md) | Content planning applies decision frameworks |
