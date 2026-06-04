# Docusaurus Advanced Setup Reference

## Quick Start

```bash
# Create new Docusaurus site with TypeScript
npx create-docusaurus@latest my-docs classic --typescript
cd my-docs
npm run start       # Dev server at localhost:3000
npm run build       # Production build to /build
npm run serve       # Serve production build locally
```

## Project Structure

```
my-docs/
├── blog/
│   ├── 2024-01-15-release.md
│   └── authors.yml
├── docs/
│   ├── intro.md
│   ├── getting-started/
│   │   ├── _category_.json
│   │   ├── installation.md
│   │   └── configuration.md
│   └── api/
│       └── overview.md
├── src/
│   ├── components/
│   │   └── HomepageFeatures.tsx
│   ├── css/
│   │   └── custom.css
│   └── pages/
│       ├── index.tsx
│       └── about.md
├── static/
│   └── img/
├── docusaurus.config.ts
├── sidebars.ts
├── babel.config.js
└── tsconfig.json
```

## docusaurus.config.ts — Full Configuration

```typescript
import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'My Project',
  tagline: 'Build something great',
  favicon: 'img/favicon.ico',

  url: 'https://docs.example.com',
  baseUrl: '/',

  organizationName: 'my-org',
  projectName: 'my-project',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/my-org/my-project/tree/main/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          remarkPlugins: [],
          rehypePlugins: [],
          // Versioning
          lastVersion: 'current',
          versions: {
            current: {
              label: '2.x',
              path: '',
            },
          },
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/my-org/my-project/tree/main/',
          blogSidebarCount: 'ALL',
          blogSidebarTitle: 'All posts',
          feedOptions: {
            type: 'all',
            copyright: `Copyright ${new Date().getFullYear()} My Org`,
          },
        },
        theme: {
          customCss: './src/css/custom.css',
        },
        gtag: {
          trackingID: 'G-XXXXXXXXXX',
          anonymizeIP: true,
        },
        sitemap: {
          changefreq: 'weekly' as const,
          priority: 0.5,
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.png',
    metadata: [
      { name: 'keywords', content: 'documentation, api, developer' },
    ],
    navbar: {
      title: 'My Project',
      logo: {
        alt: 'My Project Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        { to: '/blog', label: 'Blog', position: 'left' },
        {
          type: 'docsVersionDropdown',
          position: 'right',
        },
        {
          href: 'https://github.com/my-org/my-project',
          label: 'GitHub',
          position: 'right',
        },
      ],
      hideOnScroll: false,
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/docs/getting-started' },
            { label: 'API Reference', to: '/docs/api' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'Discord', href: 'https://discord.gg/...' },
            { label: 'Twitter', href: 'https://twitter.com/...' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Blog', to: '/blog' },
            { label: 'GitHub', href: 'https://github.com/my-org/my-project' },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} My Org. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'typescript', 'yaml'],
    },
    // Algolia DocSearch
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_ONLY_API_KEY',
      indexName: 'my-project',
      contextualSearch: true,
      searchPagePath: 'search',
    },
    // Announcement bar
    announcementBar: {
      id: 'v2_launch',
      content: 'v2.0 is now available! <a href="/blog/v2-release">Read the announcement</a>',
      backgroundColor: '#3578e5',
      textColor: '#fff',
      isCloseable: true,
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
  } satisfies Preset.ThemeConfig,

  // Additional plugins
  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'api',
        path: 'api',
        routeBasePath: 'api',
        sidebarPath: './sidebarsApi.ts',
      },
    ],
    [
      '@docusaurus/plugin-ideal-image',
      {
        quality: 70,
        max: 1030,
        min: 640,
        steps: 2,
      },
    ],
    async function tailwindPlugin(context, options) {
      return {
        name: 'docusaurus-tailwindcss',
        configurePostCss(postcssOptions) {
          postcssOptions.plugins.push(require('tailwindcss'));
          postcssOptions.plugins.push(require('autoprefixer'));
          return postcssOptions;
        },
      };
    },
  ],

  // Enable Mermaid diagrams
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
};

export default config;
```

## sidebars.ts — Sidebar Configuration

