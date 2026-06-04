# Nextra v3+ Setup Reference (App Router)

## Quick Start

```bash
# Create Next.js project
npx create-next-app@latest my-docs --typescript --app
cd my-docs

# Install Nextra v3 with docs theme
npm install nextra nextra-theme-docs
```

## Project Structure (App Router)

```
my-docs/
├── app/
│   ├── layout.tsx            # Root layout with Nextra provider
│   ├── page.mdx              # Homepage
│   ├── docs/
│   │   ├── _meta.ts          # Navigation config
│   │   ├── getting-started.mdx
│   │   ├── guides/
│   │   │   ├── _meta.ts
│   │   │   ├── authentication.mdx
│   │   │   └── deployment.mdx
│   │   └── api-reference/
│   │       ├── _meta.ts
│   │       └── client.mdx
│   └── blog/
│       ├── _meta.ts
│       └── first-post.mdx
├── components/
│   └── CustomComponent.tsx
├── public/
│   └── og-image.png
├── next.config.mjs
├── theme.config.tsx
├── mdx-components.tsx         # MDX components (App Router)
└── tsconfig.json
```

## next.config.mjs (Nextra v3)

```javascript
import nextra from 'nextra';

const withNextra = nextra({
  // Theme to use
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',

  // Options
  defaultShowCopyCode: true,
  staticImage: true,
  flexsearch: {
    codeblocks: true,
  },
  latex: true,

  // Custom MDX options
  mdxOptions: {
    remarkPlugins: [],
    rehypePlugins: [],
  },
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',      // Optional: static export
  images: {
    unoptimized: true,    // Required for static export
  },
  reactStrictMode: true,
};

export default withNextra(nextConfig);
```

## theme.config.tsx (Full Configuration)

```tsx
import type { DocsThemeConfig } from 'nextra-theme-docs';
import { useRouter } from 'next/router';

const config: DocsThemeConfig = {
  // Branding
  logo: (
    <>
      <svg width="24" height="24" viewBox="0 0 24 24">
        {/* Logo SVG */}
      </svg>
      <span style={{ marginLeft: '.4em', fontWeight: 800 }}>
        My Project
      </span>
    </>
  ),
  logoLink: '/',

  // Repository
  project: {
    link: 'https://github.com/my-org/my-project',
  },
  docsRepositoryBase: 'https://github.com/my-org/my-project/tree/main',

  // Navigation
  sidebar: {
    defaultMenuCollapseLevel: 1,
    toggleButton: true,
    autoCollapse: true,
  },
  toc: {
    float: true,
    title: 'On This Page',
    extraContent: null,
    backToTop: true,
  },

  // Interaction
  feedback: {
    content: 'Question? Give us feedback →',
    labels: 'feedback',
    useLink: () => 'https://github.com/my-org/my-project/issues/new',
  },
  editLink: {
    text: 'Edit this page on GitHub →',
  },

  // Footer
  footer: {
    text: (
      <span>
        MIT {new Date().getFullYear()} ©{' '}
        <a href="https://my-org.com" target="_blank" rel="noreferrer">
          My Org
        </a>
      </span>
    ),
  },

  // SEO
  head: () => {
    return (
      <>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta property="og:title" content="My Project Docs" />
        <meta property="og:description" content="Documentation for My Project" />
        <link rel="icon" href="/favicon.ico" />
      </>
    );
  },
  useNextSeoProps() {
    const { asPath } = useRouter();
    if (asPath !== '/') {
      return { titleTemplate: '%s – My Project' };
    }
    return { title: 'My Project – Documentation' };
  },

  // Appearance
  primaryHue: 210,
  primarySaturation: 100,
  darkMode: true,
  nextThemes: {
    defaultTheme: 'system',
  },

  // Navigation links
  navbar: {
    extraContent: null,
  },

  // Banner
  banner: {
    key: 'v3-release',
    text: (
      <a href="/blog/v3" target="_blank" rel="noreferrer">
        v3.0 is released. Read more →
      </a>
    ),
    dismissible: true,
  },

  // Search placeholder
  search: {
    placeholder: 'Search documentation...',
  },

  // Git timestamp
  gitTimestamp: ({ timestamp }) => {
    return <>Last updated on {timestamp.toLocaleDateString()}</>;
  },
};

export default config;
```

