# Email Deliverability Reference

SPF, DKIM, DMARC configuration, bounce handling, reputation management, and warm-up strategies.

## Email Authentication Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Receiving Server                       │
│                                                          │
│  1. SPF Check  → Is sender IP authorized?                │
│  2. DKIM Check → Is signature valid?                     │
│  3. DMARC Check → Do SPF/DKIM align with From domain?   │
│  4. Reputation  → Is sender trusted?                     │
│  5. Content     → Does body look like spam?              │
│                                                          │
│  Result: Inbox / Spam / Reject                           │
└──────────────────────────────────────────────────────────┘
```

## SPF (Sender Policy Framework)

SPF tells receiving servers which IPs are allowed to send email for your domain.

### Setup

Add a TXT record to your root domain DNS:

```
Type: TXT
Host: @
Value: v=spf1 include:send.resend.com ~all
```

**Multiple senders** (e.g., Resend + Google Workspace):
```
v=spf1 include:send.resend.com include:_spf.google.com ~all
```

### SPF Syntax

| Mechanism | Meaning |
|-----------|---------|
| `include:domain.com` | Authorize domain's SPF |
| `ip4:1.2.3.4` | Authorize specific IPv4 |
| `ip6:2001:db8::1` | Authorize specific IPv6 |
| `a` | Authorize domain's A record IPs |
| `mx` | Authorize domain's MX IPs |
| `~all` | Soft fail (recommended) — deliver but flag |
| `-all` | Hard fail — reject unauthorized |

### SPF Debugging

```bash
# Check current SPF record
dig TXT yourdomain.com +short | grep spf

# Validate SPF (use online tools like mxtoolbox.com/spf.aspx)
# Common issues:
# - Too many DNS lookups (max 10) → flatten with ip4/ip6
# - Missing include for ESP
# - Multiple SPF records (only one allowed — merge them)
```

**DNS Lookup Limit:** SPF allows max 10 DNS lookups. Each `include:` counts as one. If you exceed 10, authentication fails silently.

```
# Count lookups:
# include:send.resend.com        → 1
# include:_spf.google.com        → +3 (nested includes)
# include:servers.mcsv.net       → +1
# Total: 5 lookups ✓
```

## DKIM (DomainKeys Identified Mail)

DKIM adds a cryptographic signature to outgoing emails, verifiable via DNS.

### Setup with Resend

Resend provides DKIM records during domain verification. Add the CNAME records they give you:

```
Type: CNAME
Host: resend._domainkey.yourdomain.com
Value: resend._domainkey.yourdomain.com.xxxxx.resend.com
```

Resend typically provides 3 CNAME records for DKIM. Add all of them.

### Verify DKIM

```bash
# Check DKIM record exists
dig CNAME resend._domainkey.yourdomain.com +short

# Test with a real email: send to check-auth@verifier.port25.com
# or check email headers for:
# dkim=pass header.d=yourdomain.com
```

### DKIM Alignment

For DMARC to pass via DKIM alignment, the `d=` domain in the DKIM signature must match (or be a subdomain of) the `From:` header domain.

```
From: notifications@yourdomain.com
DKIM-Signature: d=yourdomain.com  ← Aligned ✓
DKIM-Signature: d=send.resend.com ← Not aligned ✗
```

Resend supports custom DKIM signing with your domain (after domain verification).

## DMARC (Domain-based Message Authentication, Reporting & Conformance)

DMARC ties SPF and DKIM together and tells receivers what to do with failures.

### Setup

Add a TXT record:

```
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com; pct=100
```

### DMARC Policies (Progressive Rollout)

Start permissive and tighten over time:

**Week 1-2: Monitor only**
```
v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com; pct=100
```

**Week 3-4: Quarantine 25%**
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=25
```

