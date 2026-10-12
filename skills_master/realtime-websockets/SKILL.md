---
name: realtime-websockets
description: "Designs live data synchronisation between a client and server using WebSockets, Server-Sent Events (SSE) and HTTP polling, including reconnection with backoff, heartbeats, authentication, presence, Socket.IO and horizontal scaling. Use when building live updates, chat, notifications, live dashboards or collaboration features, choosing between WebSocket, SSE and polling, or fixing a dropped or reconnecting real-time connection."
version: "1.0.0"
reviewed: "2026-10-12"
---

# Real-Time Communication Patterns

Use this skill when building applications requiring **live data synchronization** between client and server. Covers WebSocket protocols, Server-Sent Events (SSE), HTTP polling, reconnection strategies, authentication, and horizontal scaling.

## Response Protocol

1. Identify the real-time requirement (frequency, latency, reliability)
2. Recommend protocol: WebSocket (bidirectional), SSE (server→client), or polling (fallback)
3. Load reference files for implementation details (see below)
4. Provide code patterns for the chosen protocol
5. Address scaling and production concerns

## Reference Files (Load When Needed)

| File | When to Load |
|------|--------------|
| `references/sse-patterns.md` | Server-Sent Events patterns |
| `references/socketio-patterns.md` | Socket.IO patterns |
| `references/presence-sync.md` | Presence tracking and state synchronisation |
| Protocol selection, WebSocket implementation details, HTTP polling fallback, horizontal scaling with Redis Pub/Sub | Not bundled with this skill; use the decision matrix and the patterns below |

---

## Protocol Selection Decision Matrix

| Protocol | Latency | Bandwidth | Complexity | Browser Support | Use Case |
|----------|---------|-----------|-----------|-----------------|----------|
| **WebSocket** | <100ms | Low | High | Excellent (97%+) | Chat, multiplayer, live collaboration |
| **SSE** | 100-500ms | Low | Low | Good (95%+) | Notifications, live feeds, server updates |
| **HTTP Polling** | 1-5s | High | Very Low | Excellent (100%) | Fallback, legacy browsers, simple updates |

---

## Key Concepts

### Reconnection Strategy

```javascript
class ReconnectingWebSocket {
  constructor(url, maxRetries = 5) {
    this.url = url;
    this.maxRetries = maxRetries;
    this.retryCount = 0;
    this.retryDelay = 1000;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => this.onOpen();
      this.ws.onclose = () => this.onClose();
      this.ws.onerror = (err) => this.onError(err);
    } catch (err) {
      this.scheduleReconnect();
    }
  }

  onClose() {
    if (this.retryCount < this.maxRetries) {
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    const delay = this.retryDelay * Math.pow(2, this.retryCount);
    setTimeout(() => {
      this.retryCount++;
      this.connect();
    }, Math.min(delay, 30000)); // Cap at 30s
  }

  onOpen() {
    this.retryCount = 0;
    this.retryDelay = 1000;
  }

  onError(err) {
    console.error('WebSocket error:', err);
  }
}
```

### Heartbeat Pattern

```javascript
// Server: Send ping every 30s
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
}, 30000);

// Client: Respond to ping with pong
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'ping') {
    ws.send(JSON.stringify({ type: 'pong', timestamp: msg.timestamp }));
  }
};
```

### Authentication

```javascript
// Token in query string (tokens in URLs can appear in server and proxy logs; prefer the message below or a short-lived ticket)
const ws = new WebSocket(`wss://api.example.com/stream?token=${authToken}`);

// OR: Send auth message immediately after connection
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'authenticate',
    token: authToken
  }));
};
```

---

## Common Patterns

| Pattern | Description | When to Use |
|---------|-------------|------------|
| **Pub/Sub** | Multiple clients subscribe to topics | Chat rooms, event broadcasting |
| **Request/Response** | Client sends request, server responds | Real-time queries, command execution |
| **Stream** | Continuous data flow (time-series, sensor data) | Live dashboards, monitoring |
| **Presence** | Track who is connected/online | Collaboration tools, status displays |

---

## Production Considerations

- **Load Balancing**: Use sticky sessions or Redis-backed message brokers
- **Monitoring**: Track connection count, message throughput, error rates
- **Rate Limiting**: Prevent client message flooding
- **Data Validation**: Sanitize all incoming messages
- **Compression**: Enable WebSocket compression for large payloads

---

## Resources

| Resource | URL |
|----------|-----|
| **MDN WebSocket API** | https://developer.mozilla.org/en-US/docs/Web/API/WebSocket |
| **Server-Sent Events** | https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events |
| **Socket.IO** | https://socket.io/ |
| **ws (Node.js)** | https://github.com/websockets/ws |