## _meta.ts Navigation

### Root Level (app/docs/_meta.ts)

```typescript
export default {
  index: 'Introduction',
  'getting-started': 'Getting Started',
  '---': {
    type: 'separator',
    title: 'Guides',
  },
  guides: {
    title: 'Guides',
    type: 'menu',
    items: {
      authentication: { title: 'Authentication' },
      deployment: { title: 'Deployment' },
    },
  },
  'api-reference': 'API Reference',
  '-- ': {      // Unique key for second separator
    type: 'separator',
  },
  changelog: {
    title: 'Changelog',
    theme: {
      breadcrumb: false,
      footer: true,
      sidebar: true,
      toc: true,
      pagination: false,
      timestamp: true,
      typesetting: 'article',
    },
  },
  contact: {
    title: 'Contact Us ↗',
    type: 'page',
    href: 'https://example.com/contact',
    newWindow: true,
  },
};
```

### _meta.json Alternative (Simpler)

```json
{
  "index": "Introduction",
  "getting-started": "Getting Started",
  "---": {
    "type": "separator",
    "title": "Guides"
  },
  "authentication": "Authentication",
  "deployment": "Deployment",
  "api-reference": "API Reference"
}
```

### Nested Directory (app/docs/guides/_meta.ts)

```typescript
export default {
  authentication: 'Authentication',
  'data-fetching': 'Data Fetching',
  deployment: 'Deployment',
  advanced: {
    title: 'Advanced',
    // Override page theme for this section
    theme: {
      collapsed: false,
      layout: 'full',
    },
  },
};
```

## App Router Layout

### Root Layout (app/layout.tsx)

```tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import 'nextra-theme-docs/style.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'My Project',
    template: '%s – My Project',
  },
  description: 'Documentation for My Project',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

### mdx-components.tsx (App Router requirement)

```tsx
import { useMDXComponents as getDocsMDXComponents } from 'nextra-theme-docs';

const docsComponents = getDocsMDXComponents();

export function useMDXComponents(components: Record<string, React.FC>) {
  return {
    ...docsComponents,
    ...components,
  };
}
```

## MDX Page Frontmatter

```mdx
---
title: Authentication Guide
description: Learn how to add authentication to your app
searchable: true
---

# Authentication Guide

Content starts here...
```

## Built-in Components

### Callout

```mdx
import { Callout } from 'nextra/components';

<Callout type="info">
  This is an informational callout.
</Callout>

<Callout type="warning">
  Be careful with this operation.
</Callout>

<Callout type="error">
  This action is destructive and cannot be undone.
</Callout>

<Callout type="default" emoji="💡">
  Custom emoji callout with helpful tip.
</Callout>
```

### Tabs

```mdx
import { Tabs } from 'nextra/components';

<Tabs items={['npm', 'yarn', 'pnpm']}>
  <Tabs.Tab>
    ```bash
    npm install my-package
    ```
  </Tabs.Tab>
  <Tabs.Tab>
    ```bash
    yarn add my-package
    ```
  </Tabs.Tab>
  <Tabs.Tab>
    ```bash
    pnpm add my-package
    ```
  </Tabs.Tab>
</Tabs>
```

### Steps

```mdx
import { Steps } from 'nextra/components';

<Steps>
### Install the package

```bash
npm install my-package
```

### Configure your project

Create a `config.ts` file:

```typescript
export const config = {
  apiKey: process.env.API_KEY,
};
```

### Start developing

```bash
npm run dev
```
</Steps>
```

### File Tree

```mdx
import { FileTree } from 'nextra/components';

<FileTree>
  <FileTree.Folder name="src" defaultOpen>
    <FileTree.Folder name="components">
      <FileTree.File name="Button.tsx" />
      <FileTree.File name="Card.tsx" />
    </FileTree.Folder>
    <FileTree.Folder name="pages">
      <FileTree.File name="index.tsx" />
      <FileTree.File name="about.tsx" />
    </FileTree.Folder>
    <FileTree.File name="app.tsx" />
  </FileTree.Folder>
  <FileTree.File name="package.json" />
  <FileTree.File name="tsconfig.json" />