**Week 5-6: Quarantine 100%**
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; pct=100
```

**Week 7+: Reject (full enforcement)**
```
v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com; ruf=mailto:dmarc-forensic@yourdomain.com; pct=100
```

### DMARC Tag Reference

| Tag | Required | Default | Meaning |
|-----|----------|---------|---------|
| `v` | Yes | — | Version (always `DMARC1`) |
| `p` | Yes | — | Policy: `none`, `quarantine`, `reject` |
| `rua` | No | — | Aggregate report email (daily XML) |
| `ruf` | No | — | Forensic report email (per-failure) |
| `pct` | No | 100 | % of messages to apply policy to |
| `sp` | No | Same as `p` | Subdomain policy |
| `adkim` | No | `r` | DKIM alignment: `s` (strict) or `r` (relaxed) |
| `aspf` | No | `r` | SPF alignment: `s` (strict) or `r` (relaxed) |

### DMARC Report Processing

Raw DMARC reports are XML. Use a service to parse them:
- **Postmark DMARC** (free, dmarc.postmarkapp.com)
- **DMARC Analyzer** (dmarcanalyzer.com)
- **Valimail** (enterprise)

## Bounce Handling

### Bounce Types

| Type | Description | Action |
|------|-------------|--------|
| Hard bounce | Address doesn't exist (550) | Remove immediately |
| Soft bounce | Mailbox full, server down (4xx) | Retry 3x, then suppress |
| Complaint | User clicked "Report Spam" | Unsubscribe immediately |

### Resend Webhook Handler

```typescript
// app/api/webhooks/resend/route.ts
import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export async function POST(req: NextRequest) {
  const body = await req.text();

  // Verify webhook signature
  const signature = req.headers.get("resend-signature");
  const timestamp = req.headers.get("resend-timestamp");

  if (!verifyWebhookSignature(body, signature, timestamp)) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  const event = JSON.parse(body);

  switch (event.type) {
    case "email.bounced": {
      const { to, bounce_type } = event.data;
      if (bounce_type === "hard") {
        // Permanently suppress this address
        await db.user.update({
          where: { email: to[0] },
          data: { emailBounced: true, emailBouncedAt: new Date() },
        });
        console.warn(`Hard bounce: ${to[0]} — suppressed`);
      } else {
        // Soft bounce — increment counter
        await db.user.update({
          where: { email: to[0] },
          data: { softBounceCount: { increment: 1 } },
        });
      }
      break;
    }

    case "email.complained": {
      const { to } = event.data;
      // User reported spam — unsubscribe immediately
      await db.notificationPreferences.update({
        where: { userId: (await db.user.findUnique({ where: { email: to[0] } }))?.id },
        data: { unsubscribedAll: true },
      });
      console.warn(`Spam complaint: ${to[0]} — unsubscribed`);
      break;
    }

    case "email.delivered":
      // Optional: track delivery for analytics
      break;

    case "email.opened":
      // Optional: track opens (pixel tracking)
      break;

    case "email.clicked":
      // Optional: track link clicks
      break;
  }

  return NextResponse.json({ received: true });
}

