---
name: nextjs
description: Master router for Next.js — implementation, audits, CMS integration, and core reference.
version: 2.0.0
reviewed: "2026-06-04"
---

# Next.js — Master Router

Use the narrowest Next.js skill that matches the task.

## Router

| User need | Route to |
| --- | --- |
| Build or implement a Next.js app, auth, server actions, caching, deployment | `nextjs16-fullstack` |
| Audit, review, or harden a Next.js codebase | `nextjs-code-audit` |
| Integrate Sanity CMS with Next.js | `sanity-nextjs` |
| General reference, upgrade guidance, core conventions | See references below |

## Quick Reference

| Task | Reference |
|------|-----------|
| Core patterns & critical rules | `references/critical-rules.md` |
| Configuration templates | `references/config-templates.md` |
| Debugging / white screen | `references/troubleshooting.md` |
| Tailwind v4/v5 issues | `references/tailwind-guide.md` |
| Turbopack problems | `references/turbopack-guide.md` |
| Testing setup | `references/testing-guide.md` |
| Deployment (Docker/Vercel) | `references/deployment-guide.md` |
| Ubuntu/Nginx/PostgreSQL | `references/server-infrastructure.md` |
| Full project audit | `references/audit-checklist.md` |
| Full code examples & patterns | `references/full-reference.md` |

## Key Next.js 15/16 Changes

- **Async APIs**: `cookies()`, `headers()`, `params` are now async
- **Turbopack default**: 10x faster dev builds
- **Server Actions**: stable with unguessable IDs
- **React Compiler**: auto-memoization, enable via `experimental.reactCompiler: true`
- **Partial Prerendering**: static shell + dynamic streaming

## Common Commands

```bash
npm run dev                # Dev with Turbopack
npm run build              # Production build
npx tsc --noEmit           # Type check
rm -rf .next               # Clear cache
```
