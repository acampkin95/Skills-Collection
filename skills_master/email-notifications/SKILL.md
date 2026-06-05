---
name: email-notifications
description: Transactional email sending with Resend, React Email templates.
---

# Email Notifications Skill

Transactional email sending with Resend, email templating with React Email v5, and notification system architecture for Next.js applications.

## Core Stack

| Layer | Tool | Purpose |
|-------|------|---------
| Sending | Resend | Transactional email API (email receiving 2025+) |
| Templates | React Email v5 | JSX email components with Tailwind v4 |
| Queue | BullMQ + Redis | Async email processing |
| Auth | SPF/DKIM/DMARC | Email authentication |

## Resend SDK Setup (2025+)

### Installation

```bash
npm install resend react-email @react-email/components
```

### Environment Variables

```env
RESEND_API_KEY=re_xxxxxxxxxxxx
EMAIL_FROM=notifications@yourdomain.com
```

### Basic Client

```typescript
import { Resend } from "resend";

export const resend = new Resend(process.env.RESEND_API_KEY);
```

### 2025 Features: Email Receiving & Idempotency

Resend now supports **receiving emails** (2025) and **idempotency keys** for reliable delivery at scale:

```typescript
// Send with idempotency key to prevent duplicate sends
const { data, error } = await resend.emails.send({
  from: process.env.EMAIL_FROM!,
  to: "user@example.com",
  subject: "Welcome",
  react: WelcomeEmail({ name: "Alice" }),
  idempotencyKey: "unique-key-per-send",
});
```

## React Email v5 Components (Tailwind v4 Compatible)

React Email v5 (2025+) supports Tailwind CSS v4 and React 19. Key components from `@react-email/components`:

| Component | Purpose |
|-----------|---------|
| `Html` | Root wrapper, sets `dir` and `lang` |
| `Head` | Email `<head>`, fonts and meta |
| `Preview` | Preview text in inbox list |
| `Body` | Email body with base styles |
| `Container` | Centered content wrapper (max-width) |
| `Section` | Grouping element |
| `Row` / `Column` | Table-based layout |
| `Text` | Paragraph with inline styles |
| `Heading` | Heading elements |
| `Button` | CTA button with link |
| `Link` | Anchor element |
| `Img` | Image with absolute URL |
| `Hr` | Horizontal rule |
| `Tailwind` | Apply Tailwind CSS utilities to email |

### Email Template Pattern (Tailwind v4)

```tsx
import {
  Html, Head, Preview, Body, Container, Section,
  Text, Button, Img, Link, Hr, Tailwind,
} from "@react-email/components";

export default function WelcomeEmail({ name, actionUrl }) {
  return (
    <Html lang="en" dir="ltr">
      <Head />
      <Preview>Welcome to our platform, {name}!</Preview>
      <Tailwind>
        <Body className="bg-slate-50 font-sans">
          <Container className="mx-auto max-w-md bg-white rounded-lg p-10">
            <Section className="py-6">
              <Text className="text-2xl font-bold text-slate-900">
                Welcome, {name}!
              </Text>
              <Button
                href={actionUrl}
                className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md"
              >
                Get Started
              </Button>
            </Section>
            <Hr className="border-slate-200 my-8" />
            <Text className="text-xs text-slate-500">
              <Link href="https://yourdomain.com/unsubscribe">Unsubscribe</Link>
            </Text>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

## Sending Emails from Next.js

### Server Action Pattern

```typescript
"use server";
import { resend } from "@/lib/resend";
import WelcomeEmail from "@/emails/welcome";

export async function sendWelcomeEmail(userId: string, email: string, name: string) {
  const { data, error } = await resend.emails.send({
    from: process.env.EMAIL_FROM!,
    to: email,
    subject: `Welcome to the platform, ${name}!`,
    react: WelcomeEmail({ name, actionUrl: `${process.env.NEXT_PUBLIC_APP_URL}/onboarding` }),
    idempotencyKey: `welcome-${userId}-${Date.now()}`,
  });

  if (error) return { success: false, error: error.message };
  return { success: true, messageId: data?.id };
}
```

### Webhook Pattern

```typescript
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();

  switch (body.type) {
    case "email.delivered":
      // Update delivery status
      break;
    case "email.bounced":
      // Handle bounce - mark address invalid
      break;
    case "email.complained":
      // Handle complaint - unsubscribe user
      break;
  }

  return NextResponse.json({ received: true });
}
```

## Email Verification Flow

```typescript
import crypto from "crypto";
import { resend } from "@/lib/resend";

