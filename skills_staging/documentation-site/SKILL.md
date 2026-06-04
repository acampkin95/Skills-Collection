---
name: documentation-site
description: Documentation site generation with Docusaurus, Nextra, Starlight, and VitePress. Use for API references, versioning, search, and docs deployment.
version: 2.0.0
reviewed: "2026-06-04"
---
# Documentation Site Development

## Framework Comparison

| Feature | Docusaurus | Nextra | Starlight | VitePress |
|---------|-----------|--------|-----------|-----------|
| **Base** | React | Next.js | Astro | Vue/Vite |
| **MDX** | Yes | Yes | Yes | No (MD only) |
| **Versioning** | Built-in | Manual | Plugin | Manual |
| **i18n** | Built-in | Manual | Built-in | Built-in |
| **Blog** | Built-in | Plugin | Plugin | Manual |
| **Search** | Algolia/Local | Flexsearch | Pagefind | MiniSearch |
| **Build speed** | Medium | Medium | Fast | Fast |
| **Bundle** | ~200KB | ~100KB | ~50KB | ~50KB |
| **Best for** | Large projects | Next.js teams | Performance | Vue teams |

### Quick Decision

```
Need versioned docs + blog?       → Docusaurus
Already using Next.js?            → Nextra
Performance + minimal JS?         → Starlight
Vue ecosystem / fast builds?      → VitePress
```

## Information Architecture

### Content Organization

```
docs/
├── getting-started/
│   ├── installation.md
│   ├── quick-start.md
│   └── configuration.md
├── guides/
│   ├── authentication.md
│   ├── data-fetching.md
│   └── deployment.md
├── api-reference/
│   ├── client.md
│   ├── server.md
│   └── hooks.md
├── concepts/
│   ├── architecture.md
│   └── data-model.md
└── changelog.md
```

### Sidebar Design Principles

1. **Progressive disclosure**: Basic → Advanced
2. **Task-oriented**: Group by what users want to do
3. **Max 3 levels deep**: Keep hierarchy shallow
4. **Consistent naming**: Use verbs for guides ("Setting up auth"), nouns for references ("API Client")

### Page Structure Template

```markdown
# Page Title

Brief description of what this page covers (1-2 sentences).


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.