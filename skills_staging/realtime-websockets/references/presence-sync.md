# Presence & Synchronization Patterns

## Online/Offline Presence

### Server-Side Presence Tracking

```typescript
import { Server, Socket } from 'socket.io';

interface UserPresence {
  userId: string;
  socketId: string;
  status: 'online' | 'away' | 'busy';
  lastSeen: number;
}

const presenceMap = new Map<string, UserPresence>();

io.on('connection', (socket) => {
  const userId = (socket as any).user.id;

  // Mark online
  presenceMap.set(userId, {
    userId,
    socketId: socket.id,
    status: 'online',
    lastSeen: Date.now(),
  });

  // Broadcast presence to others
  socket.broadcast.emit('presence:update', {
    userId,
    status: 'online',
  });

  // Send current presence list to new client
  socket.emit('presence:list', Array.from(presenceMap.values()));

  // Status change (away, busy)
  socket.on('presence:status', (status: 'online' | 'away' | 'busy') => {
    const entry = presenceMap.get(userId);
    if (entry) {
      entry.status = status;
      entry.lastSeen = Date.now();
      io.emit('presence:update', { userId, status });
    }
  });

  // Disconnect
  socket.on('disconnect', () => {
    presenceMap.delete(userId);
    io.emit('presence:update', { userId, status: 'offline' });
  });
});

// Periodic stale connection cleanup
setInterval(() => {
  const staleThreshold = Date.now() - 60_000; // 1 minute
  for (const [userId, entry] of presenceMap) {
    if (entry.lastSeen < staleThreshold) {
      presenceMap.delete(userId);
      io.emit('presence:update', { userId, status: 'offline' });
    }
  }
}, 30_000);
```

### Client-Side Presence Hook

```typescript
'use client';
import { useEffect, useState } from 'react';
import { Socket } from 'socket.io-client';

interface Presence {
  userId: string;
  status: 'online' | 'away' | 'busy' | 'offline';
}

export function usePresence(socket: Socket | null, currentUserId: string) {
  const [presenceMap, setPresenceMap] = useState<Map<string, Presence>>(new Map());

  useEffect(() => {
    if (!socket) return;

    socket.on('presence:list', (list: Presence[]) => {
      const map = new Map(list.map((p) => [p.userId, p]));
      setPresenceMap(map);
    });

    socket.on('presence:update', (update: Presence) => {
      setPresenceMap((prev) => {
        const next = new Map(prev);
        if (update.status === 'offline') {
          next.delete(update.userId);
        } else {
          next.set(update.userId, update);
        }
        return next;
      });
    });

    // Auto-away on visibility change
    const handleVisibility = () => {
      socket.emit(
        'presence:status',
        document.hidden ? 'away' : 'online'
      );
    };
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibility);
      socket.off('presence:list');
      socket.off('presence:update');
    };
  }, [socket, currentUserId]);

  const isOnline = (userId: string) =>
    presenceMap.get(userId)?.status === 'online';

  return { presenceMap, isOnline };
}
```

## Typing Indicators

### Debounced Typing Events

```typescript
// Client-side: emit typing with debounce
function useTypingIndicator(socket: Socket | null, roomId: string) {
  const typingTimeout = useRef<NodeJS.Timeout | null>(null);

  const emitTyping = useCallback(() => {
    if (!socket) return;

    socket.emit('typing:start', { roomId });

    // Auto-stop after 3 seconds of no typing
    if (typingTimeout.current) clearTimeout(typingTimeout.current);
    typingTimeout.current = setTimeout(() => {
      socket.emit('typing:stop', { roomId });
    }, 3000);
  }, [socket, roomId]);

  const stopTyping = useCallback(() => {
    if (typingTimeout.current) clearTimeout(typingTimeout.current);
    socket?.emit('typing:stop', { roomId });
  }, [socket, roomId]);

  return { emitTyping, stopTyping };
}

// Server-side
io.on('connection', (socket) => {
  const userId = (socket as any).user.id;
  const userName = (socket as any).user.name;

  socket.on('typing:start', ({ roomId }) => {
    socket.to(roomId).emit('typing:update', {
      userId,
      userName,
      isTyping: true,
    });
  });

  socket.on('typing:stop', ({ roomId }) => {
    socket.to(roomId).emit('typing:update', {
      userId,
      userName,
      isTyping: false,
    });
  });

  // Clear typing on disconnect
  socket.on('disconnect', () => {
    socket.rooms.forEach((roomId) => {
      socket.to(roomId).emit('typing:update', {
        userId,
        userName,
        isTyping: false,
      });
    });
  });
});
```

