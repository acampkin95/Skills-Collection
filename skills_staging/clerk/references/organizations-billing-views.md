# Clerk — Organizations, Billing, Views & Framework SDKs

## Organizations (Multi-Tenant RBAC)

Organizations are shared accounts with role-based access control.

```typescript
import { auth, clerkClient } from '@clerk/nextjs/server'

export async function GET() {
  const { userId, orgId, orgRole, orgPermissions } = await auth()

  if (!orgId) {
    return Response.json({ error: 'No active organization' }, { status: 403 })
  }

  const org = await (await clerkClient()).organizations.getOrganization({ organizationId: orgId })
  return Response.json({ org, role: orgRole, permissions: orgPermissions })
}
```

### Organization Roles

| Role | Permissions |
|------|------------|
| `org:admin` | Full control — members, settings, billing |
| `org:member` | Default — access org resources |
| Custom roles | Define via Dashboard > Organizations > Roles |

### Organization Webhooks

```typescript
case 'organization.created':
  await db.organization.create({
    data: { clerkId: evt.data.id, name: evt.data.name, slug: evt.data.slug }
  })
  break
case 'organizationMembership.created':
  await db.member.create({
    data: { userId: evt.data.public_user_data.user_id, orgId: evt.data.organization.id, role: evt.data.role }
  })
  break
```

### Organization Switching

```typescript
import { OrganizationSwitcher } from '@clerk/nextjs'

export function Nav() {
  return <OrganizationSwitcher afterCreateOrganizationUrl="/org-dashboard" />
}
```

## Clerk Billing

Built-in billing for B2C and B2B with subscription plans, free trials, and webhook events.

### Setup

1. Connect Stripe in Dashboard > Billing
2. Define plans (free, pro, enterprise)
3. Use webhooks to sync subscription status

```typescript
case 'subscription.created':
  await db.subscription.create({
    data: {
      userId: evt.data.public_user_data.user_id,
      planId: evt.data.plan.id,
      status: 'active',
      currentPeriodEnd: new Date(evt.data.current_period_end * 1000)
    }
  })
  break
```

### Checking Plan in Server Components

```typescript
const { userId } = await auth()
const user = await (await clerkClient()).users.getUser(userId!)
const plan = user.publicMetadata?.plan as string || 'free'

if (plan !== 'pro') {
  redirect('/billing/upgrade')
}
```

## Clerk Views (Prebuilt Pages)

Full-page authentication views that replace custom sign-in/sign-up pages.

```typescript
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return <SignIn />
}
```

```typescript
import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return <SignUp />
}
```

## Framework SDKs

Clerk provides 15+ framework-specific SDKs:

| Framework | Package | Quick Start |
|-----------|---------|-------------|
| Next.js | `@clerk/nextjs` | `clerk.com/docs/nextjs` |
| React | `@clerk/react` | `clerk.com/docs/react` |
| Expo | `@clerk/expo` | `clerk.com/docs/expo` |
| Astro | `@clerk/astro` | `clerk.com/docs/astro` |
| Nuxt | `@clerk/nuxt` | `clerk.com/docs/nuxt` |
| Vue | `@clerk/vue` | `clerk.com/docs/vue` |
| Express | `@clerk/backend` | `clerk.com/docs/expressjs` |
| Fastify | `@clerk/backend` | `clerk.com/docs/fastify` |
| Go | `clerk-sdk-go` | `github.com/clerk/clerk-sdk-go` |
| Python | `clerk-sdk-python` | `github.com/clerk/clerk-sdk-python` |

## Waitlist

Control access before launch with built-in waitlist:

1. Enable in Dashboard > Waitlist
2. Users sign up but are placed in waitlist state
3. Approve/deny from Dashboard or API
4. Approved users receive invitation email

## Enterprise Features

- **SAML SSO**: Dashboard > SSO Connections > Add SAML
- **SCIM Provisioning**: Auto-sync users from IdP (Okta, Azure AD, Google Workspace)
- **Audit Logs**: Track all auth events for compliance
- **Banned Users**: Block specific users via Dashboard or API
