---
name: content-extraction
description: "Content readability algorithms, boilerplate removal, structured data extraction, metadata harvesting, and content normalization for non-CLI agents. Use when extracting clean text from web pages, removing boilerplate content, harvesting metadata, converting HTML to markdown, or normalizing extracted content."
version: "1.0.0"
metadata:
  category: web-interaction
  scope: non-cli
---

# Content Extraction & Normalization

Techniques for extracting clean, structured content from raw web sources. Covers readability algorithms, metadata extraction, format conversion, and content normalization.

## Content Extraction Pipeline

```
RAW HTML
   │
   ▼
┌──────────────────┐
│ 1. FETCH         │ Retrieve raw content
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. DETECT TYPE   │ HTML? JSON? XML? RSS? PDF?
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. PARSE         │ Build DOM / parse structure
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. EXTRACT META  │ Title, author, date, description
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. REMOVE NOISE  │ Strip boilerplate, ads, navigation
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. EXTRACT BODY  │ Get main content
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 7. NORMALIZE     │ Clean whitespace, fix encoding, convert
└────────┬─────────┘
         │
         ▼
CLEAN CONTENT + METADATA
```

## Metadata Extraction

### Primary Metadata Sources (in priority order)

```yaml
Title:
  1. <meta property="og:title">
  2. <meta name="twitter:title">
  3. <title> (clean suffixes like " - Site Name")
  4. <h1> (first one in content area)
  5. JSON-LD headline property

Description:
  1. <meta property="og:description">
  2. <meta name="description">
  3. <meta name="twitter:description">
  4. First paragraph of body content (truncated)

Author:
  1. <meta name="author">
  2. JSON-LD author.name
  3. rel="author" link
  4. [class*="author"] element
  5. Byline patterns in text ("By Author Name")

Date:
  1. JSON-LD datePublished
  2. <meta property="article:published_time">
  3. <time datetime="...">
  4. <meta name="date">
  5. Date patterns in text (less reliable)

Image:
  1. <meta property="og:image">
  2. <meta name="twitter:image">
  3. JSON-LD image
  4. First <img> in content area
```

### Structured Data (JSON-LD)

```
LOCATE: <script type="application/ld+json"> tags

COMMON SCHEMA TYPES:
├── Article / NewsArticle / BlogPosting
├── Product
├── Recipe
├── Event
├── FAQ
├── HowTo
├── Person
├── Organization
├── BreadcrumbList
└── WebPage

EXTRACT: Parse JSON, flatten nested structures
VALIDATE: Check @type, required properties
```

## Boilerplate Removal

### Elements to Remove

```
ALWAYS REMOVE:
├── <nav> and [role="navigation"]
├── <footer> and [role="contentinfo"]
├── <header> (site header, not article header)
├── <aside> and [role="complementary"]
├── [role="banner"] (ad banners)
├── Elements with ad-related classes/ids:
│   .ad, .ads, .advertisement, #sidebar
│   .social-share, .share-buttons
│   .newsletter, .subscribe
│   .related-posts, .recommendations
│   .cookie-notice, .cookie-banner
│   .popup, .modal, .overlay
│   .comments-section
└── <script>, <style>, <noscript> tags
```

### Content Scoring Algorithm

Score each text block to determine if it's content or noise:

```
POSITIVE SIGNALS (content):
├── Inside <article> or [role="article"]
├── High text-to-HTML ratio
├── Contains paragraph tags (<p>)
├── Long text blocks (>100 chars)
├── Has heading siblings (<h2>, <h3>)
└── Contains links to related content

NEGATIVE SIGNALS (boilerplate):
├── Inside <nav>, <footer>, <aside>
├── Low text-to-HTML ratio
├── Contains many inline links
├── Short text blocks (<50 chars)
├── Repeated across multiple pages
└── Contains form elements

SCORING:
  Score > threshold → Keep as content
  Score ≤ threshold → Discard as boilerplate
```

## Format Conversion

### HTML to Markdown

```
CONVERSION RULES:
─────────────────
<h1>Title</h1>              → # Title
<h2>Subtitle</h2>            → ## Subtitle
<h3>Section</h3>             → ### Section
<p>Text</p>                  → Text\n\n
<strong>bold</strong>        → **bold**
<em>italic</em>              → *italic*
<a href="url">text</a>       → [text](url)
<img src="x" alt="y">        → ![y](x)
<code>inline</code>          → `inline`
<pre><code>block</code></pre> → ```\nblock\n```
<ul><li>item</li></ul>       → - item
<ol><li>item</li></ol>       → 1. item
<blockquote>text</blockquote>→ > text
<hr>                         → ---
<br>                         → \n
<table>...</table>           → Markdown table (if simple)
```

### Special Content Handling

```
CODE BLOCKS:
├── Preserve language identifier from class="language-xxx"
├── Keep formatting and indentation
├── Don't convert HTML entities inside code blocks
└── Preserve line numbers if present

TABLES:
├── Simple tables → markdown table format
├── Complex tables → preserve as HTML or extract as list
├── Data tables → extract as structured data (JSON)
└── Layout tables → discard (they're not data)

IMAGES:
├── Extract src and alt text
├── Convert to markdown: ![alt](src)
├── If no alt text, use filename or omit
└── Note: data: URIs are embedded, not referenced

EMBEDDED CONTENT:
├── Videos → extract URL, note platform
├── Tweets → extract text content
├── Iframes → note source URL
└── Social embeds → extract text, discard widget chrome
```