### Typing Indicator Component

```typescript
'use client';
import { useEffect, useState } from 'react';

function TypingIndicator({ socket, roomId }: { socket: Socket; roomId: string }) {
  const [typingUsers, setTypingUsers] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    socket.on('typing:update', ({ userId, userName, isTyping }) => {
      setTypingUsers((prev) => {
        const next = new Map(prev);
        if (isTyping) {
          next.set(userId, userName);
        } else {
          next.delete(userId);
        }
        return next;
      });
    });

    return () => { socket.off('typing:update'); };
  }, [socket, roomId]);

  const users = Array.from(typingUsers.values());
  if (users.length === 0) return null;
  if (users.length === 1) return <p className="text-sm text-gray-500">{users[0]} is typing...</p>;
  if (users.length === 2) return <p className="text-sm text-gray-500">{users[0]} and {users[1]} are typing...</p>;
  return <p className="text-sm text-gray-500">Several people are typing...</p>;
}
```

## Cursor Sharing (Collaborative)

### Real-Time Cursor Position Broadcasting

```typescript
// Client: throttled cursor broadcasting
import { throttle } from 'lodash-es';

function useCursorSharing(socket: Socket | null, roomId: string) {
  const [cursors, setCursors] = useState<Map<string, CursorPosition>>(new Map());

  // Throttle to 20 updates/second max
  const broadcastCursor = useMemo(
    () =>
      throttle((x: number, y: number) => {
        socket?.emit('cursor:move', { roomId, x, y });
      }, 50), // 50ms = ~20fps
    [socket, roomId]
  );

  useEffect(() => {
    if (!socket) return;

    socket.on('cursor:update', ({ userId, userName, color, x, y }) => {
      setCursors((prev) => {
        const next = new Map(prev);
        next.set(userId, { userId, userName, color, x, y });
        return next;
      });
    });

    // Remove stale cursors
    socket.on('cursor:leave', ({ userId }) => {
      setCursors((prev) => {
        const next = new Map(prev);
        next.delete(userId);
        return next;
      });
    });

    return () => {
      socket.off('cursor:update');
      socket.off('cursor:leave');
    };
  }, [socket]);

  return { cursors, broadcastCursor };
}

interface CursorPosition {
  userId: string;
  userName: string;
  color: string;
  x: number;
  y: number;
}

// Render other users' cursors
function RemoteCursors({ cursors }: { cursors: Map<string, CursorPosition> }) {
  return (
    <>
      {Array.from(cursors.values()).map((cursor) => (
        <div
          key={cursor.userId}
          className="pointer-events-none absolute z-50 transition-all duration-75"
          style={{ left: cursor.x, top: cursor.y }}
        >
          {/* SVG cursor icon */}
          <svg width="16" height="16" viewBox="0 0 16 16" fill={cursor.color}>
            <path d="M0 0 L0 16 L4 12 L8 16 L10 14 L6 10 L12 10 Z" />
          </svg>
          <span
            className="ml-2 rounded px-1 text-xs text-white"
            style={{ backgroundColor: cursor.color }}
          >
            {cursor.userName}
          </span>
        </div>
      ))}
    </>
  );
}
```

## Optimistic Updates

### Pattern: Immediate UI + Server Confirmation