</FileTree>
```

### Cards

```mdx
import { Cards, Card } from 'nextra/components';

<Cards>
  <Card
    title="Getting Started"
    href="/docs/getting-started"
    icon={<svg>...</svg>}
  />
  <Card
    title="API Reference"
    href="/docs/api-reference"
    icon={<svg>...</svg>}
  />
  <Card
    title="Examples"
    href="/docs/examples"
    icon={<svg>...</svg>}
  />
</Cards>
```

## Flexsearch (Built-in Search)

Flexsearch is enabled by default. Configure in `next.config.mjs`:

```javascript
const withNextra = nextra({
  flexsearch: {
    codeblocks: true,   // Index code blocks
  },
  // Or disable entirely:
  // flexsearch: false,
});
```

### Custom Search Component

```tsx
// components/CustomSearch.tsx
import { useSearch } from 'nextra/hooks';

export function CustomSearch() {
  const { query, setQuery, results } = useSearch();

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search docs..."
      />
      <ul>
        {results.map((result) => (
          <li key={result.id}>
            <a href={result.route}>{result.title}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Custom MDX Components

### Register Global Components

```tsx
// mdx-components.tsx
import { useMDXComponents as getDocsMDXComponents } from 'nextra-theme-docs';
import { APIEndpoint } from './components/APIEndpoint';
import { VersionBadge } from './components/VersionBadge';
import { Demo } from './components/Demo';

const docsComponents = getDocsMDXComponents();

export function useMDXComponents(components: Record<string, React.FC>) {
  return {
    ...docsComponents,
    ...components,
    // These are available in all MDX files without importing
    APIEndpoint,
    VersionBadge,
    Demo,
  };
}
```

### Usage in MDX (no import needed)

```mdx
# API Client

<VersionBadge version="2.0" />

<APIEndpoint method="GET" path="/api/users" />

<Demo src="https://stackblitz.com/edit/my-demo" />
```

## Advanced Features

### Remote Content (fetch MDX at build time)

```tsx
// app/docs/remote/page.tsx
import { compileMdx } from 'nextra/compile';

export default async function RemotePage() {
  const response = await fetch('https://raw.githubusercontent.com/.../README.md');
  const markdown = await response.text();
  const { result } = await compileMdx(markdown);
  return result;
}
```

### Custom 404 Page

```tsx
// app/not-found.tsx
export default function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '100px 0' }}>
      <h1>404 - Page Not Found</h1>
      <p>The page you are looking for does not exist.</p>
      <a href="/">Go back home</a>
    </div>
  );
}
```

### Static Export & Deployment

```bash
# Build static site
npm run build
# Output in /out directory (with output: 'export' in next.config.mjs)

# Deploy to Vercel (zero config)
npx vercel

# Deploy to Netlify
# netlify.toml:
# [build]
#   command = "npm run build"
#   publish = "out"

# Deploy to GitHub Pages
# Set basePath in next.config.mjs if not at root:
# basePath: '/my-project'
```

### Theme Overrides with CSS

```css
/* app/globals.css or custom CSS file */

:root {
  --nextra-primary-hue: 210deg;
  --nextra-primary-saturation: 100%;
}

.dark {
  --nextra-primary-hue: 210deg;
  --nextra-primary-saturation: 80%;
}

/* Override sidebar width */
.nextra-sidebar-container {
  width: 280px;
}

/* Custom content max-width */
.nextra-content main {
  max-width: 900px;
}
```

## i18n (Internationalization)

```javascript
// next.config.mjs
const withNextra = nextra({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
});

export default withNextra({
  i18n: {
    locales: ['en', 'ja', 'fr'],
    defaultLocale: 'en',
  },
});
```

Directory structure:

```
app/
├── en/
│   └── docs/
│       ├── _meta.ts
│       └── getting-started.mdx
├── ja/
│   └── docs/
│       ├── _meta.ts
│       └── getting-started.mdx
└── fr/
    └── docs/
        ├── _meta.ts
        └── getting-started.mdx
```
