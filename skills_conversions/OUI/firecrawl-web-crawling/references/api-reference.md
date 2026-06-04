# Firecrawl API Reference

## Authentication & Base URLs

```
AUTHENTICATION:
  Header: Authorization: Bearer <FIRECRAWL_API_KEY>
  Keys: Obtained from Firecrawl dashboard

BASE URLS:
  v2 (current):  https://api.firecrawl.dev/v2
  v1 (legacy):   https://api.firecrawl.dev/v1
  MCP server:    https://mcp.firecrawl.dev/{api_key}/v2/mcp
```

## Endpoint Overview

| Endpoint | Method | Purpose | Sync/Async |
|----------|--------|---------|------------|
| `/scrape` | POST | Single-page content extraction | Sync |
| `/crawl` | POST | Multi-page site crawl from seed URL | Async |
| `/crawl/status/{id}` | GET | Poll crawl job progress | — |
| `/extract` | POST | Structured data extraction from URLs | Async |
| `/extract/status/{id}` | GET | Poll extract job progress | — |
| `/map` | POST | Discover URLs on a site | Sync |
| `/agent` | POST | AI-agent extraction with prompt | Async |
| `/agent/status/{id}` | GET | Poll agent job progress | — |
```
