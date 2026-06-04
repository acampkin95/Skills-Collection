---
name: pwa-offline-first
description: Progressive Web App and offline-first development with service workers. Use this skill when PWA, service worker, offline, manifest.json, push notifications, cache API, CacheFirst, NetworkFirst, StaleWhileRevalidate. Use this skill when offline detection, background sync, app install prompt, web manifest, service worker lifecycle, precaching, app shell architecture.
---

# PWA & Offline-First Development

Expert guide for service workers, cache strategies, offline-first architecture, and installable web apps.

## Service Worker Lifecycle

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│ Register  │────►│  Install   │────►│ Activate  │
└──────────┘     └───────────┘     └──────────┘
                       │                  │
                  (precache)        (clean old caches)
                       │                  │
                       ▼                  ▼
                 ┌───────────┐     ┌──────────┐
                 │  Waiting   │────►│  Active   │
                 └───────────┘     └──────────┘
                (old SW active)    (handles fetches)
```

## Registration

```javascript
// main.js — Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      });
      console.log('SW registered:', registration.scope);

      // Check for updates periodically
      setInterval(() => registration.update(), 60 * 60 * 1000);
    } catch (error) {
      console.error('SW registration failed:', error);
    }
  });
}
```

## Service Worker (Manual Implementation)

```javascript
// sw.js
const CACHE_NAME = 'app-v1';
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/styles.css',
  '/app.js',
  '/offline.html',
];

// Install — precache critical assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting(); // Activate immediately
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim(); // Take control of all pages
});

// Fetch — apply caching strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls: Network First
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Static assets: Cache First
  if (request.destination === 'image' || request.destination === 'font') {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Pages: Stale While Revalidate
  event.respondWith(staleWhileRevalidate(request));
});
```

## Cache Strategies

```javascript
// Cache First — best for static assets (images, fonts, CSS)
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone());
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

// Network First — best for API calls, dynamic content
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone());
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || new Response(JSON.stringify({ error: 'offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

// Stale While Revalidate — best for pages, non-critical data
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request)
    .then((response) => {
      cache.put(request, response.clone());
      return response;
    })
    .catch(() => cached);

  return cached || fetchPromise;
}
```

### Strategy Selection Guide

| Content Type | Strategy | Why |
|-------------|----------|-----|
| App shell (HTML/CSS/JS) | Cache First | Instant load, update in background |
| Images, fonts | Cache First | Rarely change |
| API data (non-critical) | Stale While Revalidate | Show cached, update silently |
| API data (critical) | Network First | Fresh data preferred, cached fallback |
| User-submitted data | Network Only | Must reach server |
| Offline fallback page | Cache Only | Precached during install |

## Web App Manifest

```json
{
  "name": "My Progressive App",
  "short_name": "MyApp",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4285f4",
  "description": "An offline-capable progressive web app",
  "orientation": "portrait-primary",
  "icons": [
    { "src": "/icons/192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/512.png", "sizes": "512x512", "type": "image/png" },
    {
      "src": "/icons/maskable-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/home.png",
      "sizes": "1080x1920",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],
  "categories": ["productivity", "utilities"]
}
```

```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#4285f4" />
<link rel="apple-touch-icon" href="/icons/192.png" />
```

## Install Prompt

```javascript
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  showInstallButton();
});

async function handleInstallClick() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  console.log(`Install ${outcome}`); // 'accepted' or 'dismissed'
  deferredPrompt = null;
  hideInstallButton();
}

// Detect if already installed
window.addEventListener('appinstalled', () => {
  console.log('App installed');
  hideInstallButton();
});