export async function sendVerificationEmail(email: string) {
  const token = crypto.randomBytes(32).toString("hex");
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);

  await db.verificationToken.create({ data: { email, token, expiresAt } });

  const verifyUrl = `${process.env.NEXT_PUBLIC_APP_URL}/verify-email?token=${token}`;

  await resend.emails.send({
    from: process.env.EMAIL_FROM!,
    to: email,
    subject: "Verify your email address",
    react: VerificationEmail({ verifyUrl }),
    idempotencyKey: `verify-${email}-${token}`,
  });
}

export async function verifyEmail(token: string) {
  const record = await db.verificationToken.findUnique({ where: { token } });
  if (!record || record.expiresAt < new Date()) {
    return { success: false, error: "Invalid or expired token" };
  }

  await db.user.update({
    where: { email: record.email },
    data: { emailVerified: new Date() },
  });

  await db.verificationToken.delete({ where: { token } });
  return { success: true };
}
```

## Email Authentication (SPF/DKIM/DMARC)

### DNS Records

When using Resend, add these DNS records to your domain:

**SPF** (TXT record on root domain):
```
v=spf1 include:send.resend.com ~all
```

**DKIM** (CNAME records — Resend provides these in dashboard):
```
resend._domainkey.yourdomain.com → provided-value.resend.com
```

**DMARC** (TXT record on `_dmarc.yourdomain.com`):
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=100
```

### Verification Checklist

1. Domain verified in Resend dashboard (green checkmarks for SPF, DKIM, DMARC)
2. DNS propagation complete (check with `dig TXT yourdomain.com`)
3. Test email passes authentication headers (`spf=pass`, `dkim=pass`, `dmarc=pass`)

See [deliverability reference](references/deliverability.md) for authentication debugging and warm-up strategies.

## Notification System Design

### Multi-Channel Dispatch

```typescript
type Channel = "email" | "inApp" | "push";
type Category = "marketing" | "product" | "security" | "billing";

interface NotificationPayload {
  userId: string;
  category: Category;
  title: string;
  body: string;
  actionUrl?: string;
  emailTemplate?: React.ReactElement;
}

export async function sendNotification(payload: NotificationPayload) {
  const prefs = await getPreferences(payload.userId);
  const user = await getUser(payload.userId);
  const channels: Channel[] = [];

  if (payload.category === "security") {
    channels.push("email", "inApp", "push");
  } else {
    const catPrefs = prefs.categories[payload.category];
    if (catPrefs.email && prefs.channels.email) channels.push("email");
    if (catPrefs.inApp && prefs.channels.inApp) channels.push("inApp");
    if (catPrefs.push && prefs.channels.push) channels.push("push");
  }

  return Promise.allSettled(channels.map(channel => sendViaChannel(channel, payload)));
}
```

### Queue-Based Architecture (BullMQ)

```typescript
import { Queue, Worker } from "bullmq";
import Redis from "ioredis";

const connection = new Redis(process.env.REDIS_URL!);
export const emailQueue = new Queue("email", { connection });

export async function queueEmail(params: {
  to: string;
  subject: string;
  templateName: string;
  templateProps: Record<string, unknown>;
}) {
  await emailQueue.add("send", params, {
    attempts: 3,
    backoff: { type: "exponential", delay: 5000 },
    removeOnComplete: 1000,
    removeOnFail: 5000,
  });
}

// Worker process
const worker = new Worker(
  "email",
  async (job) => {
    const { to, subject, templateName, templateProps } = job.data;
    const template = await loadTemplate(templateName, templateProps);

    const { error } = await resend.emails.send({
      from: process.env.EMAIL_FROM!,
      to,
      subject,
      react: template,
      idempotencyKey: `job-${job.id}`,
    });

    if (error) throw new Error(error.message);
  },
  { connection, concurrency: 10, limiter: { max: 50, duration: 1000 } }
);

worker.on("failed", (job, err) => {
  console.error(`Email job ${job?.id} failed:`, err.message);
});
```

See [notification systems reference](references/notification-systems.md) for digest emails, rate limiting, and advanced queue patterns.

See [React Email reference](references/react-email.md) for responsive patterns, dark mode, Tailwind v4 integration, and testing.
