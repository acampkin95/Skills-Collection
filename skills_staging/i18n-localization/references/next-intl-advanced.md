# Advanced next-intl Patterns

## Async Request Configuration

### Dynamic Message Loading with Splitting

Load only the namespaces needed per route to reduce payload:

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  // Load base messages + route-specific
  const [common, auth] = await Promise.all([
    import(`../../messages/${locale}/common.json`),
    import(`../../messages/${locale}/auth.json`).catch(() => ({}))
  ]);

  return {
    locale,
    messages: {
      ...common.default,
      ...auth.default
    }
  };
});
```

### Per-Route Message Loading

```
messages/
├── en/
│   ├── common.json       # Shared: nav, footer, errors
│   ├── auth.json          # Login, signup, password reset
│   ├── dashboard.json     # Dashboard-specific
│   └── settings.json      # Settings-specific
├── fr/
│   ├── common.json
│   └── ...
```

```tsx
// app/[locale]/dashboard/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getLocale } from 'next-intl/server';

export default async function DashboardLayout({
  children
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = (await import(`@/messages/${locale}/dashboard.json`)).default;

  return (
    <NextIntlClientProvider messages={{ Dashboard: messages }}>
      {children}
    </NextIntlClientProvider>
  );
}
```

---

## Middleware Locale Negotiation

### Standard Middleware

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: [
    // Match all pathnames except API, _next, static files
    '/((?!api|_next|_vercel|.*\\..*).*)'
  ]
};
```

### Custom Locale Detection

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';
import { NextRequest } from 'next/server';

const intlMiddleware = createMiddleware(routing);

export default function middleware(request: NextRequest) {
  // Custom: detect locale from user profile cookie
  const userLocale = request.cookies.get('NEXT_LOCALE')?.value;

  if (userLocale && routing.locales.includes(userLocale as any)) {
    request.headers.set('x-next-intl-locale', userLocale);
  }

  return intlMiddleware(request);
}
```

### Combining with Auth Middleware (e.g., Clerk)

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { routing } from './i18n/routing';

const intlMiddleware = createMiddleware(routing);
const isProtectedRoute = createRouteMatcher([
  '/:locale/dashboard(.*)',
  '/:locale/settings(.*)'
]);

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect();
  }
  return intlMiddleware(request);
});

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)', '/']
};
```

---

## Domain-Based Routing

Map locales to separate domains or subdomains:

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'fr', 'de'],
  defaultLocale: 'en',
  domains: [
    {
      domain: 'example.com',
      defaultLocale: 'en'
    },
    {
      domain: 'example.fr',
      defaultLocale: 'fr'
    },
    {
      domain: 'example.de',
      defaultLocale: 'de'
    }
  ]
});
```

Subdomain pattern:

```ts
export const routing = defineRouting({
  locales: ['en', 'fr', 'de'],
  defaultLocale: 'en',
  domains: [
    { domain: 'en.example.com', defaultLocale: 'en' },
    { domain: 'fr.example.com', defaultLocale: 'fr' },
    { domain: 'de.example.com', defaultLocale: 'de' }
  ]
});
```

---

## Type-Safe Messages

### Generate Types from Messages

```ts
// global.d.ts
import en from './messages/en.json';

type Messages = typeof en;

declare module 'next-intl' {
  interface AppConfig {
    Messages: Messages;
  }
}
```

This gives you autocomplete on `t('...')` keys and compile-time errors for missing keys.

### Strict Namespace Typing

```tsx
// TypeScript will error if 'HomePage.titl' (typo) is used
const t = useTranslations('HomePage');
t('title');  // OK
t('titl');   // Type error: Argument not assignable
```

### Typed Variables

```tsx
// messages/en.json: { "greeting": "Hello, {name}!" }
t('greeting', { name: 'Alex' });  // OK
t('greeting');                     // Type error: missing 'name'
t('greeting', { nme: 'Alex' });   // Type error: unexpected 'nme'
```

---

## Server Actions with Locale

### Pass Locale Through Server Actions

```tsx
// app/[locale]/contact/page.tsx
import { getLocale, getTranslations } from 'next-intl/server';
import { submitContact } from './actions';

export default async function ContactPage() {
  const t = await getTranslations('Contact');
  const locale = await getLocale();

  return (
    <form action={submitContact}>
      <input type="hidden" name="locale" value={locale} />
      <input name="email" placeholder={t('emailPlaceholder')} />
      <textarea name="message" placeholder={t('messagePlaceholder')} />
      <button type="submit">{t('send')}</button>
    </form>
  );
}
```

```ts
// app/[locale]/contact/actions.ts
'use server';

