# Server-Sent Events (SSE) Patterns

## EventSource API (Browser)

```typescript
// Basic usage
const source = new EventSource('/api/events');

source.onopen = () => console.log('SSE connected');

// Default "message" event
source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};

// Custom named events
source.addEventListener('notification', (event) => {
  const data = JSON.parse(event.data);
  showNotification(data);
});

source.addEventListener('heartbeat', () => {
  console.log('Server alive');
});

source.onerror = (event) => {
  if (source.readyState === EventSource.CLOSED) {
    console.log('SSE closed by server');
  } else {
    console.log('SSE error, will auto-reconnect');
    // EventSource auto-reconnects with Last-Event-ID header
  }
};

// Close when done
source.close();
```

### EventSource with Auth (fetch-based)

`EventSource` does not support custom headers. Use `fetch` for authenticated SSE:

```typescript
async function authenticatedSSE(url: string, token: string) {
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'text/event-stream',
    },
  });

  if (!response.ok) throw new Error(`SSE failed: ${response.status}`);

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop()!; // Keep incomplete line in buffer

    let eventType = 'message';
    let eventData = '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.slice(7);
      } else if (line.startsWith('data: ')) {
        eventData += line.slice(6);
      } else if (line === '' && eventData) {
        // Empty line = end of event
        handleEvent(eventType, JSON.parse(eventData));
        eventType = 'message';
        eventData = '';
      }
    }
  }
}
```

## SSE Protocol Format

The wire format is plain text:

```
event: notification\n
data: {"title":"New message","body":"Hello"}\n
id: msg-42\n
retry: 5000\n
\n
```

| Field | Purpose |
|-------|---------|
| `data:` | Event payload (required). Multi-line: repeat `data:` per line |
| `event:` | Custom event name. Omit for default `message` event |
| `id:` | Event ID. Browser sends `Last-Event-ID` header on reconnect |
| `retry:` | Reconnection delay in ms. Browser respects this |

## Next.js Streaming Responses

### App Router (Route Handler)

```typescript
// app/api/events/route.ts
export const runtime = 'nodejs'; // SSE needs Node.js runtime

export async function GET(request: Request) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      // Helper to send SSE events
      function send(event: string, data: unknown) {
        controller.enqueue(
          encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)
        );
      }

      // Send initial data
      send('connected', { status: 'ok' });

      // Periodic heartbeat
      const heartbeat = setInterval(() => {
        send('heartbeat', { ts: Date.now() });
      }, 15000);

      // Simulate real-time updates
      for (let i = 0; i < 10; i++) {
        await new Promise((r) => setTimeout(r, 1000));
        send('update', { count: i, timestamp: Date.now() });
      }

      // Cleanup on client disconnect
      request.signal.addEventListener('abort', () => {
        clearInterval(heartbeat);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no', // Disable nginx buffering
    },
  });
}
```

### Server Component Streaming (React Suspense)

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<p>Loading metrics...</p>}>
        <SlowMetrics />
      </Suspense>
      <Suspense fallback={<p>Loading chart...</p>}>
        <SlowChart />
      </Suspense>
    </div>
  );
}

async function SlowMetrics() {
  const data = await fetch('https://api.example.com/metrics', {
    next: { revalidate: 10 },
  });
  const metrics = await data.json();
  return <MetricsGrid data={metrics} />;
}
```

## AI Streaming Patterns (ChatGPT-style)

### Server: Stream AI Response

```typescript
// app/api/chat/route.ts
import OpenAI from 'openai';

const openai = new OpenAI();

export async function POST(request: Request) {
  const { messages } = await request.json();
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o',
        messages,
        stream: true,
      });

      for await (const chunk of completion) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          // Send each token as an SSE event
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ content })}\n\n`)
          );
        }
      }

      // Signal completion
      controller.enqueue(encoder.encode('data: [DONE]\n\n'));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  });
}
```

### Client: Consume AI Stream

```typescript
'use client';
import { useState, useCallback } from 'react';

export function useAIStream() {
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = useCallback(async (messages: Message[]) => {
    setResponse('');
    setIsStreaming(true);

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      const lines = text.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const payload = line.slice(6);
          if (payload === '[DONE]') break;

          const { content } = JSON.parse(payload);
          setResponse((prev) => prev + content);
        }
      }
    }

    setIsStreaming(false);
  }, []);

  return { response, isStreaming, sendMessage };
}

// Usage
function ChatUI() {
  const { response, isStreaming, sendMessage } = useAIStream();

  return (
    <div>
      <div className="prose">
        {response}
        {isStreaming && <span className="animate-pulse">|</span>}
      </div>
      <button
        onClick={() => sendMessage([{ role: 'user', content: 'Hello!' }])}
        disabled={isStreaming}
      >
        Send
      </button>
    </div>
  );
}
```

### Using Vercel AI SDK (Recommended)

```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });
  return result.toDataStreamResponse();
}

// Client component
'use client';
import { useChat } from '@ai-sdk/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <div>
      {messages.map((m) => (
        <div key={m.id}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
        <button type="submit" disabled={isLoading}>Send</button>
      </form>
    </div>
  );
}
```

## Reconnection with Last-Event-ID

```typescript
// Server: include event IDs
let eventCounter = 0;

function sendEvent(res: Response, event: string, data: unknown) {
  eventCounter++;
  res.write(`id: ${eventCounter}\n`);
  res.write(`event: ${event}\n`);
  res.write(`data: ${JSON.stringify(data)}\n\n`);
}

// On reconnect, browser sends Last-Event-ID header
// Server can replay missed events
app.get('/api/events', (req, res) => {
  const lastId = parseInt(req.headers['last-event-id'] || '0', 10);

  // Replay events since lastId
  const missedEvents = eventLog.filter((e) => e.id > lastId);
  for (const event of missedEvents) {
    sendEvent(res, event.type, event.data);
  }

  // Then continue with live events...
});
```

## Custom Reconnection Delay

```typescript
// Server controls retry interval
function setRetryInterval(res: Response, ms: number) {
  res.write(`retry: ${ms}\n\n`);
}

// On error, increase retry; on success, decrease
app.get('/api/events', (req, res) => {
  setRetryInterval(res, 3000); // 3s reconnect delay
  // ...
});
```

## SSE React Hook

```typescript
'use client';
import { useEffect, useState, useRef, useCallback } from 'react';

interface UseSSEOptions {
  url: string;
  events?: string[];
  withCredentials?: boolean;
}

export function useSSE<T = unknown>({ url, events = [], withCredentials }: UseSSEOptions) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Event | null>(null);
  const [readyState, setReadyState] = useState<number>(EventSource.CONNECTING);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const source = new EventSource(url, { withCredentials });
    sourceRef.current = source;

    source.onopen = () => setReadyState(EventSource.OPEN);
    source.onerror = (e) => {
      setError(e);
      setReadyState(source.readyState);
    };

    // Listen to default message event
    source.onmessage = (e) => setData(JSON.parse(e.data));

    // Listen to custom events
    for (const event of events) {
      source.addEventListener(event, (e: MessageEvent) => {
        setData(JSON.parse(e.data));
      });
    }

    return () => source.close();
  }, [url, withCredentials, events.join(',')]);

  const close = useCallback(() => sourceRef.current?.close(), []);

  return { data, error, readyState, close };
}
```
