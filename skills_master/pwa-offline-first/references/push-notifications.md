# Web Push Notifications

## Overview

```
┌────────┐    Subscribe     ┌──────────────┐
│ Browser │ ──────────────► │ Push Service  │ (FCM, Mozilla, Apple)
│ Client  │ ◄────────────── │ (Web Push)    │
└────────┘    Notification  └──────────────┘
     │                            ▲
     │ Subscription               │ Push Message
     ▼                            │
┌────────┐                  ┌──────────────┐
│  Your   │ ──────────────► │   Your App   │
│ Server  │   Send push     │   Server     │
└────────┘                  └──────────────┘
```

## VAPID Keys

```bash
# Generate VAPID keys
npx web-push generate-vapid-keys

# Output:
# Public Key: BN...
# Private Key: Xs...
```

```env
# .env
VAPID_PUBLIC_KEY=BN...
VAPID_PRIVATE_KEY=Xs...
VAPID_SUBJECT=mailto:admin@example.com
```

## Client-Side: Subscribe

```javascript
// Request permission
async function requestNotificationPermission() {
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    throw new Error('Notification permission denied');
  }
  return permission;
}

// Subscribe to push
async function subscribeToPush() {
  await requestNotificationPermission();

  const registration = await navigator.serviceWorker.ready;

  // Check existing subscription
  let subscription = await registration.pushManager.getSubscription();
  if (subscription) return subscription;

  // Create new subscription
  subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true, // Required: must show notification
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
  });

  // Send subscription to your server
  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription),
  });

  return subscription;
}

// Helper: Convert VAPID key
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

// Unsubscribe
async function unsubscribeFromPush() {
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.getSubscription();
  if (subscription) {
    await subscription.unsubscribe();
    await fetch('/api/push/unsubscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint: subscription.endpoint }),
    });
  }
}
```

## Service Worker: Handle Push Events

```javascript
// sw.js
self.addEventListener('push', (event) => {
  let data = { title: 'New Notification', body: 'You have a new message' };

  if (event.data) {
    try {
      data = event.data.json();
    } catch {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || '/icons/icon-192.png',
    badge: data.badge || '/icons/badge-72.png',
    image: data.image,                          // Large image
    tag: data.tag || 'default',                 // Group by tag (replaces same tag)
    renotify: data.renotify || false,           // Vibrate even if replacing
    requireInteraction: data.requireInteraction || false,
    silent: data.silent || false,
    data: data.data || {},                      // Custom data for click handler
    actions: data.actions || [
      { action: 'open', title: 'Open' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
    vibrate: [200, 100, 200],
    timestamp: data.timestamp || Date.now(),
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const action = event.action;
  const data = event.notification.data;

  if (action === 'dismiss') return;

  // Open or focus the app
  const urlToOpen = data.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Focus existing tab if found
        for (const client of windowClients) {
          if (client.url.includes(urlToOpen) && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new tab
        return clients.openWindow(urlToOpen);
      })
  );
});

// Handle notification close (user dismissed)
self.addEventListener('notificationclose', (event) => {
  // Track dismissals for analytics
  const data = event.notification.data;
  fetch('/api/analytics/notification-dismissed', {
    method: 'POST',
    body: JSON.stringify({ notificationId: data.id }),
    headers: { 'Content-Type': 'application/json' },
  }).catch(() => {}); // Best-effort
});
```

## Server-Side: Send Push

### Node.js with web-push

```bash
npm install web-push
```

```typescript
import webpush from 'web-push';

webpush.setVapidDetails(
  'mailto:admin@example.com',
  process.env.VAPID_PUBLIC_KEY!,
  process.env.VAPID_PRIVATE_KEY!
);

interface PushSubscription {
  endpoint: string;
  keys: { p256dh: string; auth: string };
}

async function sendPush(subscription: PushSubscription, payload: object) {
  try {
    await webpush.sendNotification(
      subscription,
      JSON.stringify(payload),
      {
        TTL: 60 * 60,           // Message expires in 1 hour
        urgency: 'normal',       // 'very-low' | 'low' | 'normal' | 'high'
        topic: 'new-message',    // Replace existing notification with same topic
      }
    );
  } catch (error: any) {
    if (error.statusCode === 410 || error.statusCode === 404) {
      // Subscription expired or invalid — remove from database
      await removeSubscription(subscription.endpoint);
    }
    throw error;
  }
}

// Send to all subscribers
async function broadcastPush(payload: object) {
  const subscriptions = await db.pushSubscriptions.findAll();
  const results = await Promise.allSettled(
    subscriptions.map((sub) => sendPush(sub, payload))
  );
  const failed = results.filter((r) => r.status === 'rejected');
  console.log(`Sent: ${results.length - failed.length}, Failed: ${failed.length}`);
}

// Example payload
await broadcastPush({
  title: 'New Message',
  body: 'You received a message from Alice',
  icon: '/icons/icon-192.png',
  tag: 'message-123',
  data: { url: '/messages/123', id: 'msg-123' },
  actions: [
    { action: 'reply', title: 'Reply' },
    { action: 'open', title: 'Open' },
  ],
});
```

## Notification UX Best Practices

### Permission Timing

```javascript
// BAD: Ask immediately on page load
// Notification.requestPermission(); // ← Users will deny

// GOOD: Ask after user action that indicates interest
document.getElementById('enable-notifications').addEventListener('click', async () => {
  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    await subscribeToPush();
    showSuccessMessage('Notifications enabled!');
  }
});

// BETTER: Show a custom prompt first, then the native prompt
function showCustomPrompt() {
  const banner = document.createElement('div');
  banner.innerHTML = `
    <div class="notification-prompt">
      <p>Get notified about important updates?</p>
      <button id="prompt-yes">Enable</button>
      <button id="prompt-no">Not now</button>
    </div>
  `;
  document.body.appendChild(banner);

  document.getElementById('prompt-yes').onclick = async () => {
    banner.remove();
    const permission = await Notification.requestPermission();
    if (permission === 'granted') await subscribeToPush();
  };

  document.getElementById('prompt-no').onclick = () => {
    banner.remove();
    // Remember choice, don't ask again for 30 days
    localStorage.setItem('notification-prompt-dismissed', Date.now().toString());
  };
}
```

### Content Guidelines

- **Be specific**: "Alice sent you a message" not "You have a notification"
- **Be actionable**: Include clear actions the user can take
- **Be timely**: Don't send outdated notifications
- **Be respectful**: Limit frequency (max 3-5 per day for most apps)
- **Use tags**: Group related notifications to avoid spamming
- **Set TTL**: Notifications for time-sensitive events should expire

### Frequency Capping

```typescript
async function shouldSendPush(userId: string): Promise<boolean> {
  const recentCount = await db.pushLog.count({
    userId,
    sentAt: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) },
  });
  return recentCount < 5; // Max 5 per day
}
```
