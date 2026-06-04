# Notification Systems Reference

Architecture patterns for in-app, email, and push notification systems with queues, digests, and rate limiting.

## Notification Preference System

### Database Schema (Prisma)

```prisma
model User {
  id                      String                   @id @default(cuid())
  email                   String                   @unique
  notificationPreferences NotificationPreferences?
  notifications           Notification[]
}

model NotificationPreferences {
  id        String @id @default(cuid())
  userId    String @unique
  user      User   @relation(fields: [userId], references: [id])

  // Global channel toggles
  emailEnabled Boolean @default(true)
  inAppEnabled Boolean @default(true)
  pushEnabled  Boolean @default(true)

  // Per-category preferences (JSON)
  categoryPrefs Json @default("{}")
  // Shape: { "marketing": { "email": true, "inApp": true, "push": false }, ... }

  // Digest settings
  digestFrequency DigestFrequency @default(REALTIME)

  // Quiet hours
  quietHoursStart String?   // "22:00"
  quietHoursEnd   String?   // "08:00"
  timezone        String    @default("UTC")

  // Unsubscribe
  unsubscribedAll Boolean @default(false)
  unsubscribeToken String @unique @default(cuid())

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

enum DigestFrequency {
  REALTIME
  DAILY
  WEEKLY
  OFF
}

model Notification {
  id        String   @id @default(cuid())
  userId    String
  user      User     @relation(fields: [userId], references: [id])

  category  String   // "marketing" | "product" | "security" | "billing"
  channel   String   // "email" | "inApp" | "push"
  title     String
  body      String
  actionUrl String?

  status    NotificationStatus @default(PENDING)
  sentAt    DateTime?
  readAt    DateTime?
  failedAt  DateTime?
  error     String?

  createdAt DateTime @default(now())

  @@index([userId, channel, status])
  @@index([userId, readAt])
  @@index([createdAt])
}

enum NotificationStatus {
  PENDING
  QUEUED
  SENT
  DELIVERED
  READ
  FAILED
}
```

### Preferences API

```typescript
// app/api/notifications/preferences/route.ts
import { auth } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { z } from "zod";

const prefsSchema = z.object({
  emailEnabled: z.boolean().optional(),
  inAppEnabled: z.boolean().optional(),
  pushEnabled: z.boolean().optional(),
  categoryPrefs: z.record(z.object({
    email: z.boolean(),
    inApp: z.boolean(),
    push: z.boolean(),
  })).optional(),
  digestFrequency: z.enum(["REALTIME", "DAILY", "WEEKLY", "OFF"]).optional(),
  quietHoursStart: z.string().nullable().optional(),
  quietHoursEnd: z.string().nullable().optional(),
  timezone: z.string().optional(),
});

export async function GET() {
  const { userId } = await auth();
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const prefs = await db.notificationPreferences.findUnique({
    where: { userId },
  });

  return NextResponse.json(prefs ?? getDefaultPreferences());
}

export async function PATCH(req: NextRequest) {
  const { userId } = await auth();
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = prefsSchema.parse(await req.json());

  const prefs = await db.notificationPreferences.upsert({
    where: { userId },
    update: body,
    create: { userId, ...body },
  });

  return NextResponse.json(prefs);
}

function getDefaultPreferences() {
  return {
    emailEnabled: true,
    inAppEnabled: true,
    pushEnabled: true,
    categoryPrefs: {
      marketing: { email: true, inApp: true, push: false },
      product: { email: true, inApp: true, push: true },
      security: { email: true, inApp: true, push: true },
      billing: { email: true, inApp: true, push: false },
    },
    digestFrequency: "REALTIME",
    quietHoursStart: null,
    quietHoursEnd: null,
    timezone: "UTC",
  };
}
```

### One-Click Unsubscribe

RFC 8058 compliant unsubscribe for email:

