# Socket.io Patterns

## Server Setup

```typescript
import { createServer } from 'http';
import { Server } from 'socket.io';
import express from 'express';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST'],
  },
  pingInterval: 25000,     // How often to ping clients
  pingTimeout: 20000,      // How long to wait for pong
  maxHttpBufferSize: 1e6,  // 1MB max message size
  connectionStateRecovery: {
    maxDisconnectionDuration: 2 * 60 * 1000, // 2 min
    skipMiddlewares: true,
  },
});

httpServer.listen(3001, () => console.log('Socket.io on :3001'));
```

## Namespaces

Namespaces let you multiplex a single connection for different features.

```typescript
// Default namespace
io.on('connection', (socket) => {
  console.log('Main namespace:', socket.id);
});

// /chat namespace — separate logic, same port
const chatNs = io.of('/chat');
chatNs.on('connection', (socket) => {
  console.log('Chat namespace:', socket.id);

  socket.on('message', (data) => {
    chatNs.emit('message', data); // Broadcast within /chat
  });
});

// /admin namespace with auth
const adminNs = io.of('/admin');
adminNs.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (verifyAdminToken(token)) return next();
  next(new Error('Admin access denied'));
});

adminNs.on('connection', (socket) => {
  socket.on('stats', () => {
    socket.emit('stats', getServerStats());
  });
});
```

Client connecting to namespaces:

```typescript
import { io } from 'socket.io-client';

// These share a single underlying WebSocket connection
const chatSocket = io('http://localhost:3001/chat', {
  auth: { token: 'user-jwt' },
});

const adminSocket = io('http://localhost:3001/admin', {
  auth: { token: 'admin-jwt' },
});
```

## Rooms

Rooms are server-side groupings of sockets. Clients cannot join rooms directly.

```typescript
io.on('connection', (socket) => {
  // Join a room
  socket.on('join-room', (roomId: string) => {
    socket.join(roomId);
    socket.to(roomId).emit('user-joined', { userId: socket.id });
    console.log(`${socket.id} joined ${roomId}`);
  });

  // Leave a room
  socket.on('leave-room', (roomId: string) => {
    socket.leave(roomId);
    socket.to(roomId).emit('user-left', { userId: socket.id });
  });

  // Send message to room (excludes sender)
  socket.on('room-message', ({ roomId, text }) => {
    socket.to(roomId).emit('room-message', {
      text,
      sender: socket.id,
      timestamp: Date.now(),
    });
  });

  // Auto-leave all rooms on disconnect
  socket.on('disconnecting', () => {
    for (const room of socket.rooms) {
      if (room !== socket.id) {
        socket.to(room).emit('user-left', { userId: socket.id });
      }
    }
  });
});
```

### Room Utilities

```typescript
// Get all sockets in a room
async function getRoomMembers(roomId: string) {
  const sockets = await io.in(roomId).fetchSockets();
  return sockets.map((s) => ({
    id: s.id,
    user: (s as any).user,
  }));
}

// Send to specific room from anywhere (not just in a handler)
io.to('room-123').emit('notification', { text: 'Server message' });

// Send to multiple rooms
io.to('room-a').to('room-b').emit('announcement', { text: 'Hello both rooms' });

// Send to room except specific sockets
io.to('room-123').except(socket.id).emit('update', data);
```

## Middleware

```typescript
// Connection-level middleware (runs once per connection)
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const user = verifyJwt(token);
    (socket as any).user = user;
    next();
  } catch (err) {
    next(new Error('Authentication failed'));
  }
});

// Event-level middleware (runs for every event)
io.on('connection', (socket) => {
  socket.use(([event, ...args], next) => {
    // Rate limiting
    const now = Date.now();
    const lastEvent = (socket as any).lastEvent || 0;
    if (now - lastEvent < 100) {
      return next(new Error('Rate limit exceeded'));
    }
    (socket as any).lastEvent = now;
    next();
  });
});

// Namespace middleware
io.of('/admin').use((socket, next) => {
  if ((socket as any).user?.role !== 'admin') {
    return next(new Error('Admin only'));
  }
  next();
});
```

## Broadcasting Patterns

```typescript
io.on('connection', (socket) => {
  // To everyone including sender
  io.emit('global', data);

  // To everyone except sender
  socket.broadcast.emit('others', data);

  // To specific room (excludes sender)
  socket.to('room-1').emit('room-msg', data);

  // To specific room (includes sender)
  io.in('room-1').emit('room-msg', data);

  // To specific socket by ID
  io.to(targetSocketId).emit('direct', data);

  // To sender only
  socket.emit('self', data);
});
```

## Acknowledgements (Request/Response)

