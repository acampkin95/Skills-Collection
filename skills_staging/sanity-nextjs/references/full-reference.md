---
name: sanity-nextjs
description: Headless CMS integration with Sanity and Next.js. Use this skill when Sanity CMS, GROQ, portable text, Sanity schema, Sanity Studio, content management, headless CMS, live content. Use this skill when GROQ queries, Sanity client, image optimization, webhook revalidation, ISR caching, content preview, TypeGen, Sanity dataset.
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

## GROQ Query Examples

### Fetch Single Document

```typescript
const query = `*[_type == "post" && slug.current == $slug][0] {
  _id,
  title,
  slug,
  content[] {
    ...,
    _type == 'image' => {
      ...,
      asset->
    }
  },
  author->,
  publishedAt,
  categories[]->
}`;

const post = await sanityClient.fetch(query, { slug });
```

### Fetch Multiple with Filters

```typescript
const query = `*[_type == "post" && publishedAt <= now()]
  | order(publishedAt desc)
  | [0...10] {
  _id,
  title,
  slug,
  excerpt,
  publishedAt,
  mainImage {
    asset->,
    alt
  }
}`;
```

### Related Content (Cross-References)

```typescript
const query = `*[_type == "post" && slug.current == $slug][0] {
  _id,
  title,
  relatedPosts[]-> {
    _id,
    title,
    slug,
    excerpt
  }
}`;
```

---

## Live Content API (Real-Time Updates)

### Next.js Server Component with Live Preview

```typescript
// app/posts/[slug]/page.tsx
import { LiveQuery } from 'next-sanity/preview';
import { sanityClient } from '@/lib/sanity.client';

export default async function PostPage({ params }: { params: { slug: string } }) {
  const query = `*[_type == "post" && slug.current == $slug][0] { ... }`;

  return (
    <LiveQuery
      query={query}
      initialData={await sanityClient.fetch(query, { slug: params.slug })}
      variables={{ slug: params.slug }}
    >
      {(post) => (
        <article>
          <h1>{post.title}</h1>
          <p>{post.excerpt}</p>
        </article>
      )}
    </LiveQuery>
  );
}
```

### Enable Preview Mode

```typescript
// app/api/draft/route.ts
import { validatePreviewUrl } from '@sanity/preview-url-secret';
import { draftMode } from 'next/headers';

export async function GET(request: Request) {
  const { isValid, redirectTo } = await validatePreviewUrl(
    process.env.SANITY_API_TOKEN!,
    new URL(request.url)
  );

  if (!isValid) return new Response('Invalid signature', { status: 401 });

  const draft = await draftMode();
  draft.enable();

  return new Response(null, { status: 307, headers: { location: redirectTo } });
}
```

---

## Image Optimization

### Image URL Builder

```typescript
// lib/image-url.ts
import { urlBuilder } from '@sanity/image-url';
import { sanityClient } from './sanity.client';

export const imageUrl = (source: any) =>
  urlBuilder(sanityClient)
    .image(source)
    .auto('format')
    .fit('max')
    .url();
```

### Next.js Image with Sanity

```typescript
import Image from 'next/image';
import { imageUrl } from '@/lib/image-url';

export function PostImage({ image }: { image: SanityImageAsset }) {
  return (
    <Image
      src={imageUrl(image).width(800).url()}
      alt={image.alt || 'Post image'}
      width={800}
      height={600}
      priority
    />
  );
}
```

---

## Webhook Revalidation

### Setup ISR with On-Demand Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidateTag } from 'next/cache';

export async function POST(request: Request) {
  const secret = request.headers.get('x-sanity-secret');
  if (secret !== process.env.SANITY_REVALIDATE_SECRET) {
    return new Response('Unauthorized', { status: 401 });
  }

  const body = await request.json();
  const { _type } = body;

  // Revalidate by tag
  revalidateTag(_type);

  return new Response(
    JSON.stringify({ revalidated: true, timestamp: new Date().toISOString() }),
    { status: 200 }
  );
}
```

### Configure Sanity Webhook

In Sanity Studio:
1. Go to **API > Webhooks**
2. Add webhook: `https://your-domain.com/api/revalidate`
3. Add header: `x-sanity-secret: your-secret`
4. Select events: `Create`, `Update`, `Delete`

---

## Caching Strategy

### Server Component with Tags

```typescript
// app/posts/page.tsx
import { sanityClient } from '@/lib/sanity.client';

export default async function PostsPage() {
  const posts = await sanityClient.fetch(
    `*[_type == "post"] | order(publishedAt desc)`,
    {},
    {
      next: {
        tags: ['posts'],
        revalidate: 3600, // ISR: revalidate every hour
      },
    }
  );

  return (
    <div>
      {posts.map((post) => (
        <article key={post._id}>
          <h2>{post.title}</h2>
        </article>
      ))}
    </div>
  );
}
```

---

## Common Schema Patterns

### Portable Text (Rich Text)

```typescript
{
  name: 'body',
  type: 'array',
  of: [
    {
      type: 'block',
      marks: {
        decorators: [
          { name: 'strong', title: 'Bold' },
          { name: 'em', title: 'Italic' },
        ]
      }
    },
    { type: 'image', options: { hotspot: true } },
    { type: 'code', options: { language: 'typescript' } }
  ]
}
```

### SEO Fields

```typescript
{
  name: 'seo',
  type: 'object',
  fields: [
    { name: 'title', type: 'string', validation: (Rule) => Rule.max(60) },
    { name: 'description', type: 'text', validation: (Rule) => Rule.max(160) },
    { name: 'keywords', type: 'array', of: [{ type: 'string' }] }
  ]
}
```

---

## Best Practices

1. **Use TypeGen**: Generate types automatically to catch schema changes
2. **Tag queries**: Use `tags` in fetch options for better revalidation control
3. **Image optimization**: Always use image URL builder with format/fit
4. **Draft mode**: Enable preview for editors to see changes before publish
5. **Error handling**: Gracefully handle missing documents in production

---

## Resources

| Resource | Purpose |
|----------|---------|
| [Sanity Docs](https://www.sanity.io/docs) | Official documentation |
| [GROQ Cheatsheet](https://www.sanity.io/docs/groq-cheatsheet) | Query language reference |
| [next-sanity](https://www.sanity.io/docs/next-sanity) | Next.js integration guide |
| [TypeGen](https://www.sanity.io/docs/cli/sanity-typegen) | Type generation setup |
