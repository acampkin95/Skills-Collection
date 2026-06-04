---
name: i18n-localization
description: Use this skill when i18n, internationalization, localization, next-intl, translations, locale, pluralization, RTL, language routing. Expert guidance on next-intl v4 setup, ICU MessageFormat, server components, async params, and translation workflows.
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

export const config = {
  matcher: ['/', '/(fr|de|ar|ja)/:path*']
};
```

### 6. Layout with Provider (Async params)

```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

### 7. next.config

```ts
// next.config.ts
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

const nextConfig = {};
export default withNextIntl(nextConfig);
```

---

## ICU MessageFormat

next-intl uses ICU MessageFormat syntax for all message interpolation.

### Variables

```json
{ "greeting": "Hello, {name}!" }
```

```tsx
t('greeting', { name: 'Alex' })  // "Hello, Alex!"
```

### Plurals

```json
{
  "items": "You have {count, plural, =0 {no items} one {# item} other {# items}} in your cart."
}
```

```tsx
t('items', { count: 0 })   // "You have no items in your cart."
t('items', { count: 1 })   // "You have 1 item in your cart."
t('items', { count: 5 })   // "You have 5 items in your cart."
```

### Select

```json
{
  "status": "{role, select, admin {Full access granted} editor {Edit access granted} other {View-only access}}"
}
```

```tsx
t('status', { role: 'admin' })   // "Full access granted"
t('status', { role: 'viewer' })  // "View-only access"
```

### Selectordinal

```json
{
  "place": "You finished in {pos, selectordinal, one {#st} two {#nd} few {#rd} other {#th}} place."
}
```

```tsx
t('place', { pos: 1 })  // "You finished in 1st place."
t('place', { pos: 3 })  // "You finished in 3rd place."
```

### Nested Select + Plural

```json
{
  "inbox": "{gender, select, female {{count, plural, one {She has # message} other {She has # messages}}} male {{count, plural, one {He has # message} other {He has # messages}}} other {{count, plural, one {They have # message} other {They have # messages}}}}"
}
```

### Rich Text (Tags in Messages)

```json
{
  "terms": "By signing up you agree to our <link>Terms of Service</link> and <bold>Privacy Policy</bold>."
}
```

```tsx
t.rich('terms', {
  link: (chunks) => <a href="/terms">{chunks}</a>,
  bold: (chunks) => <strong>{chunks}</strong>
});
```

---

## Server Component i18n

Server Components use the async `getTranslations` API.

```tsx
// app/[locale]/page.tsx
import { getTranslations } from 'next-intl/server';

export default async function HomePage() {
  const t = await getTranslations('HomePage');

  return (
    <main>
      <h1>{t('title', { appName: 'Acme' })}</h1>
      <p>{t('description')}</p>
    </main>
  );
}
```

### Generate Metadata (Async params)

```tsx
import { getTranslations } from 'next-intl/server';

export async function generateMetadata({
  params
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'HomePage' });

  return {
    title: t('title', { appName: 'Acme' }),
    description: t('description')
  };
}
```

### Static Params for All Locales

```tsx
import { routing } from '@/i18n/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}
```

---

## Client Component i18n

Client Components use the synchronous `useTranslations` hook.

```tsx
'use client';

import { useTranslations } from 'next-intl';

export function Counter() {
  const t = useTranslations('Counter');
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>{t('count', { value: count })}</p>
      <button onClick={() => setCount(count + 1)}>
        {t('increment')}
      </button>
    </div>
  );
}
```

### Reduce Client Bundle — Namespace Scoping

Only send required namespaces to client components:

```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { pick } from 'lodash';

export default async function Layout({ children }: { children: React.ReactNode }) {
  const messages = await getMessages();

  return (
    <NextIntlClientProvider messages={pick(messages, ['Navigation', 'Footer'])}>
      {children}
    </NextIntlClientProvider>
  );
}
```

---

## Date, Number, and Currency Formatting

Use `useFormatter` (client) or `getFormatter` (server) from next-intl:

```tsx
import { useFormatter } from 'next-intl';

function Formatted({ date, amount }: { date: Date; amount: number }) {
  const format = useFormatter();

  return (
    <div>
      {/* Dates */}
      <p>{format.dateTime(date, { dateStyle: 'full' })}</p>
      <p>{format.relativeTime(date)}</p>

      {/* Numbers */}
      <p>{format.number(amount, { style: 'percent' })}</p>
      <p>{format.number(amount, { notation: 'compact' })}</p>

      {/* Currency */}
      <p>{format.number(amount, {
        style: 'currency', currency: 'USD', currencyDisplay: 'narrowSymbol'
      })}</p>
    </div>
  );
}
```

Server-side: `const format = await getFormatter();` (from `next-intl/server`).

### Global Named Formats

```ts
// In i18n/request.ts return object:
formats: {
  dateTime: {
    short: { day: 'numeric', month: 'short', year: 'numeric' }
  },
  number: {
    price: { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }
  }
}
// Usage: format.dateTime(date, 'short') or format.number(price, 'price')
```

---

## Locale Detection & Switching

### Locale Switcher Component

```tsx
'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '@/i18n/routing';

const localeLabels: Record<string, string> = {
  en: 'English',
  fr: 'Francais',
  de: 'Deutsch',
  ar: 'العربية',
  ja: '日本語'
};

export function LocaleSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  function onChange(nextLocale: string) {
    router.replace(pathname, { locale: nextLocale });
  }

  return (
    <select value={locale} onChange={(e) => onChange(e.target.value)}>
      {Object.entries(localeLabels).map(([code, label]) => (
        <option key={code} value={code}>{label}</option>
      ))}
    </select>
  );
}
```

---

## Message Organization

Namespace by feature in a single JSON per locale. Use nested objects for grouping:

```json
{
  "Auth": { "login": "Log in", "signup": "Sign up",
    "errors": { "invalidEmail": "Please enter a valid email" } },
  "Dashboard": { "welcome": "Welcome back, {name}",
    "stats": { "items": "You have {count, plural, one {# item} other {# items}}" } },
  "OrderStatus": { "pending": "Order pending", "shipped": "Shipped", "delivered": "Delivered" }
}
```

Dynamic enum keys: `const t = useTranslations('OrderStatus'); t(order.status);`

---

## Common Patterns

### Handling Missing Translations

Use `onError` callback in request config to handle MISSING_MESSAGE code. Provide `getMessageFallback` to return a fallback (e.g., `${namespace}.${key}`) when translations are unavailable. See `references/next-intl-advanced.md` for advanced error handling patterns.

### Plurals for Multiple Languages

Different languages have different plural categories. ICU handles this automatically:

| Language | Categories |
|----------|-----------|
| English  | one, other |
| French   | one, many, other |
| Arabic   | zero, one, two, few, many, other |
| Japanese | other (no plurals) |
| Polish   | one, few, many, other |

Always provide `other` as the fallback category.

### SEO: Alternate hreflang Tags

```tsx
// app/[locale]/layout.tsx
import { routing } from '@/i18n/routing';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;

  return {
    alternates: {
      languages: Object.fromEntries(
        routing.locales.map((l) => [l, `/${l}`])
      )
    }
  };
}
```

---

## References

For advanced topics, see:
- [Advanced next-intl patterns](references/next-intl-advanced.md) — async config, domain routing, type-safe messages, streaming
- [Translation workflows](references/translation-workflow.md) — Crowdin/Lokalise, extraction scripts, machine translation QA
- [RTL support](references/rtl-support.md) — CSS logical properties, bidirectional text, Arabic/Hebrew considerations
