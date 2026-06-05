---
name: firecrawl-crawl
description: "Bulk extraction — crawl sites, download pages to disk, and autonomous structured extraction (agent)."
allowed-tools:
  - Bash(firecrawl *)
  - Bash(npx firecrawl *)
version: 2.0.0
reviewed: "2026-06-04"
---

# firecrawl crawl

Bulk extract content from a website. Crawls pages following links up to a depth/limit.

## When to use

- You need content from many pages on a site (e.g., all `/docs/`)
- You want to extract an entire site section
- Step 4 in the [workflow escalation pattern](../firecrawl/SKILL.md): search → scrape → map → **crawl** → interact

## Quick start

```bash
# Crawl a docs section
firecrawl crawl "<url>" --include-paths /docs --limit 50 --wait -o .firecrawl/crawl.json

# Full crawl with depth limit
firecrawl crawl "<url>" --max-depth 3 --wait --progress -o .firecrawl/crawl.json

# Check status of a running crawl
firecrawl crawl <job-id>
```

## Options

| Option                    | Description                                 |
| ------------------------- | ------------------------------------------- |
| `--wait`                  | Wait for crawl to complete before returning |
| `--progress`              | Show progress while waiting                 |
| `--limit <n>`             | Max pages to crawl                          |
| `--max-depth <n>`         | Max link depth to follow                    |
| `--include-paths <paths>` | Only crawl URLs matching these paths        |
| `--exclude-paths <paths>` | Skip URLs matching these paths              |
| `--delay <ms>`            | Delay between requests                      |
| `--max-concurrency <n>`   | Max parallel crawl workers                  |
| `--pretty`                | Pretty print JSON output                    |
| `-o, --output <path>`     | Output file path                            |

## Tips

- Always use `--wait` when you need the results immediately. Without it, crawl returns a job ID for async polling.
- Use `--include-paths` to scope the crawl — don't crawl an entire site when you only need one section.
- Crawl consumes credits per page. Check `firecrawl credit-usage` before large crawls.

## See also

- [firecrawl](../firecrawl/SKILL.md) — master router for Firecrawl CLI workflows
- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) — scrape individual pages
- [firecrawl-map](../firecrawl-map/SKILL.md) — discover URLs before deciding to crawl
- [firecrawl-download](../firecrawl-download/SKILL.md) — download site to local files (uses map + scrape)

## download — Save Site to Local Files

Combines `map` + `scrape` to save an entire site as local files under `.firecrawl/`. Always pass `-y` to skip confirmation.

```bash
firecrawl download https://docs.example.com --screenshot --limit 20 -y
firecrawl download https://docs.example.com --include-paths "/features,/sdks" --exclude-paths "/zh,/ja" -y
```

| Option | Description |
|--------|-------------|
| `--limit <n>` | Max pages to download |
| `--search <query>` | Filter URLs |
| `--include-paths` / `--exclude-paths` | Path filtering |
| `-y` | Skip confirmation (always use in automated flows) |

All scrape options work with download (`-f`, `--only-main-content`, `--screenshot`, etc.)

## agent — Autonomous Structured Extraction

AI-powered extraction from complex multi-page sites (2-5 min). Use when manual scraping would require navigating many pages.

```bash
firecrawl agent "extract all pricing tiers" --wait -o .firecrawl/pricing.json
firecrawl agent "extract products" --schema '{"type":"object","properties":{"name":{"type":"string"},"price":{"type":"number"}}}' --wait -o .firecrawl/products.json
```

| Option | Description |
|--------|-------------|
| `--urls <urls>` | Starting URLs |
| `--schema <json>` | JSON schema for structured output |
| `--model <model>` | `spark-1-mini` or `spark-1-pro` |
| `--max-credits <n>` | Credit limit |
| `--wait` | Wait for completion (recommended) |

- Always use `--wait` for inline results. Use `--max-credits` to cap spending.
- For simple single-page extraction, prefer `scrape` — faster and cheaper.
