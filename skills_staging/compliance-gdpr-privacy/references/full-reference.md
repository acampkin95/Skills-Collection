---
name: compliance-gdpr-privacy
description: GDPR, CCPA/CPRA, and ePrivacy compliance implementation with consent management and data protection. Use this skill when GDPR compliance, CCPA/CPRA, data subject access, right to erasure, cookie consent, Google Consent Mode v2, breach notification, lawful basis, data protection, privacy-by-design, data portability, audit logging, ePrivacy directive. Use this skill when implementing consent management systems, handling data subject access requests, ensuring EU/California regulatory compliance, managing cookie consent, establishing audit logging for data processing, designing privacy-first architectures, handling breach notifications within 72 hours, and validating lawful bases for data processing.
---

# GDPR & Privacy Compliance

## GDPR Overview

GDPR applies when:
- You process personal data of EU/EEA residents
- Your organization is established in the EU
- You offer goods/services to EU residents
- You monitor behavior of EU residents

**Personal data**: name, email, IP address, cookies, device IDs, and any identifiable information.

## Lawful Bases for Processing

| Basis | When to Use | Example |
|-------|-------------|---------|
| Consent | User explicitly agrees | Marketing emails, analytics |
| Contract | Necessary for a contract | Payment processing, account creation |
| Legal obligation | Required by law | Tax records, AML checks |
| Vital interests | Protect someone's life | Emergency medical data |
| Public task | Public authority function | Government services |
| Legitimate interest | Balanced business need | Fraud prevention, security |

### Consent Requirements