```typescript
// Server: handler with callback
io.on('connection', (socket) => {
  socket.on('create-todo', async (data, callback) => {
    try {
      const todo = await db.todos.create(data);
      callback({ status: 'ok', todo });
    } catch (err) {
      callback({ status: 'error', message: err.message });
    }
  });
});

// Client: emit with acknowledgement
const response = await socket.emitWithAck('create-todo', {
  title: 'Buy groceries',
});
if (response.status === 'ok') {
  console.log('Created:', response.todo);
}

// With timeout
socket.timeout(5000).emitWithAck('create-todo', data)
  .then((res) => console.log(res))
  .catch(() => console.error('Timeout'));
```

## Binary Data

```typescript
// Send file as ArrayBuffer
const fileInput = document.getElementById('file') as HTMLInputElement;
fileInput.addEventListener('change', () => {
  const file = fileInput.files![0];
  const reader = new FileReader();
  reader.onload = () => {
    socket.emit('upload', {
      name: file.name,
      type: file.type,
      data: reader.result, // ArrayBuffer — Socket.io handles binary
    });
  };
  reader.readAsArrayBuffer(file);
});

// Server receives binary automatically
socket.on('upload', ({ name, type, data }) => {
  // data is a Buffer
  fs.writeFileSync(`./uploads/${name}`, Buffer.from(data));
});

// Stream large files with chunking
function sendChunked(socket: Socket, file: Buffer, chunkSize = 64 * 1024) {
  const totalChunks = Math.ceil(file.length / chunkSize);
  for (let i = 0; i < totalChunks; i++) {
    const chunk = file.subarray(i * chunkSize, (i + 1) * chunkSize);
    socket.emit('chunk', { index: i, total: totalChunks, data: chunk });
  }
}
```

## Redis Adapter for Scaling

When running multiple Socket.io servers behind a load balancer, use the Redis adapter so events reach all connected clients regardless of which server they're on.

```typescript
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const pubClient = createClient({ url: 'redis://localhost:6379' });
const subClient = pubClient.duplicate();

await Promise.all([pubClient.connect(), subClient.connect()]);

const io = new Server(httpServer);
io.adapter(createAdapter(pubClient, subClient));

// Now io.emit() broadcasts across ALL server instances
io.emit('global', { msg: 'reaches every connected client' });

// Rooms work across instances too
io.to('room-1').emit('update', data);

// Fetch sockets across all instances
const sockets = await io.in('room-1').fetchSockets();
```

### Redis Adapter with Streams (more reliable)

```typescript
import { createAdapter } from '@socket.io/redis-streams-adapter';
import { createClient } from 'redis';

const redisClient = createClient({ url: 'redis://localhost:6379' });
await redisClient.connect();

io.adapter(createAdapter(redisClient));
// Uses Redis Streams instead of Pub/Sub — survives brief disconnects
```

## Socket.io with Next.js

### API Route Handler (Pages Router)

```typescript
// pages/api/socket.ts
import type { NextApiRequest } from 'next';
import type { NextApiResponse } from 'next';
import { Server } from 'socket.io';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if ((res.socket as any).server.io) {
    // Already initialized
    res.end();
    return;
  }

  const io = new Server((res.socket as any).server, {
    path: '/api/socket',
    addTrailingSlash: false,
  });

  io.on('connection', (socket) => {
    socket.on('message', (data) => {
      io.emit('message', data);
    });
  });

  (res.socket as any).server.io = io;
  res.end();
}
```

### Separate Server (Recommended for App Router)

```typescript
// server.ts — run alongside Next.js
import { createServer } from 'http';
import { Server } from 'socket.io';
import next from 'next';

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handler = app.getRequestHandler();

app.prepare().then(() => {
  const httpServer = createServer(handler);
  const io = new Server(httpServer, {
    cors: { origin: '*' },
  });

  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);
  });

  httpServer.listen(3000);
});
```

### Client Hook for React

```typescript
'use client';
import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export function useSocket(namespace = '/') {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const socket = io(
      process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3001',
      {
        path: '/socket.io',
        transports: ['websocket', 'polling'], // Prefer WebSocket
        auth: { token: getToken() },
      }
    );

    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));

    socketRef.current = socket;
    return () => { socket.disconnect(); };
  }, [namespace]);

  return { socket: socketRef.current, connected };
}

// Usage in component
function ChatRoom({ roomId }: { roomId: string }) {
  const { socket, connected } = useSocket();
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    if (!socket) return;
    socket.emit('join-room', roomId);

    socket.on('room-message', (msg: Message) => {
      setMessages((prev) => [...prev, msg]);
    });

    return () => {
      socket.emit('leave-room', roomId);
      socket.off('room-message');
    };
  }, [socket, roomId]);

  const sendMessage = (text: string) => {
    socket?.emit('room-message', { roomId, text });
  };

  return (
    <div>
      <span>{connected ? 'Connected' : 'Disconnected'}</span>
      {messages.map((m, i) => <p key={i}>{m.text}</p>)}
    </div>
  );
}
```