```typescript
// app/api/unsubscribe/route.ts
import { NextRequest, NextResponse } from "next/server";

// List-Unsubscribe-Post handler (one-click)
export async function POST(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token");
  if (!token) return NextResponse.json({ error: "Missing token" }, { status: 400 });

  const prefs = await db.notificationPreferences.findUnique({
    where: { unsubscribeToken: token },
  });
  if (!prefs) return NextResponse.json({ error: "Invalid token" }, { status: 404 });

  await db.notificationPreferences.update({
    where: { id: prefs.id },
    data: { emailEnabled: false },
  });

  return NextResponse.json({ success: true });
}

// Add these headers when sending email via Resend:
function getUnsubscribeHeaders(unsubscribeToken: string) {
  const unsubUrl = `${process.env.NEXT_PUBLIC_APP_URL}/api/unsubscribe?token=${unsubscribeToken}`;
  return {
    "List-Unsubscribe": `<${unsubUrl}>`,
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
  };
}
```

## In-App + Email + Push Architecture

### Unified Notification Service

```typescript
// lib/notifications/service.ts
import { emailQueue } from "./queues/email-queue";
import { pushQueue } from "./queues/push-queue";
import { db } from "@/lib/db";

interface SendNotificationParams {
  userId: string;
  category: string;
  title: string;
  body: string;
  actionUrl?: string;
  emailTemplate?: string;
  emailProps?: Record<string, unknown>;
  data?: Record<string, unknown>; // Extra payload for push
}

export async function sendNotification(params: SendNotificationParams) {
  const { userId, category } = params;

  // 1. Load preferences
  const prefs = await db.notificationPreferences.findUnique({ where: { userId } });
  if (prefs?.unsubscribedAll && category !== "security") return;

  const catPrefs = (prefs?.categoryPrefs as Record<string, any>)?.[category];
  const channels = resolveChannels(prefs, catPrefs, category);

  // 2. Check quiet hours
  if (isInQuietHours(prefs) && category !== "security") {
    // Queue for delivery after quiet hours end
    const delayMs = msUntilQuietHoursEnd(prefs);
    return queueDelayed(params, delayMs);
  }

  // 3. Dispatch to each channel
  const results = [];

  if (channels.includes("inApp")) {
    const notification = await db.notification.create({
      data: {
        userId,
        category,
        channel: "inApp",
        title: params.title,
        body: params.body,
        actionUrl: params.actionUrl,
        status: "SENT",
        sentAt: new Date(),
      },
    });
    results.push({ channel: "inApp", id: notification.id });

    // Emit real-time event (SSE or WebSocket)
    await emitRealtimeEvent(userId, "notification", notification);
  }

  if (channels.includes("email") && params.emailTemplate) {
    const job = await emailQueue.add("send", {
      userId,
      template: params.emailTemplate,
      props: params.emailProps,
      subject: params.title,
    });
    results.push({ channel: "email", jobId: job.id });
  }

  if (channels.includes("push")) {
    const job = await pushQueue.add("send", {
      userId,
      title: params.title,
      body: params.body,
      actionUrl: params.actionUrl,
      data: params.data,
    });
    results.push({ channel: "push", jobId: job.id });
  }

  return results;
}

function resolveChannels(
  prefs: any,
  catPrefs: any,
  category: string
): string[] {
  // Security always goes everywhere
  if (category === "security") return ["email", "inApp", "push"];
  if (!prefs) return ["email", "inApp"]; // Default channels

  const channels: string[] = [];
  if (prefs.emailEnabled && catPrefs?.email !== false) channels.push("email");
  if (prefs.inAppEnabled && catPrefs?.inApp !== false) channels.push("inApp");
  if (prefs.pushEnabled && catPrefs?.push !== false) channels.push("push");
  return channels;
}
```

### In-App Notification API

```typescript
// app/api/notifications/route.ts
import { auth } from "@clerk/nextjs/server";
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const { userId } = await auth();
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const cursor = req.nextUrl.searchParams.get("cursor");
  const limit = Math.min(Number(req.nextUrl.searchParams.get("limit") ?? 20), 50);

  const notifications = await db.notification.findMany({
    where: { userId, channel: "inApp" },
    orderBy: { createdAt: "desc" },
    take: limit + 1,
    ...(cursor ? { cursor: { id: cursor }, skip: 1 } : {}),
  });

  const hasMore = notifications.length > limit;
  const items = hasMore ? notifications.slice(0, -1) : notifications;

  return NextResponse.json({
    items,
    nextCursor: hasMore ? items[items.length - 1].id : null,
  });
}

// Mark as read
export async function PATCH(req: NextRequest) {
  const { userId } = await auth();
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { ids } = await req.json();

  await db.notification.updateMany({
    where: { id: { in: ids }, userId, readAt: null },
    data: { readAt: new Date(), status: "READ" },
  });

  return NextResponse.json({ success: true });
}
```