// Check display mode
const isInstalled = window.matchMedia('(display-mode: standalone)').matches;
```

## Offline Detection & Data Sync

```javascript
// Online/offline status
function updateOnlineStatus() {
  const isOnline = navigator.onLine;
  document.body.classList.toggle('offline', !isOnline);
  if (isOnline) {
    syncPendingActions();
  }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Reliable connectivity check (navigator.onLine can be unreliable)
async function checkConnectivity() {
  try {
    const response = await fetch('/api/ping', {
      method: 'HEAD',
      cache: 'no-store',
    });
    return response.ok;
  } catch {
    return false;
  }
}
```

## Offline Data Sync with IndexedDB

```javascript
// Offline queue using IndexedDB
import { openDB } from 'idb';

const dbPromise = openDB('app-store', 1, {
  upgrade(db) {
    db.createObjectStore('sync-queue', { keyPath: 'id', autoIncrement: true });
    db.createObjectStore('offline-data');
  },
});

// Queue operations when offline
async function queueAction(action) {
  const db = await dbPromise;
  await db.add('sync-queue', {
    action,           // { method: 'POST', url: '/api/items', body: {...} }
    createdAt: Date.now(),
    retries: 0,
  });
}

// Process queue when back online
async function processQueue() {
  const db = await dbPromise;
  const tx = db.transaction('sync-queue', 'readwrite');
  const items = await tx.store.getAll();

  for (const item of items) {
    try {
      await fetch(item.action.url, {
        method: item.action.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.action.body),
      });
      await tx.store.delete(item.id);
    } catch {
      if (item.retries < 5) {
        item.retries++;
        await tx.store.put(item);
      }
    }
  }
}
```

## Background Sync

```javascript
// main.js — Register sync
async function saveDataOffline(data) {
  await idb.put('pending-actions', { data, timestamp: Date.now() });
  const registration = await navigator.serviceWorker.ready;
  await registration.sync.register('sync-pending-data');
}

// sw.js — Handle sync event
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-pending-data') {
    event.waitUntil(syncPendingData());
  }
});

async function syncPendingData() {
  const pendingItems = await idb.getAll('pending-actions');
  for (const item of pendingItems) {
    try {
      await fetch('/api/data', {
        method: 'POST',
        body: JSON.stringify(item.data),
        headers: { 'Content-Type': 'application/json' },
      });
      await idb.delete('pending-actions', item.id);
    } catch {
      throw new Error('Sync failed, will retry');
    }
  }
}
```

## iOS PWA Considerations (2026 Update)

| Feature | Android/Chrome | iOS Safari |
|---------|---------------|------------|
| Service Workers | Full support | Supported (since iOS 11.3) |
| Push Notifications | Yes | Yes (iOS 16.4+, Home Screen only, outside EU) |
| Background Sync | Yes | No (use polling instead) |
| Install Prompt | `beforeinstallprompt` | Manual "Add to Home Screen" only |
| Storage Quota | ~60% of disk | ~50MB per origin (varies) |
| Storage Persistence | `navigator.storage.persist()` | Evicted after ~14 days of inactivity |
| Splash Screen | Via manifest | Requires `apple-touch-startup-image` |
| Display modes | standalone, fullscreen, minimal-ui | standalone only |

```html
<!-- iOS-specific meta tags -->
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="MyApp" />
<link rel="apple-touch-icon" href="/icons/180.png" />

<!-- iOS splash screens (media queries for each device) -->
<link rel="apple-touch-startup-image"
  href="/splash/iphone12.png"
  media="(device-width: 390px) and (device-height: 844px)" />
```

```javascript
// Detect iOS standalone mode
const isIOS = /iphone|ipad|ipod/.test(navigator.userAgent.toLowerCase());
const isStandalone = window.navigator.standalone === true;

if (isIOS && !isStandalone) {
  showIOSInstallBanner("Tap Share then 'Add to Home Screen'");
}
```

## PWA Checklist

- [ ] HTTPS (required for service workers)
- [ ] Web app manifest with name, icons, start_url, display
- [ ] Service worker registered and caching critical assets
- [ ] Offline fallback page
- [ ] Responsive design (viewport meta tag)
- [ ] 192x192 and 512x512 icons
- [ ] Maskable icon for Android adaptive icons
- [ ] theme-color meta tag
- [ ] Lighthouse PWA audit score > 90
- [ ] iOS considerations: push notifications (iOS 16.4+), storage limits (~50MB), cache eviction (~14 days)

---

## References

- [Workbox patterns](references/workbox-patterns.md) — Workbox setup and advanced patterns
- [Push notifications](references/push-notifications.md) — Web Push implementation, iOS 16.4+ support
