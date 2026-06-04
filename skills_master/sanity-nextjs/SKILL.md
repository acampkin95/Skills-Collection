---
name: sanity-nextjs
description: Sanity CMS with Next.js — GROQ queries, portable text, image optimization, webhook revalidation, ISR caching, and TypeGen.
version: 2.0.0
reviewed: "2026-06-04"
---
# Sanity CMS with Next.js 15+ Integration

Headless CMS implementation with Sanity and Next.js. Covers setup, client configuration, Live Content API, GROQ queries, real-time preview, image optimization, and ISR strategies for modern content-driven applications.

## Quick Start

### 1. Initialize Sanity Project

```bash
npm create sanity@latest -- --template clean --create-sample-dataset
cd sanity-project
npm install
```

### 2. Configure Next.js Environment

```env
# .env.local
NEXT_PUBLIC_SANITY_PROJECT_ID=your_project_id
NEXT_PUBLIC_SANITY_DATASET=production
NEXT_PUBLIC_SANITY_API_VERSION=2024-12-01
SANITY_API_TOKEN=your_api_token  # For server-side mutations
```

### 3. Install Sanity Packages in Next.js

```bash
npm install sanity next-sanity @sanity/image-url
```

---

## Client Configuration

### Initialize Sanity Client

```typescript
// lib/sanity.client.ts
import { createClient } from 'next-sanity';

export const sanityClient = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  apiVersion: process.env.NEXT_PUBLIC_SANITY_API_VERSION,
  useCdn: true, // Set to false for real-time updates
  token: process.env.SANITY_API_TOKEN, // Only for mutations
});
```

### Configure TypeGen (Automatic Types)

```bash
npm install --save-dev @sanity/pkg-utils @sanity/codegen
npx sanity typegen generate
```

This generates `types/sanity.types.ts` from your schema automatically.

---


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.