## Queue Patterns with BullMQ

### Setup

```bash
npm install bullmq ioredis
```

### Email Queue with Retries and Rate Limiting

```typescript
// lib/notifications/queues/email-queue.ts
import { Queue, Worker, QueueScheduler } from "bullmq";
import Redis from "ioredis";
import { resend } from "@/lib/resend";

const connection = new Redis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null, // Required by BullMQ
});

export const emailQueue = new Queue("notifications:email", {
  connection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: "exponential", delay: 5000 },
    removeOnComplete: { age: 86400, count: 1000 }, // Keep 24h or 1000 jobs
    removeOnFail: { age: 604800, count: 5000 },    // Keep 7d or 5000 failures
  },
});

// Worker with concurrency and rate limiting
export const emailWorker = new Worker(
  "notifications:email",
  async (job) => {
    const { userId, template, props, subject } = job.data;

    // Load user email
    const user = await db.user.findUnique({ where: { id: userId } });
    if (!user?.email) throw new Error(`User ${userId} has no email`);

    // Load preferences + unsubscribe token
    const prefs = await db.notificationPreferences.findUnique({
      where: { userId },
    });

    // Render template
    const emailComponent = await loadTemplate(template, {
      ...props,
      unsubscribeToken: prefs?.unsubscribeToken,
    });

    // Send via Resend
    const { data, error } = await resend.emails.send({
      from: process.env.EMAIL_FROM!,
      to: user.email,
      subject,
      react: emailComponent,
      headers: prefs?.unsubscribeToken
        ? {
            "List-Unsubscribe": `<${process.env.NEXT_PUBLIC_APP_URL}/api/unsubscribe?token=${prefs.unsubscribeToken}>`,
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
          }
        : undefined,
    });

    if (error) throw new Error(error.message);

    // Record delivery
    await db.notification.create({
      data: {
        userId,
        category: job.data.category ?? "product",
        channel: "email",
        title: subject,
        body: "",
        status: "SENT",
        sentAt: new Date(),
      },
    });

    return { messageId: data?.id };
  },
  {
    connection,
    concurrency: 5,              // 5 parallel sends
    limiter: { max: 10, duration: 1000 }, // 10 emails/sec max
  }
);

emailWorker.on("failed", (job, err) => {
  console.error(`[email-worker] Job ${job?.id} failed (attempt ${job?.attemptsMade}):`, err.message);
});

emailWorker.on("completed", (job, result) => {
  console.log(`[email-worker] Job ${job.id} sent: ${result.messageId}`);
});
```

### Dead Letter Queue

```typescript
// Handle permanently failed jobs
emailWorker.on("failed", async (job, err) => {
  if (job && job.attemptsMade >= (job.opts.attempts ?? 3)) {
    // Move to dead letter queue for manual review
    await deadLetterQueue.add("failed-email", {
      originalJob: job.data,
      error: err.message,
      failedAt: new Date().toISOString(),
      attempts: job.attemptsMade,
    });

    // Alert ops team
    console.error(`[DLQ] Email permanently failed for user ${job.data.userId}:`, err.message);
  }
});
```

## Digest / Batch Emails

### Digest Aggregator