Valid consent must be:
- **Freely given** (no forced bundling)
- **Specific** (separate consent per purpose)
- **Informed** (clear what they're agreeing to)
- **Unambiguous** (affirmative action only)
- **Withdrawable** (as easy to withdraw as give)

```typescript
interface ConsentRecord {
  userId: string;
  purposes: { analytics: boolean; marketing: boolean; personalization: boolean };
  timestamp: string;
  method: 'banner' | 'settings' | 'signup';
  version: string;
  ipAddress?: string;
}

async function recordConsent(consent: ConsentRecord): Promise<void> {
  await db.consents.insert({
    ...consent,
    timestamp: new Date().toISOString(),
  });
}
```

## Data Subject Rights

| Right | Response Time | Implementation |
|-------|--------------|----------------|
| Access (Art. 15) | 30 days | Export all personal data |
| Rectification (Art. 16) | 30 days | Allow data correction |
| Erasure (Art. 17) | 30 days | Delete data ("right to be forgotten") |
| Restrict processing (Art. 18) | 30 days | Flag as restricted |
| Portability (Art. 20) | 30 days | Export in machine-readable format |
| Object (Art. 21) | 30 days | Stop processing |
| No automated decisions (Art. 22) | 30 days | Human review required |

### Data Export

```typescript
interface UserDataExport {
  profile: { name: string; email: string; createdAt: string };
  activity: Array<{ action: string; timestamp: string }>;
  preferences: Record<string, unknown>;
  exportedAt: string;
}

async function exportUserData(userId: string): Promise<UserDataExport> {
  const [profile, activity, preferences] = await Promise.all([
    db.users.findOne({ id: userId }),
    db.activity.find({ userId }).toArray(),
    db.preferences.findOne({ userId }),
  ]);

  return {
    profile: { name: profile.name, email: profile.email, createdAt: profile.createdAt },
    activity,
    preferences: preferences?.settings || {},
    exportedAt: new Date().toISOString(),
  };
}
```

### Data Deletion

```typescript
async function deleteUserData(userId: string): Promise<DeletionReport> {
  const report = { userId, deletedAt: new Date().toISOString(), tables: [] };

  const tables = ['users', 'activity', 'preferences', 'sessions', 'consents'];
  for (const table of tables) {
    const result = await db[table].deleteMany({ userId });
    report.tables.push({ table, deletedCount: result.deletedCount });
  }

  await analyticsService.deleteUser(userId);
  await emailService.deleteSubscriber(userId);

  // Keep minimal deletion log for compliance
  await db.deletionLog.insert({
    hashedUserId: hashUserId(userId),
    deletedAt: report.deletedAt,
  });

  await sessionStore.destroyAll(userId);
  return report;
}
```

## Cookie Consent

### Categories

| Category | Requires Consent | Examples |
|----------|-----------------|----------|
| Strictly necessary | No | Session cookies, CSRF tokens, auth |
| Functional | Yes (some regions) | Language, UI settings |
| Analytics | Yes | Google Analytics, Plausible |
| Marketing | Yes | Facebook Pixel, Google Ads |

### Consent Banner Pattern

```typescript
type CookieCategory = 'necessary' | 'functional' | 'analytics' | 'marketing';

interface CookieConsent {
  necessary: true;
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
  timestamp: number;
  version: string;
}

const DEFAULT_CONSENT: CookieConsent = {
  necessary: true,
  functional: false,
  analytics: false,
  marketing: false,
  timestamp: 0,
  version: '1.0',
};

function getConsent(): CookieConsent | null {
  try {
    const stored = localStorage.getItem('cookie-consent');
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

function setConsent(consent: Partial<CookieConsent>): void {
  const full: CookieConsent = {
    ...DEFAULT_CONSENT,
    ...consent,
    necessary: true,
    timestamp: Date.now(),
  };
  localStorage.setItem('cookie-consent', JSON.stringify(full));
  applyConsent(full);
}

function applyConsent(consent: CookieConsent): void {
  if (consent.analytics) {
    loadScript('https://www.googletagmanager.com/gtag/js?id=GA_ID');
  }
  if (consent.marketing) {
    loadScript('https://connect.facebook.net/en_US/fbevents.js');
  }

  // Google Consent Mode v2
  window.gtag?.('consent', 'update', {
    analytics_storage: consent.analytics ? 'granted' : 'denied',
    ad_storage: consent.marketing ? 'granted' : 'denied',
    ad_personalization: consent.marketing ? 'granted' : 'denied',
  });
}
```

## CCPA/CPRA (California)

### Key Requirements

| Requirement | Rule |
|-------------|------|
| Right to know | Disclose data collected in past 12 months |
| Right to delete | Delete on request (with exceptions) |
| Right to opt-out | "Do Not Sell or Share My Personal Information" link |
| Right to correct | Added by CPRA (2023) |
| Right to limit use | Limit use of sensitive personal info |
| Non-discrimination | Cannot penalize users who exercise rights |

### Implementation

```typescript
interface CCPAPreferences {
  doNotSell: boolean;
  doNotShare: boolean;
  limitSensitiveUse: boolean;
  updatedAt: string;
}

function applyCCPAPreferences(prefs: CCPAPreferences): void {
  if (prefs.doNotSell || prefs.doNotShare) {
    disableScript('facebook-pixel');
    disableScript('google-ads');
    window.__gpp?.('setConsent', { SaleOptOut: true, ShareOptOut: true });
  }
}

// Respect Global Privacy Control header
const gpcEnabled = navigator.globalPrivacyControl === true;
if (gpcEnabled) {
  applyCCPAPreferences({
    doNotSell: true,
    doNotShare: true,
    limitSensitiveUse: false,
    updatedAt: new Date().toISOString(),
  });
}
```

## Data Breach Notification

### 72-Hour Rule (GDPR Art. 33)

```
Discovery → Assess severity → Notify DPA (72h) → Notify users (if high risk)
```

```typescript
interface DataBreach {
  id: string;
  discoveredAt: string;
  description: string;
  dataTypes: string[];
  affectedCount: number;
  riskLevel: 'low' | 'medium' | 'high';
  mitigationSteps: string[];
  dpaNotifiedAt?: string;
  usersNotifiedAt?: string;
  containedAt?: string;
}

function assessBreachRisk(breach: Omit<DataBreach, 'riskLevel'>): 'low' | 'medium' | 'high' {
  const sensitiveTypes = ['financial', 'health', 'credentials', 'ssn'];
  const hasSensitive = breach.dataTypes.some(t => sensitiveTypes.includes(t));
  if (hasSensitive && breach.affectedCount > 1000) return 'high';
  if (hasSensitive || breach.affectedCount > 100) return 'medium';
  return 'low';
}
```

## Audit Logging

```typescript
interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: 'view' | 'export' | 'modify' | 'delete' | 'consent_change';
  resource: string;
  ipAddress: string;
  userAgent: string;
}

class AuditLogger {
  async log(entry: Omit<AuditEntry, 'id' | 'timestamp'>): Promise<void> {
    await db.auditLog.insert({
      ...entry,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
    });
  }

  async getByUser(userId: string, from?: Date, to?: Date): Promise<AuditEntry[]> {
    return db.auditLog.find({
      $or: [{ actor: userId }, { resource: { $regex: `user:${userId}` } }],
      ...(from && { timestamp: { $gte: from.toISOString() } }),
      ...(to && { timestamp: { $lte: to.toISOString() } }),
    }).sort({ timestamp: -1 }).toArray();
  }
}
```

Log: data access, modifications, consent changes, DSAR requests, authentication events, admin access.
Retention: minimum 3 years.

## Privacy-by-Design: 7 Principles

| Principle | Implementation |
|-----------|----------------|
| Proactive, not reactive | Threat model personal data flows |
| Privacy as default | Analytics OFF by default; opt-in |
| Privacy embedded in design | Encrypt PII at rest; hash where possible |
| Full functionality | Allow service with minimal data |
| End-to-end security | TLS everywhere; AES-256 at rest |
| Visibility & transparency | Public policy; consent receipts |
| Respect for user privacy | User-friendly controls; clear settings |

### Implementation Checklist

- [ ] Data minimization: Only collect what needed
- [ ] Purpose limitation: Use data only for stated purposes
- [ ] Storage limitation: Define retention; auto-delete
- [ ] Encryption: TLS in transit, AES-256 at rest
- [ ] Access controls: Role-based least privilege
- [ ] Audit logging: Immutable trail of access
- [ ] Pseudonymization: Replace identifiers where possible
- [ ] Default privacy: Restrictive settings by default
- [ ] Consent records: Store proof with timestamp
- [ ] Breach plan: Documented incident response
- [ ] Data retention schedule: Auto-purge
- [ ] Privacy impact assessment: DPIA for high-risk activities

## Third-Party Vendor Management

### Data Processing Agreement (DPA)

Every vendor needs a DPA covering:
- Subject matter, duration, nature, purpose of processing
- Types of personal data and data subjects
- Obligations and rights of controller
- Sub-processor approval process
- Data breach notification obligations
- Audit rights

### Sub-Processor List

```typescript
interface SubProcessor {
  name: string;
  purpose: string;
  dataTypes: string[];
  location: string;
  transferMechanism?: string;
  dpaSignedAt: string;
}

const subProcessors: SubProcessor[] = [
  {
    name: "AWS",
    purpose: "Cloud hosting",
    dataTypes: ["all user data"],
    location: "EU (Frankfurt)",
    transferMechanism: "EU region only",
    dpaSignedAt: "2024-01-15",
  },
  {
    name: "SendGrid",
    purpose: "Transactional email",
    dataTypes: ["email", "name"],
    location: "US",
    transferMechanism: "EU-US Data Privacy Framework",
    dpaSignedAt: "2024-02-01",
  },
];
```

## Children's Data (COPPA/GDPR)

### Requirements

| Requirement | Implementation |
|-------------|----------------|
| Parental consent | Before collecting from under-13 (COPPA) / under-16 (GDPR) |
| Limited collection | Only what's reasonably necessary |
| No behavioral ads | Cannot serve targeted ads to children |
| Data deletion | Parents can request deletion |
| Reasonable security | Appropriate data protection measures |

```typescript
async function checkAge(birthdate: Date): Promise<'adult' | 'teen' | 'child'> {
  const age = Math.floor((Date.now() - birthdate.getTime()) / (365.25 * 24 * 60 * 60 * 1000));
  if (age >= 18) return 'adult';
  if (age >= 13) return 'teen';
  return 'child';
}

const digitalConsentAge: Record<string, number> = {
  UK: 13, ES: 14, FR: 15, DE: 16, NL: 16, IE: 16, IT: 14,
};

function requiresParentalConsent(age: number, country: string): boolean {
  const threshold = digitalConsentAge[country] || 16;
  return age < threshold;
}
```

See [references/cookie-consent.md](references/cookie-consent.md) for detailed consent banner and Google Consent Mode v2.

See [references/data-mapping.md](references/data-mapping.md) for ROPA templates, DSAR automation, and data flows.
