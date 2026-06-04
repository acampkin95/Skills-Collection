# Data Mapping & GDPR Documentation

## Data Flow Diagram

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  User Input  │───►│  Application │───►│  Database    │
│  (Forms/API) │    │  Server      │    │  (Primary)   │
└─────────────┘    └──────┬───────┘    └──────┬──────┘
                          │                    │
                          ▼                    ▼
                   ┌──────────────┐    ┌─────────────┐
                   │  3rd Party   │    │  Backups     │
                   │  Services    │    │  (Encrypted) │
                   └──────────────┘    └─────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌────────┐ ┌──────────┐
        │ Analytics│ │ Email  │ │ Payment  │
        │ (GA)     │ │ (SMTP) │ │ (Stripe) │
        └──────────┘ └────────┘ └──────────┘
```

## Records of Processing Activities (ROPA)

### Template

```typescript
interface ProcessingActivity {
  id: string;
  name: string;
  description: string;
  controller: {
    name: string;
    contact: string;
    dpo?: string;                    // Data Protection Officer
  };
  purposes: string[];
  lawfulBasis: 'consent' | 'contract' | 'legal-obligation' | 'legitimate-interest';
  dataCategories: string[];          // Types of personal data
  dataSubjects: string[];            // Whose data (customers, employees, etc.)
  recipients: string[];              // Who receives the data
  thirdCountryTransfers?: {
    country: string;
    safeguard: string;               // SCCs, adequacy decision, etc.
  }[];
  retentionPeriod: string;
  securityMeasures: string[];
  automatedDecisionMaking: boolean;
  dpiaConducted: boolean;
  lastReviewed: string;
}
```

### Example ROPA Entry

```typescript
const userAccountProcessing: ProcessingActivity = {
  id: 'proc-001',
  name: 'User Account Management',
  description: 'Creating and managing user accounts, including authentication and profile data',
  controller: {
    name: 'Example Ltd',
    contact: 'privacy@example.com',
    dpo: 'dpo@example.com',
  },
  purposes: [
    'Provide user account functionality',
    'Authentication and authorization',
    'Customer support',
  ],
  lawfulBasis: 'contract',
  dataCategories: [
    'Name',
    'Email address',
    'Hashed password',
    'Profile picture (optional)',
    'Account preferences',
  ],
  dataSubjects: ['Registered users'],
  recipients: [
    'Internal: Engineering team (via application)',
    'Internal: Support team (via admin panel)',
    'External: AWS (hosting)',
    'External: SendGrid (transactional email)',
  ],
  thirdCountryTransfers: [
    { country: 'USA', safeguard: 'EU-US Data Privacy Framework' },
  ],
  retentionPeriod: 'Duration of account + 30 days after deletion request',
  securityMeasures: [
    'Encryption at rest (AES-256)',
    'TLS 1.3 in transit',
    'Bcrypt password hashing',
    'Role-based access control',
    'Audit logging',
  ],
  automatedDecisionMaking: false,
  dpiaConducted: false,
  lastReviewed: '2025-01-15',
};
```

## Third-Party Processor Audit

### Processor Registry

```typescript
interface DataProcessor {
  name: string;
  purpose: string;
  dataProcessed: string[];
  location: string;
  transferMechanism?: string;
  dpaSignedDate: string;            // Data Processing Agreement
  subProcessors: string[];
  securityCertifications: string[];
  lastAuditDate: string;
  riskLevel: 'low' | 'medium' | 'high';
}