```typescript
// lib/notifications/digest.ts
import { emailQueue } from "./queues/email-queue";
import { db } from "@/lib/db";

/**
 * Run via cron: daily at 9am UTC and weekly on Mondays at 9am UTC
 */
export async function processDigests(frequency: "DAILY" | "WEEKLY") {
  const since = frequency === "DAILY"
    ? new Date(Date.now() - 24 * 60 * 60 * 1000)
    : new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  // Find users with this digest frequency
  const users = await db.notificationPreferences.findMany({
    where: {
      digestFrequency: frequency,
      emailEnabled: true,
      unsubscribedAll: false,
    },
    include: { user: true },
  });

  for (const prefs of users) {
    // Gather unread in-app notifications since last digest
    const notifications = await db.notification.findMany({
      where: {
        userId: prefs.userId,
        channel: "inApp",
        createdAt: { gte: since },
        readAt: null,
      },
      orderBy: { createdAt: "desc" },
      take: 20,
    });

    if (notifications.length === 0) continue;

    // Queue digest email
    await emailQueue.add("send", {
      userId: prefs.userId,
      template: "digest",
      props: {
        name: prefs.user.name,
        notifications: notifications.map((n) => ({
          title: n.title,
          body: n.body,
          actionUrl: n.actionUrl,
          createdAt: n.createdAt.toISOString(),
        })),
        frequency,
        unsubscribeToken: prefs.unsubscribeToken,
      },
      subject: frequency === "DAILY"
        ? `Your daily digest — ${notifications.length} updates`
        : `Your weekly digest — ${notifications.length} updates`,
      category: "product",
    });
  }
}
```

### Cron Setup (Next.js Route + Vercel Cron)

```typescript
// app/api/cron/digest/route.ts
import { NextRequest, NextResponse } from "next/server";
import { processDigests } from "@/lib/notifications/digest";

export async function GET(req: NextRequest) {
  // Verify cron secret
  if (req.headers.get("authorization") !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const frequency = req.nextUrl.searchParams.get("frequency") as "DAILY" | "WEEKLY";
  if (!frequency || !["DAILY", "WEEKLY"].includes(frequency)) {
    return NextResponse.json({ error: "Invalid frequency" }, { status: 400 });
  }

  await processDigests(frequency);
  return NextResponse.json({ success: true });
}
```

```json
// vercel.json
{
  "crons": [
    { "path": "/api/cron/digest?frequency=DAILY", "schedule": "0 9 * * *" },
    { "path": "/api/cron/digest?frequency=WEEKLY", "schedule": "0 9 * * 1" }
  ]
}
```

## Rate Limiting Notifications

### Per-User Rate Limiter

```typescript
// lib/notifications/rate-limiter.ts
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL!);

interface RateLimitConfig {
  maxPerHour: number;
  maxPerDay: number;
}

const LIMITS: Record<string, RateLimitConfig> = {
  marketing: { maxPerHour: 1, maxPerDay: 3 },
  product: { maxPerHour: 5, maxPerDay: 20 },
  security: { maxPerHour: 100, maxPerDay: 100 }, // No practical limit
  billing: { maxPerHour: 3, maxPerDay: 10 },
};

export async function checkRateLimit(
  userId: string,
  category: string,
  channel: string
): Promise<{ allowed: boolean; retryAfterMs?: number }> {
  const config = LIMITS[category] ?? LIMITS.product;
  const hourKey = `ratelimit:${userId}:${category}:${channel}:hour`;
  const dayKey = `ratelimit:${userId}:${category}:${channel}:day`;

  const [hourCount, dayCount] = await Promise.all([
    redis.incr(hourKey),
    redis.incr(dayKey),
  ]);

  // Set TTL on first increment
  if (hourCount === 1) await redis.expire(hourKey, 3600);
  if (dayCount === 1) await redis.expire(dayKey, 86400);

  if (hourCount > config.maxPerHour) {
    const ttl = await redis.ttl(hourKey);
    return { allowed: false, retryAfterMs: ttl * 1000 };
  }

  if (dayCount > config.maxPerDay) {
    const ttl = await redis.ttl(dayKey);
    return { allowed: false, retryAfterMs: ttl * 1000 };
  }

  return { allowed: true };
}
```

### Integrate Rate Limiting into Dispatch

```typescript
// In sendNotification(), before dispatching to each channel:
for (const channel of channels) {
  const { allowed, retryAfterMs } = await checkRateLimit(userId, category, channel);

  if (!allowed) {
    console.warn(
      `Rate limited: ${channel} notification for user ${userId} (${category}). Retry in ${retryAfterMs}ms`
    );
    // Optionally: queue with delay instead of dropping
    if (channel === "email") {
      await emailQueue.add("send", jobData, { delay: retryAfterMs });
    }
    continue;
  }

  // ... dispatch normally
}
```