## Content Normalization

### Text Cleaning Pipeline

```
1. DECODE HTML ENTITIES
   &amp; → &    &lt; → <    &gt; → >    &nbsp; → space
   &#39; → '   &quot; → "   &#x27; → '

2. NORMALIZE WHITESPACE
   Multiple spaces → single space
   Multiple newlines → double newline
   Leading/trailing whitespace → trim
   Tab characters → spaces

3. NORMALIZE UNICODE
   Smart quotes: ""'' → ""''
   Dashes: – — → -- ---
   Ellipsis: … → ...
   Non-breaking spaces: → regular space
   Zero-width characters: → remove

4. FIX ENCODING
   Detect encoding from headers/meta
   Convert to UTF-8
   Remove BOM if present
   Replace mojibake where detectable

5. NORMALIZE URLs
   Make relative URLs absolute
   Remove tracking parameters
   Decode percent-encoding where readable
```

### Content Quality Metrics

```
QUALITY SCORE FACTORS:
──────────────────────
├── Text density (content vs markup ratio)
│   Good: > 0.5 (more text than HTML)
│   Poor: < 0.2 (mostly markup)
│
├── Paragraph count
│   Good: > 3 paragraphs
│   Poor: 1-2 short paragraphs
│
├── Average paragraph length
│   Good: 50-300 words per paragraph
│   Poor: < 20 words (likely fragments)
│
├── Heading structure
│   Good: Has <h1> + multiple <h2>/<h3>
│   Poor: No heading hierarchy
│
├── Metadata completeness
│   Good: Title + description + date
│   Poor: Missing multiple metadata fields
│
└── Link density
    Good: < 30% of text is links
    Poor: > 50% of text is links (likely navigation)
```

## Extraction by Source Type

### RSS/Atom Feeds
```
Extract: title, link, description, pubDate, author
Parse: XML with namespace awareness
Normalize: ISO 8601 dates
Output: Ordered list of items
```

### JSON APIs
```
Extract: Relevant fields from response
Handle: Nested objects, arrays, pagination
Normalize: Flatten where appropriate
Output: Structured data
```

### PDF Content
```
Extract: Text blocks, tables, images
Challenge: Layout varies, no semantic markup
Approach: Text extraction + structure inference
Output: Markdown with sections
```

### Social Media Posts
```
Extract: Text content, media URLs, timestamps
Handle: Mentions (@user), hashtags, emojis
Normalize: Expand shortened URLs
Output: Clean text with metadata
```

## Firecrawl Extraction Templates

### Schema-Based Extraction Patterns

```
ARTICLE EXTRACTION:
  prompt: "Extract the article title, author, publication date, and main content"
  schema:
    title: string
    author: string
    datePublished: string
    content: string
    tags: string[]

PRODUCT PAGE EXTRACTION:
  prompt: "Extract product details including pricing, availability, and specifications"
  schema:
    name: string
    price: number
    currency: string
    inStock: boolean
    specifications: object
    images: string[]
    rating: number

DIRECTORY/LISTING EXTRACTION:
  prompt: "Extract all items from this directory listing"
  schema:
    items:
      type: array
      items:
        name: string
        description: string
        url: string
        category: string
        location: string

DOCUMENTATION EXTRACTION:
  prompt: "Extract API documentation including endpoints, parameters, and examples"
  schema:
    endpoints:
      type: array
      items:
        method: string
        path: string
        description: string
        parameters: array
        responseExample: string
```

### Multi-Modal Extraction Strategy

```
CONTENT TYPE          EXTRACTION APPROACH
─────────────────────────────────────────────────────────────
Static HTML           → /scrape with formats: ["markdown"]
JavaScript-rendered   → /scrape with actions + waitFor
Structured data       → /extract with JSON schema
Multiple pages        → /crawl + /extract pipeline
PDFs/documents        → /scrape (Firecrawl handles PDF rendering)
Screenshots needed    → /scrape with formats: ["screenshot"]
Full site knowledge   → /crawl with includePaths scoping
```

## When to Use

- Extracting structured data from HTML, JSON, or XML responses
- Converting web content to Markdown or clean text
- Parsing metadata (Open Graph, JSON-LD, microdata) from pages
- Normalizing content from diverse sources into consistent formats
- Removing boilerplate, ads, and navigation from article content

## Limitations

- Extraction accuracy depends on source HTML structure consistency
- JavaScript-rendered content may not be present in initial HTML
- Tables and complex layouts may lose structure during extraction
- Binary formats (PDFs, images) require specialized extraction tools

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-fetching](../web-fetching/SKILL.md) | Raw content is obtained via web fetching |
| [web-crawling](../web-crawling/SKILL.md) | Extraction is applied to pages discovered during crawling |
| [web-research](../web-research/SKILL.md) | Extracted content feeds into research workflows |
| [data-synthesis](../data-synthesis/SKILL.md) | Extracted data is combined during synthesis |
| [firecrawl-web-crawling](../firecrawl-web-crawling/SKILL.md) | Schema-based extraction via Firecrawl /extract endpoint |
