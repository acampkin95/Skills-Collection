---
name: web-crawling
description: "Ethical web crawling, scraping methodology, content extraction, anti-bot handling, robots.txt compliance, and structured data extraction for non-CLI agents. Use when crawling websites, extracting structured data from web pages, handling anti-bot measures, respecting robots.txt, or performing systematic web content collection."
version: "1.0.0"
metadata:
  category: web-interaction
  scope: non-cli
---

# Web Crawling & Scraping

Ethical and effective web content extraction. Covers crawling strategy, content parsing, anti-bot handling, and responsible data collection practices.

## Ethical Crawling Principles

### The Crawler's Code

1. **Respect robots.txt** - Always check before crawling
2. **Honor rate limits** - Default to 1 request per 2-3 seconds minimum
3. **Identify yourself** - Use meaningful User-Agent strings
4. **Check ToS** - Some sites prohibit automated access
5. **Minimize load** - Only request what you need
6. **Cache aggressively** - Never re-request the same page
7. **Handle errors gracefully** - Back off on errors, don't hammer
8. **Don't circumvent** - If blocked, respect the block

### robots.txt Interpretation

```
User-agent: *              # Applies to all crawlers
Disallow: /admin/          # Don't crawl /admin/
Disallow: /private/        # Don't crawl /private/
Allow: /public/            # Explicitly allow /public/
Crawl-delay: 5             # Wait 5 seconds between requests

User-agent: GoogleBot      # Specific to Google
Disallow: /tmp/            # Only Google can't crawl /tmp/
```

**Rules:**
- `Disallow` with no path = allow everything
- `Disallow: /` = block everything
- Most specific rule wins
- `Crawl-delay` is advisory (respect it)
- No robots.txt = assume everything allowed (but be conservative)

## Crawling Strategy

### Breadth-First vs Depth-First

```
BREADTH-FIRST (recommended for most cases):
Page 1 → extract all links
Page 2 → extract all links
Page 3 → extract all links
...then go deeper

Good for: Site mapping, comprehensive coverage

DEPTH-FIRST:
Page 1 → follow first link → follow first link → ...
...then backtrack

Good for: Finding specific deep content, following a topic trail
```

### URL Queue Management

```
URL QUEUE
─────────
┌────────────────────────────────────────────┐
│ SEED URLS (starting points)                │
│   https://example.com/page1                │
│   https://example.com/page2                │
├────────────────────────────────────────────┤
│ DISCOVERED URLs (found but not yet visited) │
│   https://example.com/page3                │
│   https://example.com/page4                │
├────────────────────────────────────────────┤
│ VISITED URLs (already processed)           │
│   https://example.com/page1 ✓              │
│   https://example.com/page2 ✓              │
├────────────────────────────────────────────┤
│ RULES                                      │
│   - Stay within domain (or follow scope)   │
│   - Skip file downloads (.pdf, .zip, etc)  │
│   - Skip media files (.jpg, .mp4, etc)     │
│   - Normalize URLs (remove fragments, etc) │
│   - Respect robots.txt                     │
│   - Enforce crawl delay                    │
└────────────────────────────────────────────┘
```

### URL Normalization

```
These are the same URL:
  https://example.com/page
  https://example.com/page/
  https://example.com/page?utm_source=twitter
  https://example.com/page#section1
  https://www.example.com/page
  http://example.com/page

Normalize to: https://example.com/page

Rules:
1. Lowercase hostname
2. Remove www. (if canonical)
3. Remove tracking params (utm_*, fbclid, etc.)
4. Remove fragment (#section)
5. Remove trailing slash (or add consistently)
6. Use HTTPS as default
7. Remove default ports (:80, :443)
```

## Content Extraction

### Readability Extraction

Extract main content from a web page (article body, not navigation/ads):

```
CONTENT HIERARCHY (what to extract)
────────────────────────────────────
1. TITLE        → <h1>, <title>, og:title
2. AUTHOR       → meta author, rel="author", byline
3. DATE         → time[datetime], meta date, published_time
4. BODY         → <article>, <main>, [role="main"]
5. IMAGES       → <img> with meaningful alt text
6. LINKS        → <a> with href in body content
7. METADATA     → structured data (JSON-LD, microdata)

SKIP:
- Navigation menus
- Sidebars
- Footer content
- Ad blocks
- Cookie notices
- Comment sections (unless specifically needed)
```

### HTML Content Selection Patterns

| Target | Selector Strategy | Notes |
|--------|-------------------|-------|
| Article | `article`, `[role="article"]`, `.post-content` | Most reliable for blog posts |
| Main content | `main`, `[role="main"]`, `#content` | Standard HTML5 |
| Product info | `.product-details`, `[itemprop]` | E-commerce sites |
| List items | `.list-item`, `li` in content area | Varies by site |
| Tables | `table` with `thead` + `tbody` | Structured data |
| Code blocks | `pre > code`, `.highlight` | Technical content |

### Structured Data Extraction

```
JSON-LD (most common structured data format):
─────────────────────────────────────────────
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": { "@type": "Person", "name": "Author" },
  "datePublished": "2025-01-15",
  "image": "url-to-image.jpg"
}
</script>

Check <script type="application/ld+json"> for structured data
Common types: Article, Product, Recipe, Event, FAQ, HowTo
```

## Anti-Bot Handling

### Common Anti-Bot Measures

| Measure | Detection | Ethical Response |
|---------|-----------|-----------------|
| **Rate limiting** | 429 responses | Slow down, honor limits |
| **CAPTCHA** | Cannot solve | Stop, flag for manual review |
| **JavaScript rendering** | Empty content without JS | Use rendered content source |
| **IP blocking** | 403 responses | Respect the block |
| **Browser fingerprinting** | Blocked after few requests | Reduce frequency |
| **Login required** | Redirect to login | Check if API available instead |

