# Sanity + Next.js Performance Optimization

## Live Content API (Recommended)

The Live Content API is now the recommended approach for real-time updates without webhooks or polling.

### Setup

```typescript
// src/sanity/lib/live.ts
import { defineLive } from 'next-sanity/live'
import { client } from './client'

const token = process.env.SANITY_API_READ_TOKEN
if (!token) {
  throw new Error('Missing SANITY_API_READ_TOKEN')
}

export const { sanityFetch, SanityLive } = defineLive({
  client,
  serverToken: token,
  browserToken: token,
})
```

### Benefits
- Automatic real-time updates without webhooks
- CDN-cached responses with instant invalidation
- Seamless draft mode integration
- Reduced infrastructure complexity

### Usage

```typescript
// Layout - Always render SanityLive
import { SanityLive } from '@/sanity/lib/live'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SanityLive />
      </body>
    </html>
  )
}

// Page - Use sanityFetch
import { sanityFetch } from '@/sanity/lib/live'

export default async function Page() {
  const { data: posts } = await sanityFetch({ query: POSTS_QUERY })
  return <PostList posts={posts} />
}
```

## CDN and Caching Strategy

### Sanity CDN Configuration

```typescript
// src/sanity/lib/client.ts
import { createClient } from 'next-sanity'

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: '2024-12-01',
  useCdn: true, // Cached responses (60-second TTL)
  perspective: 'published',
  stega: {
    studioUrl: '/studio',
  },
})
```

### Next.js Caching (Without Live Content API)

```typescript
// Tag-based revalidation
export async function sanityFetch<T>({
  query,
  params = {},
  tags = [],
}: {
  query: string
  params?: QueryParams
  tags?: string[]
}): Promise<T> {
  return client.fetch<T>(query, params, {
    next: {
      revalidate: 3600, // 1 hour cache
      tags: ['sanity', ...tags],
    },
  })
}

// Usage with granular tags
const post = await sanityFetch({
  query: postBySlugQuery,
  params: { slug },
  tags: ['post', `post:${slug}`],
})
```

## Query Optimization

### Projection Best Practices

```groq
// ❌ BAD: Fetches entire documents
*[_type == "post"][0...10]

// ✅ GOOD: Fetches only needed fields
*[_type == "post"][0...10]{
  _id,
  title,
  "slug": slug.current,
  "imageUrl": mainImage.asset->url,
  publishedAt
}

// ❌ BAD: Deep reference chains
*[_type == "post"]{
  author->{
    organization->{
      team[]->{members[]->}
    }
  }
}

// ✅ GOOD: Flatten or split queries
*[_type == "post"]{
  "authorName": author->name,
  "organizationName": author->organization->name
}
```

### Query Indexing

Create indexes in Sanity dashboard for frequently filtered fields:

```groq
// These benefit from indexes
*[_type == "post" && publishedAt > $date]
*[_type == "post" && slug.current == $slug]
*[_type == "product" && category._ref == $categoryId]

// These don't benefit (avoid in production)
*[title match "search*"]     // Full-text without index
*[lower(title) == "test"]    // Function on field
```

## Image Optimization

### Sanity Image Pipeline

```typescript
// src/sanity/lib/image.ts
import imageUrlBuilder from '@sanity/image-url'
import { client } from './client'

const builder = imageUrlBuilder(client)

export function urlFor(source: SanityImageSource) {
  return builder.image(source)
}

// Optimized helpers
export const imageHelpers = {
  thumbnail: (source: SanityImageSource) =>
    urlFor(source).width(200).height(200).fit('crop').auto('format').url(),

  card: (source: SanityImageSource) =>
    urlFor(source).width(400).height(300).fit('crop').auto('format').url(),

  hero: (source: SanityImageSource) => ({
    src: urlFor(source).width(1920).height(1080).fit('crop').auto('format').url(),
    blurDataURL: urlFor(source).width(20).blur(50).url(),
  }),

  srcSet: (source: SanityImageSource, widths: number[]) =>
    widths
      .map((w) => `${urlFor(source).width(w).auto('format').url()} ${w}w`)
      .join(', '),
}
```

### Next.js Image Component

