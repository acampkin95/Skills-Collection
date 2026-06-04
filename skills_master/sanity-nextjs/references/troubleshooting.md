# Sanity + Next.js Troubleshooting Guide

## CORS Errors

### Symptoms
```
Access to fetch at 'https://PROJECT_ID.api.sanity.io/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

### Solutions

**1. Add CORS Origins in Sanity Dashboard**
- Go to https://sanity.io/manage → Select project → API tab
- Add origins under "CORS origins":
  - `http://localhost:3000` (development)
  - `https://yourdomain.com` (production)
- **Critical**: Enable "Allow credentials" if using tokens or Studio

**2. Via CLI**
```bash
npx sanity cors add http://localhost:3000 --credentials
npx sanity cors add https://yourdomain.com --credentials
npx sanity cors list  # Verify
```

**3. Common Mistakes**
- Forgetting the port: `http://localhost` vs `http://localhost:3000`
- Missing protocol: `localhost:3000` vs `http://localhost:3000`
- Not enabling credentials for authenticated requests

---

## Data Not Fetching / 404 Errors

### Check Project Configuration
```typescript
// Verify these match your Sanity project
const client = createClient({
  projectId: 'YOUR_PROJECT_ID',  // Check manage.sanity.io
  dataset: 'production',          // Or your dataset name
  apiVersion: '2024-12-01',       // Use recent date
})
```

### Debugging Queries
```typescript
// Wrap in try-catch and log errors
try {
  const data = await client.fetch(query, params)
  console.log('Data received:', data)
} catch (error) {
  console.error('[SANITY QUERY FAILED]', error)
}
```

### Common Query Issues

**Missing Documents**
```groq
// Check if documents exist
count(*[_type == "post"])

// Check document structure
*[_type == "post"][0]
```

**Undefined Slug Errors**
```groq
// ❌ Fails on unpublished/incomplete docs
*[_type == "post"]{slug: slug.current}

// ✅ Filter for defined slugs
*[_type == "post" && defined(slug.current)]{slug: slug.current}
```

---

## Draft Mode / Preview Not Working

### Checklist
1. **Token Permissions**: Verify `SANITY_API_READ_TOKEN` has Viewer role
2. **CORS**: Origin must allow credentials
3. **Draft Mode Enabled**: Check `(await draftMode()).isEnabled` returns true
4. **Component Rendered**: Ensure `<VisualEditing />` is in layout when draft mode active

### Debug Draft Mode
```typescript
// app/debug/route.ts
import { draftMode } from 'next/headers'

export async function GET() {
  const dm = await draftMode()
  return Response.json({
    isEnabled: dm.isEnabled,
    hasToken: !!process.env.SANITY_API_READ_TOKEN,
  })
}
```

### Common Issues

**Token Not Being Used**
```typescript
// Ensure token is passed when fetching drafts
const { isEnabled } = await draftMode()

const data = await client.fetch(query, params, {
  perspective: isEnabled ? 'previewDrafts' : 'published',
  useCdn: !isEnabled,
  token: isEnabled ? process.env.SANITY_API_READ_TOKEN : undefined,
})
```

**Visual Editing Overlays Missing**
```typescript
// Verify stega is configured
const client = createClient({
  // ...
  stega: {
    studioUrl: '/studio', // Must match your Studio URL
  },
})
```

---

## Images Not Loading

### Next.js Image Configuration
```javascript
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.sanity.io',
      },
    ],
  },
}
```

### Verify Image Asset
```groq
// Check if image exists
*[_type == "post" && slug.current == "my-post"][0].mainImage.asset->

// Full image details
*[_type == "post"][0].mainImage{
  asset->{
    _id,
    url,
    metadata
  }
}
```

### Common Image Issues

**Null Asset Reference**
```typescript
// Always check for asset before rendering
function PostImage({ image }: { image: SanityImageSource }) {
  if (!image?.asset) return null
  return <Image src={urlFor(image).url()} ... />
}
```

**Hotspot Not Working**
```typescript
// Ensure hotspot is enabled in schema
defineField({
  name: 'image',
  type: 'image',
  options: { hotspot: true }, // Required!
})

// Use fit: 'crop' with hotspot
urlFor(image).width(400).height(300).fit('crop').url()
```

---

## TypeScript / TypeGen Issues

### Types Not Generating

```bash
# Full regeneration
rm -f schema.json sanity.types.ts
npx sanity schema extract --enforce-required-fields
npx sanity typegen generate
```

### Query Types Not Working

```typescript
// Queries must use defineQuery for type inference
import { defineQuery } from 'next-sanity'

// ✅ Types generated
const POSTS_QUERY = defineQuery(`*[_type == "post"]`)

// ❌ No types
const query = `*[_type == "post"]`
```

