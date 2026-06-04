---
name: nextjs16-fullstack
description: Next.js 16 full-stack with React 19, Tailwind v4, Zustand v5, TanStack Query, Server Actions, and Cache Components.
version: 2.0.0
reviewed: "2026-06-04"
---
# Next.js 16 Full-Stack Development

Production-ready full-stack patterns for Next.js 16, React 19, and modern tooling.

## Security Notice

**Next.js 16.0.10+ required** — patches RSC vulnerabilities:
- CVE-2025-66478 (RCE, CVSS 10.0) — fixed in 16.0.7+
- CVE-2025-55183 (source exposure) — fixed in 16.0.10+
- CVE-2025-67779 (DoS) — fixed in 16.0.10+

Upgrade immediately: `npm install next@latest`

## Next.js 16 Core Features

### Cache Components & `use cache` Directive

The defining innovation is granular caching control:

```javascript
'use cache';
export async function getStaticData() {
  return await fetchCachedData();
}
```

**Benefits:**
- Replaces implicit ISR with explicit control
- Dynamic code executes at request time by default
- Build on Partial Pre-Rendering foundation

### Turbopack Default

- 2-5x faster production builds
- 10x faster Fast Refresh
- No config changes required

### New Caching APIs

```javascript
revalidateTag('data', { cacheLife: '1h' });
updateTag('content');
refresh();
```

### DevTools MCP (New!)

**AI-native debugging** with Cursor/Claude integration:
- Direct AI access to routing tree and logs
- Automated upgrades via natural language

```bash
next dev --mcp
```

## Reference Files

| Resource | Purpose |
|----------|---------|
| `references/config-templates.md` | next.config.ts, tsconfig, postcss configs |
| `references/advanced-patterns.md` | Forms, streaming, caching strategies |
| `references/nextauth.md` | Auth.js v5, OAuth, RBAC, credentials |
| `references/migration-guide.md` | v15 → v16 upgrade paths |
| `references/troubleshooting.md` | Hydration, "dead UI", common errors |


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.