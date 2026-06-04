# Bun Native APIs Reference

## File System - Bun.file() and Bun.write()

Fast, optimized file operations with zero async overhead.

```typescript
// Read file as text
const file = Bun.file("README.md");
const text = await file.text();
const size = file.size;
const lastModified = file.lastModified;

// Read as binary
const buffer = await Bun.file("image.png").arrayBuffer();

// Read as stream
const stream = Bun.file("large.bin").stream();
for await (const chunk of stream) {
  console.log(chunk.length);
}

// Write file (overwrites)
await Bun.write("output.txt", "Hello World");

// Write from buffer
const data = new Uint8Array([1, 2, 3]);
await Bun.write("binary.bin", data);

// Append to file
const file = Bun.file("log.txt");
await Bun.write(file, "new line\n", { createOnly: false });

// Write multiple files
await Bun.write("file1.txt", "content1");
await Bun.write("file2.txt", "content2");
```

## HTTP Server - Bun.serve()

Ultra-fast HTTP server with automatic performance optimizations.

```typescript
import { Bun } from "bun";

// Basic server
Bun.serve({
  port: 3000,
  hostname: "0.0.0.0",
  fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/") {
      return new Response("Hello, World!");
    }

    if (url.pathname === "/api/data") {
      return Response.json({ status: "ok" });
    }

    return new Response("Not Found", { status: 404 });
  },
});

// With async
Bun.serve({
  port: 3000,
  async fetch(req) {
    const body = await req.json();
    return Response.json({ received: body });
  },
});

// WebSocket support
Bun.serve({
  port: 3000,
  fetch(req, server) {
    if (server.upgrade(req)) {
      return; // Upgraded to WebSocket
    }
    return new Response("Not a WebSocket");
  },
  websocket: {
    open(ws) {
      console.log("Client connected");
      ws.send("Welcome");
    },
    message(ws, message) {
      console.log("Received:", message);
      ws.send(`Echo: ${message}`);
    },
    close(ws) {
      console.log("Client disconnected");
    },
  },
});
```

## SQLite - bun:sqlite

Built-in SQLite driver, zero dependencies.

```typescript
import { Database } from "bun:sqlite";

// Create in-memory or file-based DB
const db = new Database("mydb.sqlite");
// const db = new Database(":memory:"); // In-memory

// Create table
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE
  )
`);

// Prepared statement (safe from SQL injection)
const insertUser = db.prepare("INSERT INTO users (name, email) VALUES (?, ?)");
insertUser.run("Alice", "alice@example.com");
insertUser.run("Bob", "bob@example.com");

// Query with results
const query = db.prepare("SELECT * FROM users WHERE id = ?");
const user = query.get(1);
console.log(user); // { id: 1, name: "Alice", email: "alice@example.com" }

// Query all rows
const allUsers = db.prepare("SELECT * FROM users").all();
console.log(allUsers);

// Query with parameters
const byEmail = db.prepare("SELECT * FROM users WHERE email = ?");
const user2 = byEmail.get("bob@example.com");

// Update
const update = db.prepare("UPDATE users SET name = ? WHERE id = ?");
update.run("Alice Updated", 1);

// Delete
const delete_stmt = db.prepare("DELETE FROM users WHERE id = ?");
delete_stmt.run(2);

// Transaction
db.exec("BEGIN TRANSACTION");
try {
  insertUser.run("Carol", "carol@example.com");
  insertUser.run("Dave", "dave@example.com");
  db.exec("COMMIT");
} catch (error) {
  db.exec("ROLLBACK");
  throw error;
}
```

## Web APIs - Native (No Polyfills Needed)

Bun implements Web standards natively.

```typescript
// fetch - built-in, fast
const response = await fetch("https://api.example.com");
const data = await response.json();

// FormData
const form = new FormData();
form.append("file", new File([content], "doc.txt"));
form.append("name", "test");
const response = await fetch("/upload", {
  method: "POST",
  body: form,
});

// Blob and File
const blob = new Blob(["hello"], { type: "text/plain" });
const file = new File([blob], "greeting.txt");

// WebSocket (no ws package needed)
const ws = new WebSocket("wss://echo.websocket.org");
ws.onopen = () => ws.send("hello");
ws.onmessage = (e) => console.log("Message:", e.data);
ws.onerror = (e) => console.error("Error:", e);
ws.onclose = () => console.log("Closed");

// Headers, Request, Response - all native
const headers = new Headers({
  "content-type": "application/json",
  "authorization": "Bearer token",
});

const request = new Request("https://api.example.com/data", {
  method: "POST",
  headers,
  body: JSON.stringify({ key: "value" }),
});

// URLSearchParams
const params = new URLSearchParams({ q: "bun", limit: "10" });
console.log(params.toString()); // "q=bun&limit=10"

// TextEncoder / TextDecoder
const encoded = new TextEncoder().encode("hello");
const decoded = new TextDecoder().decode(encoded);
```

## Child Process - Bun.spawn()

```typescript
// Spawn process
const proc = Bun.spawn(["echo", "hello"]);
const output = await Bun.readableStreamToText(proc.stdout);
console.log(output); // "hello\n"

// With stdin/stdout piping
const proc2 = Bun.spawn(["cat"], {
  stdin: Bun.file("input.txt").stream(),
  stdout: "pipe",
});
const text = await Bun.readableStreamToText(proc2.stdout);

// Exit code
const exitCode = await proc.exited;
console.log("Exit code:", exitCode);
```

## Timers & Performance

```typescript
// Standard timers (same as Node.js)
const timeout = setTimeout(() => {
  console.log("After 1 second");
}, 1000);

const interval = setInterval(() => {
  console.log("Every 500ms");
}, 500);

clearTimeout(timeout);
clearInterval(interval);

// High-resolution timing
const start = performance.now();
// do work
const elapsed = performance.now() - start;
console.log(`Took ${elapsed}ms`);

// Memory usage
console.log(process.memoryUsage());
// { rss: ..., heapTotal: ..., heapUsed: ... }
```