### Configuration
```typescript
// sanity.cli.ts
import { defineCliConfig } from 'sanity/cli'

export default defineCliConfig({
  api: {
    projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  },
  typegen: {
    generates: './src/sanity/types.ts',
  },
})
```

---

## Studio Issues

### Studio 404 in Production

Ensure catch-all route:
```typescript
// app/studio/[[...tool]]/page.tsx - Note double brackets!
import { NextStudio } from 'next-sanity/studio'
import config from '@/sanity.config'

export const dynamic = 'force-static'

export { metadata, viewport } from 'next-sanity/studio'

export default function StudioPage() {
  return <NextStudio config={config} />
}
```

### Studio Blank Screen

**Check Console for Errors**
- Missing environment variables
- Schema import errors
- Plugin configuration issues

**Verify Configuration**
```typescript
// sanity.config.ts
export default defineConfig({
  name: 'default',
  title: 'My Studio',
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!, // Must be set
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  plugins: [structureTool(), visionTool()],
  schema: { types: schemaTypes },
})
```

---

## Caching / Stale Data

### With Live Content API
Data updates automatically. If stale:
```typescript
// Verify SanityLive is rendered
<SanityLive />

// Check token is configured
const { sanityFetch, SanityLive } = defineLive({
  client,
  serverToken: token,
  browserToken: token,
})
```

### Without Live Content API

**On-Demand Revalidation**
```typescript
// Webhook handler
import { revalidateTag, revalidatePath } from 'next/cache'

// Revalidate by tag
revalidateTag('post')

// Revalidate specific path
revalidatePath('/blog/my-post')
```

**Time-Based Revalidation**
```typescript
const data = await client.fetch(query, params, {
  next: {
    revalidate: 60, // Seconds
    tags: ['post'],
  },
})
```

### Force Refresh During Development
```bash
rm -rf .next
npm run dev
```

---

## Hydration Errors

### Common Causes

**Date/Time Rendering**
```typescript
// ❌ Server and client render different times
<span>{new Date().toLocaleString()}</span>

// ✅ Use suppressHydrationWarning or client-only
<time dateTime={date.toISOString()} suppressHydrationWarning>
  {date.toLocaleDateString()}
</time>
```

**Conditional Rendering Based on Browser**
```typescript
// ❌ Different on server vs client
{typeof window !== 'undefined' && <Component />}

// ✅ Use useEffect for client-only
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null
```

---

## Performance Issues

### Slow Queries

**Add Projections**
```groq
// ❌ Fetches everything
*[_type == "post"]

// ✅ Fetch only needed fields
*[_type == "post"]{_id, title, "slug": slug.current}
```

**Limit Deep References**
```groq
// ❌ Deep chain
author->{organization->{team[]->{members[]->}}}

// ✅ Flatten
"authorName": author->name,
"orgName": author->organization->name
```

### Enable CDN
```typescript
const client = createClient({
  useCdn: process.env.NODE_ENV === 'production',
})
```

---

## Environment Variable Issues

### Next.js Conventions
- `NEXT_PUBLIC_*` - Exposed to browser
- Without prefix - Server-only

```bash
# .env.local
NEXT_PUBLIC_SANITY_PROJECT_ID=abc123    # ✅ Browser + Server
NEXT_PUBLIC_SANITY_DATASET=production   # ✅ Browser + Server
SANITY_API_READ_TOKEN=sk...             # ✅ Server only (secure)
```

### Verify Variables
```typescript
// Debug endpoint
export async function GET() {
  return Response.json({
    projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
    hasToken: !!process.env.SANITY_API_READ_TOKEN,
  })
}
```

---

## Webhook Not Triggering

### Sanity Dashboard Configuration
1. Go to manage.sanity.io → Project → API → Webhooks
2. Add webhook with:
   - URL: `https://yourdomain.com/api/revalidate`
   - Secret: Your `SANITY_WEBHOOK_SECRET`
   - Trigger on: Create, Update, Delete
   - Filter: `_type in ["post", "page"]`

### Debug Webhook
```typescript
export async function POST(request: Request) {
  console.log('Webhook received')
  
  const { body, isValidSignature } = await parseBody(
    request,
    process.env.SANITY_WEBHOOK_SECRET
  )
  
  console.log('Valid signature:', isValidSignature)
  console.log('Body:', body)
  
  // ...
}
```

### Common Issues
- Secret mismatch between Sanity and `.env`
- HTTPS required in production
- Route not deployed (check Vercel/Netlify logs)
