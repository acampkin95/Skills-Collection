---
name: email-notifications
description: Transactional email with Resend, React Email templates, and multi-channel notifications. Use for SPF/DKIM/DMARC, BullMQ queues, and batch email pipelines.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.