```typescript
type MessageStatus = 'sending' | 'sent' | 'failed';

interface ChatMessage {
  id: string;
  text: string;
  status: MessageStatus;
}

function useChatWithOptimisticUpdates(socket: Socket, roomId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const sendMessage = useCallback((text: string) => {
    const tempId = `temp_${Date.now()}_${Math.random()}`;

    // 1. Immediately show in UI
    setMessages((prev) => [
      ...prev,
      { id: tempId, text, status: 'sending' },
    ]);

    // 2. Send to server with acknowledgement
    socket.timeout(5000).emitWithAck('chat:send', { roomId, text, tempId })
      .then((res: { id: string }) => {
        // 3a. Replace temp ID with real ID from server
        setMessages((prev) =>
          prev.map((m) =>
            m.id === tempId ? { ...m, id: res.id, status: 'sent' } : m
          )
        );
      })
      .catch(() => {
        // 3b. Mark as failed
        setMessages((prev) =>
          prev.map((m) =>
            m.id === tempId ? { ...m, status: 'failed' } : m
          )
        );
      });
  }, [socket, roomId]);

  const retryMessage = useCallback((tempId: string) => {
    const msg = messages.find((m) => m.id === tempId);
    if (msg) {
      setMessages((prev) => prev.filter((m) => m.id !== tempId));
      sendMessage(msg.text);
    }
  }, [messages, sendMessage]);

  return { messages, sendMessage, retryMessage };
}
```

## CRDT Basics for Conflict Resolution

CRDTs (Conflict-free Replicated Data Types) allow multiple clients to edit concurrently without coordination.

### Last-Writer-Wins Register

```typescript
// Simplest CRDT: higher timestamp wins
interface LWWRegister<T> {
  value: T;
  timestamp: number;
  peerId: string;
}

function mergeLWW<T>(local: LWWRegister<T>, remote: LWWRegister<T>): LWWRegister<T> {
  if (remote.timestamp > local.timestamp) return remote;
  if (remote.timestamp === local.timestamp) {
    // Tiebreaker: lexicographic peer ID
    return remote.peerId > local.peerId ? remote : local;
  }
  return local;
}

// Usage: shared document title
const titleRegister: LWWRegister<string> = {
  value: 'Untitled',
  timestamp: Date.now(),
  peerId: myPeerId,
};

socket.on('title:update', (remote: LWWRegister<string>) => {
  const merged = mergeLWW(titleRegister, remote);
  titleRegister.value = merged.value;
  titleRegister.timestamp = merged.timestamp;
  titleRegister.peerId = merged.peerId;
});
```

### G-Counter (Grow-only Counter)

```typescript
// Each peer has its own counter. Sum gives total.
type GCounter = Record<string, number>;

function increment(counter: GCounter, peerId: string): GCounter {
  return { ...counter, [peerId]: (counter[peerId] || 0) + 1 };
}

function merge(a: GCounter, b: GCounter): GCounter {
  const result: GCounter = { ...a };
  for (const [peer, count] of Object.entries(b)) {
    result[peer] = Math.max(result[peer] || 0, count);
  }
  return result;
}

function value(counter: GCounter): number {
  return Object.values(counter).reduce((sum, n) => sum + n, 0);
}

// Usage: like counter, view counter
let likes: GCounter = {};
likes = increment(likes, myPeerId);
socket.emit('likes:update', likes);

socket.on('likes:update', (remote: GCounter) => {
  likes = merge(likes, remote);
  updateUI(value(likes));
});
```

### Using Yjs for Rich Collaborative Editing

```typescript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

// Shared document
const ydoc = new Y.Doc();
const provider = new WebsocketProvider(
  'wss://your-yjs-server.com',
  'document-room-id',
  ydoc
);

// Shared text (like Google Docs)
const ytext = ydoc.getText('content');
ytext.observe((event) => {
  console.log('Text changed:', ytext.toString());
});

// Shared map (like a key-value store)
const ymap = ydoc.getMap('metadata');
ymap.set('title', 'My Document');
ymap.observe((event) => {
  event.changes.keys.forEach((change, key) => {
    console.log(`Key "${key}" changed:`, ymap.get(key));
  });
});

// Shared array (like a list)
const yarray = ydoc.getArray('items');
yarray.push(['item 1', 'item 2']);

// Awareness (cursors, selections, presence)
const awareness = provider.awareness;
awareness.setLocalStateField('user', {
  name: 'Alice',
  color: '#ff0000',
  cursor: { x: 100, y: 200 },
});

awareness.on('change', () => {
  const states = awareness.getStates();
  // Map<clientId, { user: { name, color, cursor } }>
  updateRemoteCursors(states);
});

// Cleanup
provider.disconnect();
ydoc.destroy();
```

