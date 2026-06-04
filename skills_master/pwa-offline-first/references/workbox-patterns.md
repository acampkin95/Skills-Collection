# Workbox Patterns

## Setup Methods

### Workbox Build Plugin (Webpack)

```bash
npm install workbox-webpack-plugin --save-dev
```

```javascript
// webpack.config.js
const { GenerateSW, InjectManifest } = require('workbox-webpack-plugin');

module.exports = {
  plugins: [
    // Option 1: Auto-generate service worker
    new GenerateSW({
      clientsClaim: true,
      skipWaiting: true,
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/api\.example\.com/,
          handler: 'NetworkFirst',
          options: {
            cacheName: 'api-cache',
            expiration: { maxEntries: 50, maxAgeSeconds: 300 },
          },
        },
      ],
    }),

    // Option 2: Custom service worker with injected manifest
    new InjectManifest({
      swSrc: './src/sw.js',
      swDest: 'sw.js',
    }),
  ],
};
```

### Workbox CLI

```bash
npx workbox-cli wizard
# Generates workbox-config.js

npx workbox-cli generateSW workbox-config.js
# or
npx workbox-cli injectManifest workbox-config.js
```

### Workbox CDN (Quick Start)

```javascript
// sw.js
importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');

const { registerRoute } = workbox.routing;
const { CacheFirst, NetworkFirst, StaleWhileRevalidate } = workbox.strategies;
const { ExpirationPlugin } = workbox.expiration;
const { precacheAndRoute } = workbox.precaching;

// Precache build assets (injected by build tool)
precacheAndRoute(self.__WB_MANIFEST || []);
```

## Routing Strategies

```javascript
import { registerRoute, NavigationRoute, Route } from 'workbox-routing';
import { CacheFirst, NetworkFirst, StaleWhileRevalidate, NetworkOnly } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';
import { precacheAndRoute } from 'workbox-precaching';

// Precache build output
precacheAndRoute(self.__WB_MANIFEST);

// Images — Cache First (long-lived)
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
    plugins: [
      new ExpirationPlugin({ maxEntries: 100, maxAgeSeconds: 30 * 24 * 60 * 60 }),
      new CacheableResponsePlugin({ statuses: [0, 200] }),
    ],
  })
);

// API calls — Network First
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-responses',
    plugins: [
      new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 5 * 60 }),
    ],
    networkTimeoutSeconds: 3,  // Fall back to cache after 3s
  })
);

// Google Fonts — Cache First
registerRoute(
  ({ url }) => url.origin === 'https://fonts.googleapis.com' ||
               url.origin === 'https://fonts.gstatic.com',
  new CacheFirst({
    cacheName: 'google-fonts',
    plugins: [
      new ExpirationPlugin({ maxEntries: 30, maxAgeSeconds: 365 * 24 * 60 * 60 }),
    ],
  })
);

// JS/CSS — Stale While Revalidate
registerRoute(
  ({ request }) => request.destination === 'script' || request.destination === 'style',
  new StaleWhileRevalidate({
    cacheName: 'static-resources',
  })
);

// Navigation (HTML pages) — Network First with offline fallback
import { setCatchHandler } from 'workbox-routing';

registerRoute(
  new NavigationRoute(
    new NetworkFirst({ cacheName: 'pages', networkTimeoutSeconds: 3 })
  )
);

// Fallback for failed navigations
setCatchHandler(async ({ event }) => {
  if (event.request.destination === 'document') {
    return caches.match('/offline.html');
  }
  return Response.error();
});
```

## Precaching

```javascript
import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';

// Auto-injected by build tool
precacheAndRoute(self.__WB_MANIFEST);

// Clean up old precaches on activate
cleanupOutdatedCaches();

// Manual precache list (if not using build tool)
precacheAndRoute([
  { url: '/index.html', revision: 'abc123' },
  { url: '/styles.css', revision: 'def456' },
  { url: '/app.js', revision: 'ghi789' },
  '/offline.html',
]);
```

## Cache Expiration

```javascript
import { ExpirationPlugin } from 'workbox-expiration';

// By count
new ExpirationPlugin({ maxEntries: 50 })

// By age
new ExpirationPlugin({ maxAgeSeconds: 7 * 24 * 60 * 60 }) // 7 days

// Both (either triggers cleanup)
new ExpirationPlugin({
  maxEntries: 100,
  maxAgeSeconds: 30 * 24 * 60 * 60,
  purgeOnQuotaError: true,  // Auto-purge if storage quota exceeded
})
```

## Background Sync

```javascript
import { BackgroundSyncPlugin } from 'workbox-background-sync';
import { NetworkOnly } from 'workbox-strategies';

// Queue failed POST requests and retry when online
registerRoute(
  ({ url }) => url.pathname === '/api/submit',
  new NetworkOnly({
    plugins: [
      new BackgroundSyncPlugin('submit-queue', {
        maxRetentionTime: 24 * 60, // Retry for 24 hours (in minutes)
        onSync: async ({ queue }) => {
          let entry;
          while ((entry = await queue.shiftRequest())) {
            try {
              await fetch(entry.request);
            } catch (error) {
              await queue.unshiftRequest(entry);
              throw error;
            }
          }
        },
      }),
    ],
  }),
  'POST'
);
```

## Workbox Recipes (Pre-built Patterns)

```javascript
import { offlineFallback, pageCache, imageCache, staticResourceCache, googleFontsCache } from 'workbox-recipes';

// All-in-one setup
pageCache();                // Network-first HTML
staticResourceCache();      // Stale-while-revalidate JS/CSS
imageCache();              // Cache-first images
googleFontsCache();        // Cache-first fonts
offlineFallback({
  pageFallback: '/offline.html',
  imageFallback: '/images/offline-placeholder.png',
});
```

## Next.js PWA Setup (next-pwa)

```bash
npm install @ducanh2912/next-pwa
```

```javascript
// next.config.mjs
import withPWA from '@ducanh2912/next-pwa';

const nextConfig = withPWA({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\.example\.com\/.*/i,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        expiration: {
          maxEntries: 32,
          maxAgeSeconds: 24 * 60 * 60,
        },
      },
    },
    {
      urlPattern: /\.(?:jpg|jpeg|gif|png|svg|ico|webp)$/i,
      handler: 'CacheFirst',
      options: {
        cacheName: 'static-image-assets',
        expiration: {
          maxEntries: 64,
          maxAgeSeconds: 30 * 24 * 60 * 60,
        },
      },
    },
  ],
})({
  // Normal Next.js config
  reactStrictMode: true,
});

export default nextConfig;
```

```json
// public/manifest.json
{
  "name": "My Next.js App",
  "short_name": "MyApp",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#000000",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

```tsx
// app/layout.tsx
export const metadata = {
  manifest: '/manifest.json',
  themeColor: '#000000',
};
```
