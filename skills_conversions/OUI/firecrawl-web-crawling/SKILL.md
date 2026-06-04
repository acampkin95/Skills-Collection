---
name: firecrawl-web-crawling
description: "Firecrawl API (v2) for production-grade web scraping, site crawling, structured data extraction, URL mapping, and AI-agent-driven extraction. Covers all endpoints (/scrape, /crawl, /extract, /map, /agent), Open WebUI pipeline integration, RAG workflows, and MCP server patterns. Use when scraping pages, crawling sites, extracting structured data from URLs, building knowledge bases, or integrating web data into LLM pipelines."
version: "1.0.0"
metadata:
  category: web-interaction
  scope: non-cli
---

# Firecrawl — Production Web Scraping & Extraction API

Firecrawl by Mendable provides cloud-based web scraping, crawling, structured extraction, and AI-agent-driven data collection. Designed for LLM and RAG pipelines with first-class Open WebUI and MCP integration.

## Endpoint Details

### /scrape — Single Page Extraction

```
PURPOSE: Extract content from a single URL with format options

REQUEST:
  POST /v2/scrape
  {
    "url": "https://example.com/article",
    "formats": ["markdown", "html", "screenshot"],
    "onlyMainContent": true,
    "timeout": 30000,
    "waitFor": 1000,
    "actions": [
      { "type": "click", "selector": ".accept-cookies" },
      { "type": "wait", "milliseconds": 500 }
    ]
  }

KEY PARAMETERS:
  ├── url (required): Target URL to scrape
  ├── formats: ["markdown", "html", "screenshot", "links", "rawHtml"]
  ├── onlyMainContent: Remove nav, footer, sidebar noise (default: true)
  ├── timeout: Max wait in ms (default: 30000)
  ├── waitFor: Delay before extraction in ms
  ├── actions: Sequential browser interactions before extraction
  ├── includeTags: CSS selectors to include
  ├── excludeTags: CSS selectors to exclude
  └── headers: Custom HTTP headers for the request

RESPONSE:
  {
    "success": true,
    "data": {
      "markdown": "# Article Title\n\nContent...",
      "html": "<article>...</article>",
      "metadata": {
        "title": "Article Title",
        "description": "...",
        "language": "en",
        "sourceURL": "https://example.com/article"
      }
    }
  }

WHEN TO USE:
  ├── Extract a single article or page
  ├── Get markdown for LLM consumption
  ├── Capture page screenshots
  ├── Extract specific sections via CSS selectors
  └── Handle cookie banners or modals before extraction
```

### /crawl — Multi-Page Site Crawl

```
PURPOSE: Crawl an entire site or section, extracting content from each page

REQUEST:
  POST /v2/crawl
  {
    "url": "https://docs.example.com",
    "limit": 100,
    "maxDepth": 3,
    "formats": ["markdown"],
    "excludePaths": ["/blog", "/changelog"],
    "includePaths": ["/docs/api"],
    "allowBackwardCrawling": false,
    "allowExternalLinks": false,
    "webhook": {
      "url": "https://your-server.com/webhook",
      "headers": { "Authorization": "Bearer token" }
    }
  }

KEY PARAMETERS:
  ├── url (required): Seed URL to start crawling from
  ├── limit: Max pages to crawl (plan-dependent cap)
  ├── maxDepth: Max link-depth from seed (default: 10)
  ├── formats: Per-page output formats (same as /scrape)
  ├── excludePaths: URL path patterns to skip (glob)
  ├── includePaths: URL path patterns to include (glob)
  ├── allowBackwardCrawling: Follow parent-path links
  ├── allowExternalLinks: Follow links to other domains
  ├── webhook: Callback URL when crawl completes
  ├── ignoreSitemap: Skip sitemap.xml discovery
  └── sitemapOnly: Only crawl URLs from sitemap

RESPONSE (async — poll /crawl/status/{id}):
  {
    "success": true,
    "id": "crawl-job-id",
    "status": "completed",
    "total": 47,
    "completed": 47,
    "data": [
      { "markdown": "...", "metadata": { "sourceURL": "..." } },
      ...
    ]
  }

WHEN TO USE:
  ├── Build documentation knowledge bases
  ├── Crawl entire sites for RAG ingestion
  ├── Archive site content
  ├── Discover and extract all pages in a section
  └── Generate site-wide content datasets
```

### /extract — Structured Data Extraction