```typescript
import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/configuration',
        'getting-started/quick-start',
      ],
      link: {
        type: 'generated-index',
        title: 'Getting Started',
        description: 'Learn how to set up and configure the project.',
        slug: '/getting-started',
      },
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/authentication',
        'guides/data-fetching',
        'guides/deployment',
        {
          type: 'category',
          label: 'Advanced',
          items: ['guides/advanced/plugins', 'guides/advanced/custom-themes'],
        },
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      link: {
        type: 'doc',
        id: 'api/overview',
      },
      items: [
        'api/client',
        'api/server',
        'api/hooks',
      ],
    },
    {
      // Auto-generated sidebar from directory structure
      type: 'autogenerated',
      dirName: 'tutorials',
    },
    {
      type: 'link',
      label: 'External Resource',
      href: 'https://example.com',
    },
  ],
};

export default sidebars;
```

### Category Metadata (_category_.json)

```json
{
  "label": "Getting Started",
  "position": 1,
  "collapsed": false,
  "link": {
    "type": "generated-index",
    "description": "Learn how to get started."
  }
}
```

## Blog Setup

### Blog Post Frontmatter

```markdown
---
slug: welcome
title: Welcome to Our Blog
authors: [alice, bob]
tags: [announcement, release]
image: ./img/banner.png
hide_table_of_contents: false
date: 2024-01-15
---

First paragraph is the summary (truncated at `<!-- truncate -->`).

<!-- truncate -->

Full content below the fold...
```

### authors.yml

```yaml
alice:
  name: Alice Smith
  title: Lead Engineer
  url: https://github.com/alice
  image_url: https://github.com/alice.png
  email: alice@example.com

bob:
  name: Bob Jones
  title: Developer Advocate
  url: https://github.com/bob
  image_url: https://github.com/bob.png
```

## Plugins

### Algolia DocSearch (Full Setup)

