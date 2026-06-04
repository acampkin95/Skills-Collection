---
name: firecrawl-build
description: Master router for Firecrawl app integration — credentials, SDK setup, and endpoint selection.
license: ISC
metadata:
  author: firecrawl
  version: "2.0.0"
  homepage: https://www.firecrawl.dev
reviewed: "2026-06-04"
---

# Firecrawl Build — Master Router

Use this skill for application integration, not live CLI research.

## Router

| User need | Route to | Notes |
| --- | --- | --- |
| Get `FIRECRAWL_API_KEY`, authenticate, install the SDK, or wire project setup | `firecrawl-build-onboarding` | First-time setup |
| Start from a query | `firecrawl-build-search` | Discovery before extraction |
| Start from a known URL | `firecrawl-build-scrape` | Single-page extraction |
| Need clicks, forms, pagination, or login | `firecrawl-build-interact` | Browser actions after scrape |

## Defaults

- Search first when the URL is unknown.
- Scrape first when the URL is known.
- Escalate to interact only when clicks, forms, login, or pagination are required.
- Read the source-of-truth docs for the target language before writing code.

## Source of truth

- Node / TypeScript, Python, Rust, Java, Elixir, cURL / REST: `https://docs.firecrawl.dev/agent-source-of-truth/`

## See also

- [firecrawl](../firecrawl/SKILL.md) — master router for Firecrawl CLI workflows