### When to Stop Crawling

```
STOP IF:
├── 429 Too Many Requests (after backoff)
├── 403 Forbidden (explicitly denied)
├── CAPTCHA presented
├── robots.txt disallows the path
├── Terms of Service prohibit crawling
├── You've collected sufficient data
├── Error rate exceeds 50%
└── You've hit a legal or ethical boundary
```

## Extraction Patterns by Content Type

### News Articles
```
Extract: title, author, date, body, source
Skip: related articles, comments, ads
Format: markdown with metadata header
```

### Product Pages
```
Extract: name, price, description, specs, reviews, images
Skip: recommendations, ads, newsletter popups
Format: structured object (JSON)
```

### Documentation
```
Extract: headings, body, code blocks, navigation structure
Skip: search bars, theme toggles, footer
Format: markdown preserving heading hierarchy
```

### API Documentation
```
Extract: endpoints, methods, parameters, responses, examples
Skip: marketing content, navigation
Format: structured reference (JSON/YAML)
```

### Blog Index Pages
```
Extract: post titles, URLs, dates, excerpts
Skip: pagination controls, sidebar
Format: list of objects with URLs for detail extraction
```

## Data Quality Assurance

### Extraction Validation

| Check | Method |
|-------|--------|
| **Completeness** | All expected fields present? |
| **Freshness** | Date within expected range? |
| **Accuracy** | Spot-check against source |
| **Deduplication** | URL/content hash comparison |
| **Encoding** | UTF-8, no mojibake |
| **HTML artifacts** | No stray tags, entities decoded |

### Common Extraction Errors

```
PROBLEM                    → FIX
─────────────────────────────────────────
HTML entities in text       → Decode &amp; &lt; etc.
JavaScript-rendered content → Use rendered source, not raw HTML
Truncated content           → Check for pagination or "read more"
Wrong encoding              → Detect from Content-Type header
Duplicate content           → Normalize URLs before dedup
Missing metadata            → Fall back to meta tags, og: tags
Inconsistent dates          → Parse with multiple format patterns
Relative URLs               → Resolve against base URL
```

## Firecrawl Integration Patterns

### When to Use Firecrawl vs Manual Crawling

```
USE FIRECRAWL WHEN:
├── Target site has JavaScript-rendered content (SPAs, React/Vue apps)
├── Need structured data extraction with schema validation
├── Building RAG pipelines or knowledge bases from web content
├── Site has anti-bot protections that block simple HTTP requests
├── Need to crawl 50+ pages with consistent extraction quality
├── Want async crawling with status polling for large sites
└── Integrating with Open WebUI or MCP-based LLM workflows

USE MANUAL CRAWLING WHEN:
├── Simple static HTML sites with no JavaScript requirements
├── Only need a handful of pages (1-5)
├── Have direct API access (prefer APIs over crawling)
├── Need fine-grained control over request timing and headers
└── Operating in air-gapped or no-external-service environments
```

### Firecrawl-Enhanced Crawling Workflow

```
1. RECONNAISSANCE
   → /map to discover URLs and estimate scope
   → Identify content types, depth, and relevant paths

2. PLANNING
   → Set includePaths/excludePaths based on research scope
   → Determine limit and maxDepth for crawl budget
   → Choose output format (markdown for LLM, HTML for archiving)

3. EXECUTION
   → /crawl with scoped parameters
   → Monitor via /crawl/status/{id} for progress
   → Adjust excludePaths if discovering irrelevant content

4. EXTRACTION
   → /extract with schema for structured data from crawled pages
   → /scrape with actions for dynamic content requiring interaction

5. VALIDATION
   → Cross-check extracted content against source pages
   → Score extraction quality per page
   → Flag pages with low content yield for manual review
```

### Dynamic Content Handling

```
JAVASCRIPT-HEAVY SITES:
├── Use /scrape with actions for interactive pages
│   → Click cookie banners: { "type": "click", "selector": ".accept" }
│   → Wait for content: { "type": "wait", "milliseconds": 2000 }
│   → Scroll for lazy-loaded content: { "type": "scroll", "direction": "down" }
├── Use waitFor parameter for pages needing render time
├── Use includeTags to target specific rendered sections
└── For infinite scroll: /scrape with scroll actions, then extract

ANTI-BOT SITES:
├── Firecrawl handles Cloudflare, CAPTCHA challenges server-side
├── Use /scrape or /crawl directly — proxy rotation is built-in
├── No need for manual user-agent rotation or proxy management
└── If a page fails, retry with increased timeout parameter
```

## When to Use

- Systematically visiting multiple pages on a website
- Extracting structured data across multiple URLs
- Building site maps or content inventories
- Monitoring websites for changes
- Scraping directories, listings, or paginated content

## Limitations

- Must respect robots.txt, crawl delays, and terms of service
- JavaScript-heavy sites may not render without browser automation
- Anti-bot protections (CAPTCHAs, Cloudflare) may block requests
- Large-scale crawls can be resource-intensive and slow

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-fetching](../web-fetching/SKILL.md) | Each crawl step involves fetching individual pages |
| [content-extraction](../content-extraction/SKILL.md) | Extract structured data from crawled pages |
| [source-evaluation](../source-evaluation/SKILL.md) | Evaluate crawled content for quality and relevance |
| [crawl4ai](/home/alex/.claude/skills/crawl4ai/SKILL.md) | Specialized async web scraping with JavaScript rendering |
| [api-patterns](../api-patterns/SKILL.md) | Many sites offer APIs as alternatives to crawling |
| [firecrawl-web-crawling](../firecrawl-web-crawling/SKILL.md) | Production-grade crawling for JS-heavy sites and structured extraction |
