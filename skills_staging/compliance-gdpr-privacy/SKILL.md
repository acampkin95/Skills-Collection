---
name: compliance-gdpr-privacy
description: GDPR, CCPA/CPRA, and ePrivacy compliance with consent management, data subject rights, cookie consent, breach notification, and audit logging.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.