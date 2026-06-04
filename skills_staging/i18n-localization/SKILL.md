---
name: i18n-localization
description: Internationalization with next-intl v4 for Next.js. Use for ICU MessageFormat, server components, async params, locale routing, and RTL support.
version: 2.0.0
reviewed: "2026-06-04"
---
# Internationalization & Localization with next-intl v4

## Quick Setup

### 1. Install

```bash
npm install next-intl
```

### 2. Define Messages

```
messages/
├── en.json
├── fr.json
└── de.json
```

```json
// messages/en.json
{
  "HomePage": {
    "title": "Welcome to {appName}",
    "description": "Start building your international app"
  },
  "Navigation": {
    "home": "Home",
    "about": "About",
    "settings": "Settings"
  }
}
```

### 3. Request Configuration

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default
  };
});
```

### 4. Routing Configuration

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';
import { createNavigation } from 'next-intl/navigation';

export const routing = defineRouting({
  locales: ['en', 'fr', 'de', 'ar', 'ja'],
  defaultLocale: 'en'
});

export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);
```

### 5. Middleware

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

## References

For advanced topics, see:
- [Advanced next-intl patterns](references/next-intl-advanced.md) — async config, domain routing, type-safe messages, streaming
- [Translation workflows](references/translation-workflow.md) — Crowdin/Lokalise, extraction scripts, machine translation QA
- [RTL support](references/rtl-support.md) — CSS logical properties, bidirectional text, Arabic/Hebrew considerations


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.