## Room-Based State Synchronization

### Server-Side Room State

```typescript
interface RoomState {
  id: string;
  data: Record<string, unknown>;
  version: number;
  members: Set<string>;
}

const rooms = new Map<string, RoomState>();

function getOrCreateRoom(roomId: string): RoomState {
  if (!rooms.has(roomId)) {
    rooms.set(roomId, {
      id: roomId,
      data: {},
      version: 0,
      members: new Set(),
    });
  }
  return rooms.get(roomId)!;
}

io.on('connection', (socket) => {
  const userId = (socket as any).user.id;

  socket.on('room:join', (roomId: string) => {
    const room = getOrCreateRoom(roomId);
    room.members.add(userId);
    socket.join(roomId);

    // Send full state to new member
    socket.emit('room:state', {
      data: room.data,
      version: room.version,
      members: Array.from(room.members),
    });

    // Notify others
    socket.to(roomId).emit('room:member-joined', { userId });
  });

  socket.on('room:update', ({ roomId, patch, expectedVersion }) => {
    const room = getOrCreateRoom(roomId);

    // Optimistic concurrency: reject stale updates
    if (expectedVersion !== room.version) {
      socket.emit('room:conflict', {
        serverVersion: room.version,
        serverData: room.data,
      });
      return;
    }

    // Apply patch
    room.data = { ...room.data, ...patch };
    room.version++;

    // Broadcast to all in room (including sender for confirmation)
    io.in(roomId).emit('room:updated', {
      patch,
      version: room.version,
      updatedBy: userId,
    });
  });

  socket.on('disconnect', () => {
    for (const [roomId, room] of rooms) {
      if (room.members.has(userId)) {
        room.members.delete(userId);
        io.in(roomId).emit('room:member-left', { userId });

        // Cleanup empty rooms
        if (room.members.size === 0) {
          rooms.delete(roomId);
        }
      }
    }
  });
});
```

### Client-Side Room State Hook

```typescript
'use client';
import { useEffect, useState, useCallback, useRef } from 'react';

export function useRoomState<T extends Record<string, unknown>>(
  socket: Socket | null,
  roomId: string,
  initialState: T
) {
  const [state, setState] = useState<T>(initialState);
  const [version, setVersion] = useState(0);
  const [members, setMembers] = useState<string[]>([]);
  const versionRef = useRef(version);
  versionRef.current = version;

  useEffect(() => {
    if (!socket) return;
    socket.emit('room:join', roomId);

    socket.on('room:state', ({ data, version: v, members: m }) => {
      setState(data as T);
      setVersion(v);
      versionRef.current = v;
      setMembers(m);
    });

    socket.on('room:updated', ({ patch, version: v }) => {
      setState((prev) => ({ ...prev, ...patch }));
      setVersion(v);
      versionRef.current = v;
    });

    socket.on('room:conflict', ({ serverData, serverVersion }) => {
      // Server wins on conflict — reset local state
      setState(serverData as T);
      setVersion(serverVersion);
      versionRef.current = serverVersion;
    });

    socket.on('room:member-joined', ({ userId }) => {
      setMembers((prev) => [...prev, userId]);
    });

    socket.on('room:member-left', ({ userId }) => {
      setMembers((prev) => prev.filter((id) => id !== userId));
    });

    return () => {
      socket.emit('room:leave', roomId);
      socket.off('room:state');
      socket.off('room:updated');
      socket.off('room:conflict');
      socket.off('room:member-joined');
      socket.off('room:member-left');
    };
  }, [socket, roomId]);

  const updateState = useCallback(
    (patch: Partial<T>) => {
      // Optimistic local update
      setState((prev) => ({ ...prev, ...patch }));
      socket?.emit('room:update', {
        roomId,
        patch,
        expectedVersion: versionRef.current,
      });
    },
    [socket, roomId]
  );

  return { state, version, members, updateState };
}
```
