---
name: firecrawl-scrape
description: "Scrape URLs, discover pages (map), and parse local files (PDF, DOCX) into markdown."
allowed-tools:
  - Bash(firecrawl *)
  - Bash(npx firecrawl *)
version: 2.0.0
reviewed: "2026-06-04"
---

# firecrawl scrape

Scrape one or more URLs. Returns clean, LLM-optimized markdown. Multiple URLs are scraped concurrently.

## When to use

- You have a specific URL and want its content
- The page is static or JS-rendered (SPA)
- Step 2 in the [workflow escalation pattern](../firecrawl/SKILL.md): search → **scrape** → map → crawl → interact

## Quick start

```bash
# Basic markdown extraction
firecrawl scrape "<url>" -o .firecrawl/page.md

# Main content only, no nav/footer
firecrawl scrape "<url>" --only-main-content -o .firecrawl/page.md

# Wait for JS to render, then scrape
firecrawl scrape "<url>" --wait-for 3000 -o .firecrawl/page.md

# Multiple URLs (each saved to .firecrawl/)
firecrawl scrape https://example.com https://example.com/blog https://example.com/docs

# Get markdown and links together
firecrawl scrape "<url>" --format markdown,links -o .firecrawl/page.json

# Ask a question about the page
firecrawl scrape "https://example.com/pricing" --query "What is the enterprise plan price?"
```

## Options

| Option                   | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `-f, --format <formats>` | Output formats: markdown, html, rawHtml, links, screenshot, json |
| `-Q, --query <prompt>`   | Ask a question about the page content (5 credits)                |
| `-H`                     | Include HTTP headers in output                                   |
| `--only-main-content`    | Strip nav, footer, sidebar — main content only                   |
| `--wait-for <ms>`        | Wait for JS rendering before scraping                            |
| `--include-tags <tags>`  | Only include these HTML tags                                     |
| `--exclude-tags <tags>`  | Exclude these HTML tags                                          |
| `-o, --output <path>`    | Output file path                                                 |

## Tips

- **Prefer plain scrape over `--query`.** Scrape to a file, then use `grep`, `head`, or read the markdown directly — you can search and reason over the full content yourself. Use `--query` only when you want a single targeted answer without saving the page (costs 5 extra credits).
- **Try scrape before interact.** Scrape handles static pages and JS-rendered SPAs. Only escalate to `interact` when you need interaction (clicks, form fills, pagination).
- Multiple URLs are scraped concurrently — check `firecrawl --status` for your concurrency limit.
- Single format outputs raw content. Multiple formats (e.g., `--format markdown,links`) output JSON.
- Always quote URLs — shell interprets `?` and `&` as special characters.
- Naming convention: `.firecrawl/{site}-{path}.md`

## See also

- [firecrawl](../firecrawl/SKILL.md) — master router for Firecrawl CLI workflows
- [firecrawl-search](../firecrawl-search/SKILL.md) — find pages when you don't have a URL
- [firecrawl-interact](../firecrawl-interact/SKILL.md) — when scrape can't get the content, use `interact` to click, fill forms, etc.
- [firecrawl-download](../firecrawl-download/SKILL.md) — bulk download an entire site to local files

## map — Discover URLs on a Site

Find URLs on a site. Use `--search` to find a specific page within a large site.

```bash
firecrawl map "<url>" --search "authentication" -o .firecrawl/filtered.txt
firecrawl map "<url>" --limit 500 --json -o .firecrawl/urls.json
```

| Option | Description |
|--------|-------------|
| `--limit <n>` | Max URLs to return |
| `--search <query>` | Filter URLs by search query |
| `--include-subdomains` | Include subdomain URLs |

## parse — Local File Extraction

Turn a local file (PDF, DOCX, XLSX, HTML) into clean markdown. **Not a URL** — use scrape for URLs.

```bash
firecrawl parse ./paper.pdf -o .firecrawl/paper.md
firecrawl parse ./paper.pdf -S -o .firecrawl/paper-summary.md
firecrawl parse ./paper.pdf -Q "What are the conclusions?" -o .firecrawl/paper-qa.md
```

| Option | Description |
|--------|-------------|
| `-S, --summary` | AI-generated summary |
| `-Q, --query <prompt>` | Ask a question about the content |
| `-f, --format <fmt>` | `markdown` (default), `html`, `summary` |

- Max upload: 50 MB. Credits: ~1 per PDF page.
- Quote paths with spaces: `firecrawl parse "./My Doc.pdf" -o .firecrawl/mydoc.md`