```
PURPOSE: Extract structured JSON from one or more URLs using LLM

REQUEST (schema mode):
  POST /v2/extract
  {
    "urls": ["https://example.com/products"],
    "prompt": "Extract all product names, prices, and availability",
    "schema": {
      "type": "object",
      "properties": {
        "products": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "price": { "type": "number" },
              "inStock": { "type": "boolean" }
            }
          }
        }
      }
    },
    "enableWebSearch": false
  }

REQUEST (prompt-only mode):
  POST /v2/extract
  {
    "urls": ["https://example.com/about"],
    "prompt": "Extract company founding year, HQ location, and employee count"
  }

KEY PARAMETERS:
  ├── urls (required): Array of URLs or domain patterns (e.g., ["example.com/*"])
  ├── prompt: Natural language extraction instruction
  ├── schema: JSON Schema for structured output
  ├── enableWebSearch: Allow agent to follow external links (default: false)
  └── systemPrompt: System-level instruction for the extraction LLM

RESPONSE (async — poll /extract/status/{id}):
  {
    "success": true,
    "data": {
      "products": [
        { "name": "Widget A", "price": 29.99, "inStock": true },
        { "name": "Widget B", "price": 49.99, "inStock": false }
      ]
    }
  }

WHEN TO USE:
  ├── Extract structured data from product pages, directories, listings
  ├── Pull specific fields from multiple pages at once
  ├── Build datasets from web sources
  ├── Domain-wide extraction with wildcard URLs
  └── Schema-validated data collection for pipelines
```

### /map — URL Discovery

```
PURPOSE: Discover all URLs on a site without full crawl

REQUEST:
  POST /v2/map
  {
    "url": "https://docs.example.com",
    "includeSubdomains": false,
    "search": "API reference authentication",
    "ignoreSitemap": false,
    "limit": 500
  }

KEY PARAMETERS:
  ├── url (required): Base URL to map from
  ├── search: Filter URLs by relevance to query
  ├── includeSubdomains: Include subdomain URLs
  ├── ignoreSitemap: Skip sitemap.xml
  └── limit: Max URLs to return

RESPONSE:
  {
    "success": true,
    "links": [
      "https://docs.example.com/api/auth",
      "https://docs.example.com/api/users",
      "https://docs.example.com/api/products",
      ...
    ]
  }

WHEN TO USE:
  ├── Plan crawl scope before running expensive /crawl
  ├── Discover API endpoints or doc pages
  ├── Build URL lists for batch /extract operations
  └── Quick site structure reconnaissance
```

### /agent — AI-Agent Extraction

```
PURPOSE: Autonomous extraction — agent finds sources and extracts data

REQUEST:
  POST /v2/agent
  {
    "prompt": "Find the top 5 competitors of Acme Corp and extract their pricing",
    "schema": {
      "type": "object",
      "properties": {
        "competitors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "url": { "type": "string" },
              "pricing": { "type": "string" }
            }
          }
        }
      }
    }
  }

KEY PARAMETERS:
  ├── prompt (required): What to find and extract
  ├── schema: Optional JSON Schema for output structure
  └── The agent autonomously discovers sources and extracts

WHEN TO USE:
  ├── Don't know exact URLs — let agent find sources
  ├── Research tasks requiring web discovery + extraction
  ├── Competitive analysis across multiple sites
  └── Open-ended data collection with structured output
```

## Integration Patterns

### Open WebUI Pipeline Integration

```
ARCHITECTURE:
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Open WebUI  │────▸│  Firecrawl      │────▸│  LLM/RAG     │
│  Chat Input  │     │  Pipeline       │     │  Processing   │
│              │◂────│  (scrape/crawl) │◂────│              │
└──────────────┘     └─────────────────┘     └──────────────┘

PIPELINE CONFIGURATION:
  ├── Add Firecrawl as an Open WebUI Pipeline
  ├── Configure FIRECRAWL_API_KEY in pipeline settings
  ├── Base URL: https://api.firecrawl.dev/v1 (pipeline compat)
  ├── Pipeline exposes: scrape, crawl, extract, map as tools
  └── LLM can invoke Firecrawl tools during conversation

USAGE IN CONVERSATION:
  User: "What does the React docs say about Server Components?"
  → Pipeline triggers /scrape on react.dev/docs
  → Returns markdown content to LLM context
  → LLM answers with cited source content
```

### MCP Server Integration