1. Apply at [docsearch.algolia.com](https://docsearch.algolia.com/apply/)
2. Or run your own crawler:

```json
// algolia-config.json (for self-hosted crawler)
{
  "index_name": "my-project",
  "start_urls": ["https://docs.example.com/"],
  "selectors": {
    "lvl0": "header h1",
    "lvl1": "article h2",
    "lvl2": "article h3",
    "lvl3": "article h4",
    "text": "article p, article li"
  }
}
```

### Local Search (Offline / No Algolia)

```bash
npm install @easyops-cn/docusaurus-search-local
```

```typescript
// docusaurus.config.ts
{
  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        language: ['en'],
        highlightSearchTermsOnTargetPage: true,
        indexDocs: true,
        indexBlog: true,
        indexPages: false,
        docsRouteBasePath: '/docs',
      },
    ],
  ],
}
```

### Google Analytics / Plausible

```typescript
// GA4 is built into preset-classic via gtag (shown in config above)

// For Plausible:
plugins: [
  [
    'docusaurus-plugin-plausible',
    {
      domain: 'docs.example.com',
    },
  ],
],
```

## Versioned Docs

```bash
# Create a version snapshot from current docs/
npx docusaurus docs:version 1.0

# Result:
# versioned_docs/version-1.0/    ← snapshot of docs/
# versioned_sidebars/version-1.0-sidebars.json
# versions.json                   ← ["1.0"]

# Create another version
npx docusaurus docs:version 2.0
# versions.json → ["2.0", "1.0"]
```

### Version Configuration

```typescript
// docusaurus.config.ts
docs: {
  lastVersion: 'current',
  versions: {
    current: {
      label: '3.x (Next)',
      path: 'next',
      banner: 'unreleased',
    },
    '2.0': {
      label: '2.0',
      path: '',          // default version at /docs/
      banner: 'none',
    },
    '1.0': {
      label: '1.0',
      path: '1.0',
      banner: 'unmaintained',
    },
  },
},
```

### Version-Specific Content

```mdx
import {CurrentVersion} from '@site/src/components/CurrentVersion';

Install version <CurrentVersion />.
```

## Custom Pages

### React Page (src/pages/about.tsx)

```tsx
import React from 'react';
import Layout from '@theme/Layout';

export default function About(): React.JSX.Element {
  return (
    <Layout title="About" description="About our project">
      <main className="container margin-vert--lg">
        <h1>About</h1>
        <p>Custom page content with full React support.</p>
      </main>
    </Layout>
  );
}
```

### MDX Page (src/pages/support.mdx)

```mdx
---
title: Support
description: Get help with our project
---

# Support

Need help? Here are your options:

- [GitHub Issues](https://github.com/my-org/my-project/issues)
- [Discord Community](https://discord.gg/...)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/my-project)
```

## MDX Components

### Custom Admonitions

```mdx
:::note
This is a note.
:::

:::tip
Helpful tip here.
:::

:::warning
Be careful with this.
:::

:::danger
This is dangerous!
:::

:::info[Custom Title]
Info with a custom title.
:::
```

### Tabs Component

```mdx
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="npm" label="npm" default>

```bash
npm install my-package
```

  </TabItem>
  <TabItem value="yarn" label="yarn">

```bash
yarn add my-package
```

  </TabItem>
  <TabItem value="pnpm" label="pnpm">

```bash
pnpm add my-package
```

  </TabItem>
</Tabs>
```

### Code Blocks with Features

````mdx
```typescript title="src/config.ts" showLineNumbers
// highlight-next-line
const API_KEY = process.env.API_KEY;

// highlight-start
function getConfig() {
  return {
    apiKey: API_KEY,
    baseUrl: 'https://api.example.com',
  };
}
// highlight-end

export default getConfig;
```
````

### Custom React Component in MDX

```tsx
// src/components/APIEndpoint.tsx
import React from 'react';

interface Props {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
}

export default function APIEndpoint({ method, path, description }: Props) {
  const colors: Record<string, string> = {
    GET: '#61affe',
    POST: '#49cc90',
    PUT: '#fca130',
    DELETE: '#f93e3e',
  };

  return (
    <div style={{
      border: `2px solid ${colors[method]}`,
      borderRadius: 8,
      padding: 16,
      marginBottom: 16,
    }}>
      <span style={{
        backgroundColor: colors[method],
        color: '#fff',
        padding: '2px 8px',
        borderRadius: 4,
        fontWeight: 'bold',
        marginRight: 8,
      }}>
        {method}
      </span>
      <code>{path}</code>
      <p style={{ marginTop: 8, marginBottom: 0 }}>{description}</p>
    </div>
  );
}
```

Usage in MDX:

```mdx
import APIEndpoint from '@site/src/components/APIEndpoint';

<APIEndpoint method="GET" path="/api/users" description="List all users" />
<APIEndpoint method="POST" path="/api/users" description="Create a new user" />
```

## Deployment

### GitHub Pages (with GitHub Actions)

```yaml
# .github/workflows/deploy-docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths: ['docs/**', '.github/workflows/deploy-docs.yml']

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: docs/package-lock.json
      - run: npm ci
        working-directory: docs
      - run: npm run build
        working-directory: docs
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

### Vercel

```json
// vercel.json
{
  "buildCommand": "cd docs && npm run build",
  "outputDirectory": "docs/build",
  "framework": null
}
```

### Netlify

```toml
# netlify.toml
[build]
  base = "docs"
  command = "npm run build"
  publish = "build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Docker

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY docs/ .
RUN npm ci && npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## Swizzling (Theme Customization)

```bash
# List swizzlable components
npx docusaurus swizzle --list

# Eject a component (full control)
npx docusaurus swizzle @docusaurus/theme-classic Footer -- --eject

# Wrap a component (extend behavior)
npx docusaurus swizzle @docusaurus/theme-classic DocItem -- --wrap
```

## Multi-Instance Docs

For separate doc sections (e.g., API docs alongside guides):

```typescript
// docusaurus.config.ts
plugins: [
  [
    '@docusaurus/plugin-content-docs',
    {
      id: 'api-docs',
      path: 'api-docs',
      routeBasePath: 'api',
      sidebarPath: './sidebarsApi.ts',
      editUrl: 'https://github.com/my-org/my-project/tree/main/',
    },
  ],
],
```

## Performance Tips

- Use `@docusaurus/plugin-ideal-image` for automatic image optimization
- Enable `staticDirectories` for assets that bypass webpack
- Use `@docusaurus/faster` (Rspack) for faster builds:

```typescript
// docusaurus.config.ts
future: {
  experimental_faster: true,
},
```