import { getTranslations } from 'next-intl/server';

export async function submitContact(formData: FormData) {
  const locale = formData.get('locale') as string;
  const t = await getTranslations({ locale, namespace: 'Contact' });

  const email = formData.get('email') as string;
  if (!email) {
    return { error: t('errors.emailRequired') };
  }

  // Process submission...
  return { success: t('successMessage') };
}
```

### Locale-Aware Email/Notification Templates

```ts
// lib/notifications.ts
import { getTranslations } from 'next-intl/server';

export async function sendWelcomeEmail(userLocale: string, userName: string) {
  const t = await getTranslations({ locale: userLocale, namespace: 'Emails' });

  const subject = t('welcome.subject');
  const body = t('welcome.body', { name: userName });

  await sendEmail({ subject, body });
}
```

---

## Streaming with i18n

### Suspense-Friendly Translation Loading

```tsx
// app/[locale]/page.tsx
import { Suspense } from 'react';
import { getTranslations } from 'next-intl/server';

export default async function Page() {
  const t = await getTranslations('HomePage');

  return (
    <main>
      <h1>{t('title')}</h1>
      <Suspense fallback={<div>Loading feed...</div>}>
        <ActivityFeed />
      </Suspense>
      <Suspense fallback={<div>Loading stats...</div>}>
        <StatsPanel />
      </Suspense>
    </main>
  );
}

async function ActivityFeed() {
  const t = await getTranslations('Feed');
  const items = await fetchFeedItems(); // slow data fetch

  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>
          {t('activityItem', { user: item.userName, action: item.type })}
        </li>
      ))}
    </ul>
  );
}
```

### Parallel Data + Translation Loading

```tsx
async function ProductPage({ id }: { id: string }) {
  // Load translations and data in parallel
  const [t, product] = await Promise.all([
    getTranslations('Product'),
    fetchProduct(id)
  ]);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{t('inStock', { count: product.stock })}</p>
    </div>
  );
}
```

---

## Locale-Aware Pathname Configuration

### Localized Pathnames

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'fr', 'de'],
  defaultLocale: 'en',
  pathnames: {
    '/': '/',
    '/about': {
      en: '/about',
      fr: '/a-propos',
      de: '/ueber-uns'
    },
    '/products/[slug]': {
      en: '/products/[slug]',
      fr: '/produits/[slug]',
      de: '/produkte/[slug]'
    }
  }
});
```

### Navigation with Localized Paths

```tsx
import { Link } from '@/i18n/routing';

// Automatically resolves to /fr/a-propos when locale is 'fr'
<Link href="/about">About</Link>

// Dynamic routes
<Link href={{ pathname: '/products/[slug]', params: { slug: 'widget' } }}>
  Widget
</Link>
```

---

## Timezone-Aware Formatting

```ts
// i18n/request.ts
export default getRequestConfig(async ({ requestLocale }) => {
  const locale = await requestLocale;

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
    timeZone: 'Europe/London',  // Default timezone
    now: new Date()             // Reference time for relative formatting
  };
});
```

Override per-component:

```tsx
import { useFormatter } from 'next-intl';

function MeetingTime({ date }: { date: Date }) {
  const format = useFormatter();

  return (
    <time>
      {format.dateTime(date, {
        dateStyle: 'long',
        timeStyle: 'short',
        timeZone: 'America/New_York'  // Override for this display
      })}
    </time>
  );
}
```

---

## Error Handling and Fallbacks

### Graceful Fallback Chain

```ts
// i18n/request.ts
export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale ?? 'en';

  let messages;
  try {
    messages = (await import(`../../messages/${locale}.json`)).default;
  } catch {
    // Fallback to English if locale file missing
    console.warn(`Missing messages for locale: ${locale}, falling back to en`);
    messages = (await import('../../messages/en.json')).default;
    locale = 'en';
  }

  return {
    locale,
    messages,
    onError(error) {
      if (error.code === 'MISSING_MESSAGE') {
        // Log but don't crash
        console.warn(error.message);
      }
    },
    getMessageFallback({ namespace, key, error }) {
      // Show key path in development, empty string in production
      if (process.env.NODE_ENV === 'development') {
        return `[${namespace}.${key}]`;
      }
      return '';
    }
  };
});
```