function verifyWebhookSignature(
  body: string,
  signature: string | null,
  timestamp: string | null
): boolean {
  if (!signature || !timestamp) return false;

  const expectedSignature = crypto
    .createHmac("sha256", process.env.RESEND_WEBHOOK_SECRET!)
    .update(`${timestamp}.${body}`)
    .digest("hex");

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

### Suppression List

```typescript
// lib/email/suppression.ts

/**
 * Check if an email is suppressed before sending.
 * Call this before every send.
 */
export async function isEmailSuppressed(email: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { email },
    select: {
      emailBounced: true,
      softBounceCount: true,
      notificationPreferences: { select: { unsubscribedAll: true } },
    },
  });

  if (!user) return true; // Unknown user
  if (user.emailBounced) return true; // Hard bounced
  if ((user.softBounceCount ?? 0) >= 3) return true; // Too many soft bounces
  if (user.notificationPreferences?.unsubscribedAll) return true; // Unsubscribed

  return false;
}
```

## Reputation Management

### Sender Reputation Factors

| Factor | Impact | How to Maintain |
|--------|--------|-----------------|
| Bounce rate | High | Remove invalid addresses; verify on signup |
| Complaint rate | Very High | One-click unsubscribe; respect preferences |
| Spam trap hits | Critical | Never buy lists; clean inactive users |
| Engagement | Medium | Send to engaged users; segment lists |
| Volume consistency | Medium | Gradual changes; avoid spikes |
| Authentication | High | SPF + DKIM + DMARC all passing |

### Key Metrics to Monitor

| Metric | Healthy Range | Alert Threshold |
|--------|---------------|-----------------|
| Bounce rate | < 2% | > 5% |
| Complaint rate | < 0.1% | > 0.3% |
| Open rate | > 20% | < 10% |
| Deliverability | > 95% | < 90% |

### Monitoring Tools

- **Google Postmaster Tools** — Reputation, spam rate, authentication for Gmail
- **Microsoft SNDS** — Delivery data for Outlook/Hotmail
- **Resend Dashboard** — Delivery, bounce, complaint analytics
- **MXToolbox** — DNS, blacklist, and deliverability checks

### Blacklist Recovery

If your domain or IP is blacklisted:

1. **Identify** — Check `mxtoolbox.com/blacklists.aspx`
2. **Fix root cause** — Stop whatever triggered it (spam, bounces, compromised account)
3. **Request delisting** — Each blacklist has a removal process
4. **Monitor** — Set up alerts for future listings

## Warm-Up Strategies

When sending from a new domain or IP, ISPs have no reputation data. Sending too much too fast triggers spam filters.

### IP/Domain Warm-Up Schedule

| Day | Daily Volume | Notes |
|-----|-------------|-------|
| 1-3 | 50 | Send to your most engaged users only |
| 4-7 | 100 | Expand to recently active users |
| 8-14 | 250 | Monitor bounce/complaint rates |
| 15-21 | 500 | Check Google Postmaster reputation |
| 22-30 | 1,000 | Evaluate and adjust |
| 31-45 | 2,500 | Scale if metrics are healthy |
| 46-60 | 5,000 | Approach target volume |
| 60+ | Target volume | Maintain consistent sending |

### Warm-Up Best Practices

1. **Start with engaged users** — Send first to users who opened emails in the last 30 days
2. **Clean your list first** — Remove bounced, unsubscribed, and inactive (>6 months) addresses
3. **Authenticate fully** — SPF, DKIM, DMARC all passing before you start
4. **Consistent schedule** — Send daily at similar times; avoid weekend-only spikes
5. **Monitor daily** — Check bounce rate, complaints, and Google Postmaster Tools
6. **Pause if degraded** — If bounce rate > 5% or complaint rate > 0.3%, reduce volume

### Warm-Up with Resend

Resend uses shared IP pools by default, which have existing reputation. If you're on a dedicated IP (enterprise plan), warm-up is critical:

```typescript
// lib/email/warmup.ts
const WARMUP_SCHEDULE = [
  { day: 1, maxEmails: 50 },
  { day: 4, maxEmails: 100 },
  { day: 8, maxEmails: 250 },
  { day: 15, maxEmails: 500 },
  { day: 22, maxEmails: 1000 },
  { day: 31, maxEmails: 2500 },
  { day: 46, maxEmails: 5000 },
];

export function getWarmupLimit(startDate: Date): number {
  const daysSinceStart = Math.floor(
    (Date.now() - startDate.getTime()) / (24 * 60 * 60 * 1000)
  );

  // Find the applicable limit
  const applicable = WARMUP_SCHEDULE
    .filter((s) => daysSinceStart >= s.day)
    .pop();

  return applicable?.maxEmails ?? 50;
}

export async function getDailySendCount(): Promise<number> {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return db.notification.count({
    where: {
      channel: "email",
      status: { in: ["SENT", "DELIVERED"] },
      sentAt: { gte: today },
    },
  });
}
```

## Email Authentication Debugging

### Complete Debug Checklist

```bash
# 1. Check SPF record
dig TXT yourdomain.com +short
# Expected: "v=spf1 include:send.resend.com ~all"

# 2. Check DKIM records
dig CNAME resend._domainkey.yourdomain.com +short
# Expected: Points to resend's DKIM server

# 3. Check DMARC record
dig TXT _dmarc.yourdomain.com +short
# Expected: "v=DMARC1; p=quarantine; ..."

# 4. Check MX records (for bounce handling)
dig MX yourdomain.com +short

# 5. Check for blacklisting
# Visit: mxtoolbox.com/blacklists.aspx

# 6. Send test email and check headers
# In Gmail: Open email → "..." → "Show original"
# Look for:
#   SPF: PASS
#   DKIM: PASS
#   DMARC: PASS
```

### Common Issues and Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| SPF permerror | Too many DNS lookups | Flatten nested includes to `ip4:`/`ip6:` |
| SPF softfail | `~all` not matching | Add ESP's `include:` to SPF record |
| DKIM fail | Signature doesn't verify | Re-add CNAME records; check propagation |
| DMARC fail | SPF or DKIM not aligned | Ensure `From:` domain matches SPF/DKIM domain |
| Going to spam | Low reputation | Check Postmaster Tools; reduce volume; warm up |
| Delayed delivery | Greylisting | Normal for new senders; resolves after retry |
| Bouncing | 550 user unknown | Remove address from list; check for typos |
| Missing in inbox | Tabs/categories | Improve engagement; avoid marketing language |

### Header Analysis

When debugging, check the `Authentication-Results` header:

```
Authentication-Results: mx.google.com;
  dkim=pass header.d=yourdomain.com header.s=resend;
  spf=pass (google.com: domain of bounce@send.resend.com designates 1.2.3.4 as permitted sender) smtp.mailfrom=bounce@send.resend.com;
  dmarc=pass (p=QUARANTINE sp=QUARANTINE dis=NONE) header.from=yourdomain.com
```

All three should show `pass`. If any show `fail`, `softfail`, or `temperror`, fix that layer first.
