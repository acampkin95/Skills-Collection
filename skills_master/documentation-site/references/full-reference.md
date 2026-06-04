---
name: documentation-site
description: Documentation site generation with Docusaurus, Nextra, Starlight, and VitePress for technical docs. Use this skill when Docusaurus, Nextra, Starlight, VitePress, documentation site, API reference, docs versioning, sidebar configuration, MDX, search integration, docs deployment, GitHub Pages, Vercel docs, Netlify docs, information architecture. Use this skill when setting up documentation sites and frameworks, designing information architecture and navigation, configuring sidebar organization and content structure, implementing site search and discoverability, managing documentation versioning and releases, writing API references and guides, deploying docs to GitHub Pages/Vercel/Netlify, and optimizing documentation for technical audiences.
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

## Prerequisites

- Requirement 1
- Requirement 2

## Step 1: First Thing

Explanation and code example.

```language
code here
```

## Step 2: Next Thing

...

## Troubleshooting

### Common Error: X
Solution...

## Next Steps

- [Related Guide](./next-guide.md)
- [API Reference](../api-reference/relevant.md)
```

## Docusaurus Quick Setup

```bash
npx create-docusaurus@latest my-docs classic --typescript
cd my-docs
npm run start
```

### docusaurus.config.ts

```typescript
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'My Project',
  tagline: 'Documentation for My Project',
  url: 'https://docs.example.com',
  baseUrl: '/',
  favicon: 'img/favicon.ico',
  organizationName: 'my-org',
  projectName: 'my-project',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/my-org/my-project/tree/main/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'My Project',
      items: [
        { type: 'docSidebar', sidebarId: 'docs', label: 'Docs' },
        { to: '/blog', label: 'Blog' },
        { href: 'https://github.com/my-org/my-project', label: 'GitHub', position: 'right' },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        { title: 'Docs', items: [{ label: 'Getting Started', to: '/docs/getting-started' }] },
        { title: 'Community', items: [{ label: 'Discord', href: 'https://discord.gg/...' }] },
      ],
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'my-project',
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
```

## Nextra Quick Setup

```bash
npx create-next-app my-docs
cd my-docs
npm install nextra nextra-theme-docs
```

### next.config.mjs

```javascript
import nextra from 'nextra';

const withNextra = nextra({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
  defaultShowCopyCode: true,
});

export default withNextra({
  output: 'export', // For static export
});
```

### theme.config.tsx

```tsx
import type { DocsThemeConfig } from 'nextra-theme-docs';

const config: DocsThemeConfig = {
  logo: <span style={{ fontWeight: 800 }}>My Project</span>,
  project: { link: 'https://github.com/my-org/my-project' },
  docsRepositoryBase: 'https://github.com/my-org/my-project/tree/main',
  footer: { text: `MIT ${new Date().getFullYear()} My Org` },
  useNextSeoProps() {
    return { titleTemplate: '%s – My Project' };
  },
  sidebar: { defaultMenuCollapseLevel: 1, toggleButton: true },
  toc: { float: true },
  feedback: { content: 'Question? Give us feedback →' },
  editLink: { text: 'Edit this page on GitHub' },
};

export default config;
```

### Navigation with _meta.json

```json
{
  "index": "Introduction",
  "getting-started": "Getting Started",
  "guides": {
    "title": "Guides",
    "type": "separator"
  },
  "authentication": "Authentication",
  "data-fetching": "Data Fetching",
  "---": { "type": "separator" },
  "api-reference": "API Reference",
  "changelog": {
    "title": "Changelog",
    "theme": { "timestamp": true }
  }
}
```

## Search Integration

### Pagefind (Static, Zero-Config)

```bash
# After building the site
npx pagefind --site dist
```

### Local Search (Docusaurus)

```bash
npm install @easyops-cn/docusaurus-search-local
```

```javascript
// docusaurus.config.js themes
themes: [
  ['@easyops-cn/docusaurus-search-local', { hashed: true }],
],
```

### Flexsearch (Nextra — built-in)

Nextra includes Flexsearch by default. No additional configuration needed.

## Versioning Strategy

### When to Version

- **API docs**: Version when API has breaking changes
- **Product docs**: Version for major releases
- **Tutorials**: Generally don't version (always show latest)

### Docusaurus Versioning

```bash
# Create a version snapshot
npm run docusaurus docs:version 1.0

# Structure after versioning:
# docs/              → "Next" (unreleased)
# versioned_docs/
#   version-1.0/     → Stable v1.0
# versioned_sidebars/
#   version-1.0-sidebars.json
# versions.json      → ["1.0"]
```

## Deployment

### GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy Docs
on:
  push:
    branches: [main]
    paths: ['docs/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
        working-directory: docs
      - run: npm run build
        working-directory: docs
      - uses: actions/upload-pages-artifact@v3
        with: { path: docs/build }
      - uses: actions/deploy-pages@v4
```

### Vercel

```json
{
  "buildCommand": "cd docs && npm run build",
  "outputDirectory": "docs/build"
}
```

See [references/docusaurus-setup.md](references/docusaurus-setup.md) for advanced Docusaurus configuration.

See [references/nextra-setup.md](references/nextra-setup.md) for Nextra patterns and MDX components.

See [references/api-reference.md](references/api-reference.md) for TypeDoc, OpenAPI, and SDK documentation.