```
MCP CONFIGURATION:
  Server URL: https://mcp.firecrawl.dev/{api_key}/v2/mcp
  Transport: Streamable HTTP
  Auth: API key embedded in URL path

EXPOSED MCP TOOLS:
  ├── firecrawl_scrape   — Scrape single URL
  ├── firecrawl_crawl    — Crawl site from seed URL
  ├── firecrawl_extract  — Extract structured data
  ├── firecrawl_map      — Discover URLs on site
  └── firecrawl_search   — Search and extract from web

USAGE WITH OPENAI:
  Wire MCP server into OpenAI Responses API
  Agent calls Firecrawl tools as function invocations
  Results returned in conversation context
```

### RAG Pipeline Pattern

```
FULL RAG WORKFLOW:
1. DISCOVER  → /map to find relevant pages
2. CRAWL     → /crawl to extract content from discovered pages
3. CHUNK     → Split markdown into LLM-sized chunks
4. EMBED     → Generate vector embeddings per chunk
5. STORE     → Index in vector store (Weaviate, Qdrant, etc.)
6. RETRIEVE  → Semantic search at query time
7. GENERATE  → LLM generates answer with retrieved context

OPTIMIZATION:
  ├── Use /crawl with formats: ["markdown"] for cleanest RAG input
  ├── Set onlyMainContent: true to reduce noise
  ├── Use excludePaths to skip irrelevant sections
  ├── Batch crawl large sites with limit + depth controls
  └── Re-crawl periodically for content freshness
```

## Decision Framework

### When to Use Each Endpoint

```
NEED                          → ENDPOINT     → WHY
─────────────────────────────────────────────────────────────
Single page content           → /scrape      → Fast, synchronous
Entire site or section        → /crawl       → Async, multi-page
Specific data from pages      → /extract     → Structured + schema
Discover what pages exist     → /map         → Lightweight recon
Unknown sources, let AI find  → /agent       → Autonomous search
Page + dynamic interaction    → /scrape      → Actions parameter
Build knowledge base          → /crawl       → Bulk extraction
Product/service comparison    → /extract     → Schema across URLs
Research with web discovery   → /agent       → Finds + extracts
RAG ingestion pipeline        → /crawl → /extract → embed → store
```

## Best Practices

```
CRAWLING:
  ├── Start with /map to plan scope before expensive /crawl
  ├── Use includePaths/excludePaths to narrow crawl targets
  ├── Set limit to prevent runaway crawls
  ├── Use webhook for async notification on large crawls
  └── Respect robots.txt — Firecrawl handles this server-side

EXTRACTION:
  ├── Provide a schema whenever possible (more reliable than prompt-only)
  ├── Use prompt + schema together for best results
  ├── Break complex extractions into focused single-purpose requests
  ├── Test schema on 2-3 URLs before batch extraction
  └── Use enableWebSearch only when URLs don't cover the topic

PERFORMANCE:
  ├── /scrape is synchronous — use for single pages
  ├── /crawl and /extract are async — poll for results
  ├── Batch multiple URLs in single /extract call
  ├── Use onlyMainContent: true to reduce output size
  └── Cache results locally to avoid re-scraping

COST OPTIMIZATION:
  ├── /map before /crawl to estimate scope
  ├── Use excludePaths to skip irrelevant pages
  ├── Set reasonable limit values (don't crawl 10k pages blindly)
  ├── Cache markdown output for reuse across queries
  └── Re-use crawl results for multiple extraction queries
```

## When to Use

- Scraping single pages or crawling entire sites via Firecrawl API
- Extracting structured data from web pages with schema validation
- Building RAG knowledge bases from web content
- Integrating web data into Open WebUI pipelines or MCP workflows
- Discovering URLs and planning crawl strategies before full extraction
- AI-agent-driven research where sources are unknown upfront

## Limitations

- Requires Firecrawl API key and active subscription for production use
- Free tier has strict rate limits (10/min scrape, 1/min crawl/extract)
- Async endpoints require polling — no real-time streaming of results
- JavaScript-heavy SPAs may require action sequences for full rendering
- Credit consumption varies by endpoint and extraction complexity
- Domain-wide extraction with wildcards can consume significant credits

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-crawling](../web-crawling/SKILL.md) | General crawling methodology and ethics — Firecrawl is one implementation |
| [content-extraction](../content-extraction/SKILL.md) | Content parsing and normalization — Firecrawl provides raw extraction |
| [deep-research](../deep-research/SKILL.md) | Firecrawl crawl/extract feeds structured data into deep research workflows |
| [web-fetching](../web-fetching/SKILL.md) | Basic HTTP patterns — Firecrawl handles rendering, anti-bot, and parsing |
| [tapestry](../tapestry/SKILL.md) | Firecrawl output feeds content-to-action planning pipelines |
| [API Reference](references/api-reference.md) | Complete endpoint list, rate limits, authentication details |