const processors: DataProcessor[] = [
  {
    name: 'AWS',
    purpose: 'Cloud infrastructure hosting',
    dataProcessed: ['All user data (stored in eu-west-1)'],
    location: 'Ireland (eu-west-1)',
    dpaSignedDate: '2024-03-15',
    subProcessors: [],
    securityCertifications: ['SOC 2', 'ISO 27001', 'GDPR compliant'],
    lastAuditDate: '2024-12-01',
    riskLevel: 'low',
  },
  {
    name: 'Stripe',
    purpose: 'Payment processing',
    dataProcessed: ['Name', 'Email', 'Payment card (tokenized)', 'Billing address'],
    location: 'USA',
    transferMechanism: 'EU-US Data Privacy Framework',
    dpaSignedDate: '2024-04-01',
    subProcessors: ['Plaid (bank verification)'],
    securityCertifications: ['PCI DSS Level 1', 'SOC 2'],
    lastAuditDate: '2024-11-15',
    riskLevel: 'low',
  },
  {
    name: 'SendGrid',
    purpose: 'Transactional and marketing email',
    dataProcessed: ['Name', 'Email', 'Email engagement (opens, clicks)'],
    location: 'USA',
    transferMechanism: 'Standard Contractual Clauses',
    dpaSignedDate: '2024-05-01',
    subProcessors: [],
    securityCertifications: ['SOC 2'],
    lastAuditDate: '2024-10-20',
    riskLevel: 'medium',
  },
];
```

## Data Retention Schedules

```typescript
const retentionSchedule = {
  // Active data
  userProfile: {
    retention: 'Account lifetime + 30 days',
    deletionTrigger: 'Account deletion request or inactivity > 2 years',
    action: 'Hard delete',
  },
  activityLogs: {
    retention: '12 months',
    deletionTrigger: 'Automated monthly cleanup',
    action: 'Hard delete',
  },
  sessionData: {
    retention: '30 days',
    deletionTrigger: 'Automated daily cleanup',
    action: 'Hard delete',
  },

  // Legal retention
  invoices: {
    retention: '7 years (tax law)',
    deletionTrigger: 'Automated after retention period',
    action: 'Archive then delete',
  },
  consentRecords: {
    retention: '5 years after last interaction',
    deletionTrigger: 'Manual review',
    action: 'Archive then delete',
  },

  // Security
  auditLogs: {
    retention: '3 years',
    deletionTrigger: 'Automated quarterly cleanup',
    action: 'Hard delete',
  },
  securityIncidents: {
    retention: '5 years',
    deletionTrigger: 'Manual review',
    action: 'Anonymize then archive',
  },
};
```

### Automated Retention Enforcement

```typescript
// Cron job: Run daily
async function enforceRetention(): Promise<void> {
  const now = new Date();

  // Delete expired sessions
  await db.sessions.deleteMany({
    lastActive: { $lt: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) },
  });

  // Delete old activity logs
  await db.activityLogs.deleteMany({
    createdAt: { $lt: new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000) },
  });

  // Flag inactive accounts for review
  const inactiveUsers = await db.users.find({
    lastLogin: { $lt: new Date(now.getTime() - 2 * 365 * 24 * 60 * 60 * 1000) },
    inactiveNotified: { $ne: true },
  });

  for (const user of inactiveUsers) {
    await sendInactivityNotice(user.email);
    await db.users.updateOne(
      { _id: user._id },
      { $set: { inactiveNotified: true, notifiedAt: now } }
    );
  }

  console.log(`Retention cleanup completed at ${now.toISOString()}`);
}
```

## DSAR (Data Subject Access Request) Automation

```typescript
interface DSARRequest {
  id: string;
  type: 'access' | 'erasure' | 'rectification' | 'portability' | 'restriction' | 'objection';
  userId: string;
  email: string;
  receivedAt: string;
  dueDate: string;           // 30 days from receipt
  status: 'received' | 'verified' | 'processing' | 'completed' | 'rejected';
  completedAt?: string;
  notes?: string;
}

// API: POST /api/dsar
async function handleDSAR(request: DSARRequest): Promise<void> {
  // 1. Verify identity (email confirmation + ID check)
  await sendVerificationEmail(request.email, request.id);

  // 2. Log the request
  await db.dsarRequests.insert({
    ...request,
    receivedAt: new Date().toISOString(),
    dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'received',
  });

  // 3. Notify DPO
  await notifyDPO(`New ${request.type} request from ${request.email}`);
}

// After identity verification
async function processDSAR(requestId: string): Promise<void> {
  const request = await db.dsarRequests.findOne({ id: requestId });
  if (!request) throw new Error('Request not found');

  await db.dsarRequests.updateOne({ id: requestId }, { $set: { status: 'processing' } });

  switch (request.type) {
    case 'access':
    case 'portability':
      const data = await exportUserData(request.userId);
      await sendSecureDownloadLink(request.email, data);
      break;

    case 'erasure':
      await deleteUserData(request.userId);
      await sendConfirmation(request.email, 'Your data has been deleted.');
      break;

    case 'rectification':
      // Requires manual review — notify support team
      await createSupportTicket(request);
      break;

    case 'restriction':
      await db.users.updateOne(
        { id: request.userId },
        { $set: { processingRestricted: true, restrictedAt: new Date() } }
      );
      break;
  }

  await db.dsarRequests.updateOne(
    { id: requestId },
    { $set: { status: 'completed', completedAt: new Date().toISOString() } }
  );
}
```

## Anonymization & Pseudonymization

```typescript
import { createHash, randomBytes } from 'crypto';

// Pseudonymization: Reversible with key
function pseudonymize(value: string, key: string): string {
  return createHash('sha256').update(value + key).digest('hex').slice(0, 16);
}

// Anonymization: Irreversible
function anonymizeUser(user: any): any {
  return {
    ...user,
    name: 'Anonymous',
    email: `anon-${randomBytes(8).toString('hex')}@deleted`,
    ip: user.ip ? user.ip.replace(/\d+$/, '0') : null,  // Zero last octet
    phone: null,
    address: user.address ? { country: user.address.country } : null, // Keep only country
    dateOfBirth: user.dateOfBirth
      ? new Date(user.dateOfBirth).getFullYear().toString() // Keep only year
      : null,
  };
}

// K-anonymity: Generalize data so each record matches at least K others
function generalizeAge(age: number): string {
  if (age < 18) return '<18';
  if (age < 25) return '18-24';
  if (age < 35) return '25-34';
  if (age < 45) return '35-44';
  if (age < 55) return '45-54';
  if (age < 65) return '55-64';
  return '65+';
}
```
