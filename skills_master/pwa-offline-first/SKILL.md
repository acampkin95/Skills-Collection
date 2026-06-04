---
name: pwa-offline-first
description: PWA and offline-first development with service workers. Use for cache strategies, push notifications, background sync, and app install prompts.
version: 2.0.0
reviewed: "2026-06-04"
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

## References

- [Workbox patterns](references/workbox-patterns.md) — Workbox setup and advanced patterns
- [Push notifications](references/push-notifications.md) — Web Push implementation, iOS 16.4+ support


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.