```typescript
// components/SanityImage.tsx
import Image from 'next/image'
import { urlFor } from '@/sanity/lib/image'

export function SanityImage({
  image,
  alt,
  width = 1200,
  height = 630,
  priority = false,
  className,
}: {
  image: SanityImageSource
  alt: string
  width?: number
  height?: number
  priority?: boolean
  className?: string
}) {
  if (!image?.asset) return null

  return (
    <Image
      src={urlFor(image).width(width).height(height).auto('format').url()}
      alt={alt}
      width={width}
      height={height}
      priority={priority}
      placeholder="blur"
      blurDataURL={urlFor(image).width(20).blur(50).url()}
      className={className}
    />
  )
}
```

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.sanity.io',
      },
    ],
  },
}

module.exports = nextConfig
```

## Static Generation

### generateStaticParams

```typescript
// app/posts/[slug]/page.tsx
import { client } from '@/sanity/lib/client'

export async function generateStaticParams() {
  const slugs = await client.fetch<string[]>(
    `*[_type == "post" && defined(slug.current)].slug.current`
  )
  return slugs.map((slug) => ({ slug }))
}

// Render on-demand for new posts
export const dynamicParams = true
```

### Incremental Static Regeneration

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { parseBody } from 'next-sanity/webhook'

export async function POST(request: Request) {
  const { body, isValidSignature } = await parseBody(
    request,
    process.env.SANITY_WEBHOOK_SECRET
  )

  if (!isValidSignature) {
    return Response.json({ message: 'Invalid signature' }, { status: 401 })
  }

  // Revalidate by tag
  revalidateTag(body._type)
  
  // Revalidate specific paths
  if (body.slug?.current) {
    revalidatePath(`/posts/${body.slug.current}`)
  }

  return Response.json({ revalidated: true })
}
```

## Bundle Optimization

### Dynamic Imports for Studio

```typescript
// app/studio/[[...tool]]/Studio.tsx
'use client'

import { NextStudio } from 'next-sanity/studio'
import config from '@/sanity.config'

export default function Studio() {
  return <NextStudio config={config} />
}

// app/studio/[[...tool]]/page.tsx
import dynamic from 'next/dynamic'

const Studio = dynamic(() => import('./Studio'), {
  ssr: false,
  loading: () => <div className="h-screen flex items-center justify-center">Loading Studio...</div>,
})

export default function StudioPage() {
  return <Studio />
}
```

### Tree Shaking

```typescript
// ❌ Imports entire groq package
import groq from 'groq'

// ✅ Import from next-sanity (smaller bundle)
import { groq } from 'next-sanity'

// ✅ Or use defineQuery for type inference
import { defineQuery } from 'next-sanity'
const QUERY = defineQuery(`*[_type == "post"]`)
```

## Monitoring and Debugging

### Query Performance Logging

```typescript
export async function sanityFetch<T>({
  query,
  params = {},
  tags = [],
}: FetchParams): Promise<T> {
  const start = performance.now()
  
  const result = await client.fetch<T>(query, params, {
    next: { revalidate: 3600, tags },
  })
  
  const duration = performance.now() - start
  if (duration > 500) {
    console.warn(`Slow Sanity query (${duration.toFixed(0)}ms):`, query.slice(0, 100))
  }
  
  return result
}
```

### Vision Tool

Use Vision (included with `@sanity/vision`) at `/studio/vision` to:
- Test queries before implementing
- Profile query execution time
- Preview results with different API versions

## Webhook Configuration

Configure in Sanity Dashboard (manage.sanity.io):

```
URL: https://yourdomain.com/api/revalidate
Secret: your-webhook-secret
Trigger on: Create, Update, Delete
Filter: _type in ["post", "page", "author"]
Projection: {_type, "slug": slug.current}
```

## Performance Checklist

- [ ] Live Content API configured (`defineLive` + `SanityLive`)
- [ ] Or CDN enabled (`useCdn: true`) with webhook revalidation
- [ ] Projections limit fetched fields
- [ ] Images use URL builder with sizing and `auto('format')`
- [ ] Static params generated for common pages
- [ ] Studio lazy-loaded with dynamic import
- [ ] Slow queries identified and optimized
- [ ] `cdn.sanity.io` in Next.js image config
