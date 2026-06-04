# Clerk Schema Patterns

## Prisma Schema with Clerk

```prisma
// prisma/schema.prisma
model User {
  id        String   @id @default(cuid())
  clerkId   String   @unique @map("clerk_id")
  email     String   @unique
  firstName String?  @map("first_name")
  lastName  String?  @map("last_name")
  imageUrl  String?  @map("image_url")
  role      String   @default("user")

  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("users")
}

model Organization {
  id      String @id @default(cuid())
  clerkId String @unique @map("clerk_id")
  name    String
  slug    String @unique

  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("organizations")
}

model Membership {
  id             String @id @default(cuid())
  userId         String @map("user_id")
  organizationId String @map("organization_id")
  role           String @default("member")

  user         User         @relation(fields: [userId], references: [id])
  organization Organization @relation(fields: [organizationId], references: [id])

  @@unique([userId, organizationId])
  @@map("memberships")
}
```

## Sync Functions

```typescript
// lib/clerk-sync.ts
import { clerkClient } from '@clerk/nextjs/server'
import { db } from '@/lib/db'

export async function syncUser(clerkUserId: string) {
  const clerkUser = await clerkClient.users.getUser(clerkUserId)

  return db.user.upsert({
    where: { clerkId: clerkUserId },
    create: {
      clerkId: clerkUserId,
      email: clerkUser.emailAddresses[0]?.emailAddress,
      firstName: clerkUser.firstName,
      lastName: clerkUser.lastName,
      imageUrl: clerkUser.imageUrl,
    },
    update: {
      email: clerkUser.emailAddresses[0]?.emailAddress,
      firstName: clerkUser.firstName,
      lastName: clerkUser.lastName,
      imageUrl: clerkUser.imageUrl,
    },
  })
}

export async function syncOrganization(clerkOrgId: string) {
  const clerkOrg = await clerkClient.organizations.getOrganization(clerkOrgId)

  return db.organization.upsert({
    where: { clerkId: clerkOrgId },
    create: {
      clerkId: clerkOrgId,
      name: clerkOrg.name,
      slug: clerkOrg.slug,
    },
    update: {
      name: clerkOrg.name,
      slug: clerkOrg.slug,
    },
  })
}
```
