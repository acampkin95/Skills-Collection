# Sanity Webhooks

## Webhook Configuration

Configure webhooks in the Sanity dashboard:
**Settings → API → Webhooks → Add Webhook**

### Basic Webhook Settings

| Setting | Description |
|---------|-------------|
| Name | Descriptive name for the webhook |
| URL | Your endpoint (must be HTTPS in production) |
| Dataset | Which dataset triggers the webhook |
| Events | Create, Update, Delete, or all |
| Filter | GROQ filter to limit which documents trigger |
| Projection | GROQ projection to control payload shape |
| Secret | Shared secret for signature verification |

### Example Configuration

```
Name: Content Updates
URL: https://yourdomain.com/api/webhooks/sanity
Dataset: production
Events: Create, Update, Delete
Filter: _type in ["post", "page", "product"]
Projection: {
  _id,
  _type,
  _rev,
  _updatedAt,
  "slug": slug.current,
  title
}
Secret: your-webhook-secret-here
```

## Webhook Handler (Next.js App Router)

```typescript
// app/api/webhooks/sanity/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'
import { headers } from 'next/headers'
import crypto from 'crypto'

interface WebhookPayload {
  _id: string
  _type: string
  _rev: string
  _updatedAt: string
  slug?: string
  title?: string
}

// Verify webhook signature
function verifySignature(body: string, signature: string | null): boolean {
  if (!signature || !process.env.SANITY_WEBHOOK_SECRET) {
    return false
  }

  const hmac = crypto.createHmac('sha256', process.env.SANITY_WEBHOOK_SECRET)
  const digest = hmac.update(body).digest('hex')
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  )
}

export async function POST(request: Request) {
  const body = await request.text()
  const headersList = await headers()
  const signature = headersList.get('sanity-webhook-signature')

  // Verify signature
  if (!verifySignature(body, signature)) {
    console.error('Invalid webhook signature')
    return new Response('Unauthorized', { status: 401 })
  }

  const payload: WebhookPayload = JSON.parse(body)

  try {
    // Handle based on document type
    switch (payload._type) {
      case 'post':
        revalidateTag('posts')
        if (payload.slug) {
          revalidatePath(`/blog/${payload.slug}`)
        }
        revalidatePath('/blog')
        break

      case 'page':
        revalidateTag('pages')
        if (payload.slug) {
          revalidatePath(`/${payload.slug}`)
        }
        break

      case 'product':
        revalidateTag('products')
        if (payload.slug) {
          revalidatePath(`/products/${payload.slug}`)
        }
        revalidatePath('/products')
        break

      case 'siteSettings':
        // Revalidate everything for global settings
        revalidateTag('settings')
        revalidatePath('/', 'layout')
        break

      default:
        console.log(`Unhandled document type: ${payload._type}`)
    }

    console.log(`Revalidated: ${payload._type} - ${payload._id}`)

    return Response.json({ 
      revalidated: true, 
      type: payload._type,
      id: payload._id 
    })
  } catch (error) {
    console.error('Webhook error:', error)
    return Response.json({ error: 'Revalidation failed' }, { status: 500 })
  }
}
```

## Webhook Handler with Event Types

```typescript
// app/api/webhooks/sanity/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'

interface SanityWebhookBody {
  _id: string
  _type: string
  _rev: string
  operation: 'create' | 'update' | 'delete'
  documentId: string
  projectId: string
  dataset: string
  slug?: string
  [key: string]: unknown
}

type WebhookHandler = (payload: SanityWebhookBody) => Promise<void>

const handlers: Record<string, Record<string, WebhookHandler>> = {
  post: {
    create: async (payload) => {
      console.log('New post created:', payload._id)
      revalidateTag('posts')
      revalidatePath('/blog')
      // Notify subscribers, update search index, etc.
    },
    update: async (payload) => {
      console.log('Post updated:', payload._id)
      revalidateTag('posts')
      if (payload.slug) {
        revalidatePath(`/blog/${payload.slug}`)
      }
    },
    delete: async (payload) => {
      console.log('Post deleted:', payload._id)
      revalidateTag('posts')
      revalidatePath('/blog')
      // Remove from search index, clean up related data
    }
  },
  product: {
    create: async (payload) => {
      revalidateTag('products')
      revalidatePath('/products')
    },
    update: async (payload) => {
      revalidateTag('products')
      if (payload.slug) {
        revalidatePath(`/products/${payload.slug}`)
      }
    },
    delete: async (payload) => {
      revalidateTag('products')
      revalidatePath('/products')
    }
  }
}

export async function POST(request: Request) {
  // ... signature verification ...

  const payload: SanityWebhookBody = JSON.parse(await request.text())
  const { _type, operation } = payload

  const typeHandlers = handlers[_type]
  if (typeHandlers && typeHandlers[operation]) {
    await typeHandlers[operation](payload)
  }

  return Response.json({ success: true })
}
```

## Webhook with External Service Integration

```typescript
// app/api/webhooks/sanity/route.ts

async function updateSearchIndex(payload: WebhookPayload) {
  const { _id, _type, operation, title, slug } = payload

  if (operation === 'delete') {
    await fetch(`${process.env.SEARCH_API_URL}/delete`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${process.env.SEARCH_API_KEY}` },
      body: JSON.stringify({ id: _id })
    })
  } else {
    await fetch(`${process.env.SEARCH_API_URL}/upsert`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${process.env.SEARCH_API_KEY}` },
      body: JSON.stringify({
        id: _id,
        type: _type,
        title,
        url: `/${_type}s/${slug}`
      })
    })
  }
}

async function sendSlackNotification(payload: WebhookPayload) {
  if (payload.operation !== 'create') return

  await fetch(process.env.SLACK_WEBHOOK_URL!, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: `New ${payload._type} created: ${payload.title}`,
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `*New ${payload._type}*\n${payload.title}`
          }
        },
        {
          type: 'actions',
          elements: [
            {
              type: 'button',
              text: { type: 'plain_text', text: 'View in Studio' },
              url: `https://your-studio.sanity.studio/desk/${payload._type};${payload._id}`
            }
          ]
        }
      ]
    })
  })
}

async function invalidateCDN(paths: string[]) {
  // Example: Cloudflare cache purge
  await fetch(
    `https://api.cloudflare.com/client/v4/zones/${process.env.CF_ZONE_ID}/purge_cache`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.CF_API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ files: paths.map(p => `https://yourdomain.com${p}`) })
    }
  )
}

export async function POST(request: Request) {
  // ... verification ...

  const payload = JSON.parse(await request.text())

  // Run all integrations
  await Promise.all([
    updateSearchIndex(payload),
    sendSlackNotification(payload),
    invalidateCDN([`/blog/${payload.slug}`, '/blog'])
  ])

  return Response.json({ success: true })
}
```

## Webhook for Preview/Draft Content

Handle draft documents separately:

```typescript
export async function POST(request: Request) {
  const payload = JSON.parse(await request.text())
  
  // Check if this is a draft document
  const isDraft = payload._id.startsWith('drafts.')
  
  if (isDraft) {
    // Don't revalidate production cache for drafts
    // But you might want to notify preview environments
    console.log('Draft updated:', payload._id)
    
    // Optionally ping preview deployment
    await fetch(`${process.env.PREVIEW_URL}/api/revalidate`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    
    return Response.json({ preview: true })
  }

  // Handle published content
  revalidateTag(payload._type)
  return Response.json({ revalidated: true })
}
```

## Testing Webhooks Locally

### Using ngrok

```bash
# Install ngrok
npm install -g ngrok

# Start your Next.js dev server
npm run dev

# In another terminal, expose your local server
ngrok http 3000

# Use the ngrok URL in Sanity webhook config
# https://abc123.ngrok.io/api/webhooks/sanity
```

### Manual Testing

```typescript
// scripts/test-webhook.ts
const testPayload = {
  _id: 'test-123',
  _type: 'post',
  _rev: 'rev-123',
  operation: 'update',
  slug: 'test-post',
  title: 'Test Post'
}

const secret = process.env.SANITY_WEBHOOK_SECRET
const body = JSON.stringify(testPayload)
const signature = crypto
  .createHmac('sha256', secret)
  .update(body)
  .digest('hex')

fetch('http://localhost:3000/api/webhooks/sanity', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'sanity-webhook-signature': signature
  },
  body
})
```

## Webhook Debugging

```typescript
export async function POST(request: Request) {
  const body = await request.text()
  const headersList = await headers()

  // Log everything for debugging
  console.log('=== Webhook Received ===')
  console.log('Headers:', Object.fromEntries(headersList.entries()))
  console.log('Body:', body)
  console.log('========================')

  // ... rest of handler
}
```

## Common Webhook Filters

```groq
# Only published documents (exclude drafts)
!(_id in path("drafts.**"))

# Specific document types
_type in ["post", "page", "product"]

# Only documents with specific field
defined(publishedAt)

# Documents modified by specific user
_updatedBy == "user-id"

# Exclude certain types
!(_type in ["media.tag", "system.group"])

# Combined filters
_type == "post" && defined(publishedAt) && !(_id in path("drafts.**"))
```

## Error Handling Best Practices

```typescript
export async function POST(request: Request) {
  try {
    const body = await request.text()
    
    // Verify signature first
    if (!verifySignature(body, signature)) {
      return Response.json({ error: 'Invalid signature' }, { status: 401 })
    }

    const payload = JSON.parse(body)

    // Validate payload structure
    if (!payload._id || !payload._type) {
      return Response.json({ error: 'Invalid payload' }, { status: 400 })
    }

    // Process webhook
    await processWebhook(payload)

    return Response.json({ success: true })
  } catch (error) {
    console.error('Webhook error:', error)
    
    // Return 500 so Sanity will retry
    return Response.json(
      { error: 'Internal error', message: error.message },
      { status: 500 }
    )
  }
}
```

## Webhook Retry Behavior

Sanity will retry failed webhooks:
- Initial attempt
- Retry after 1 minute
- Retry after 5 minutes
- Retry after 30 minutes
- Final retry after 2 hours

Return appropriate status codes:
- `2xx`: Success, no retry
- `4xx`: Client error, no retry (except 429)
- `429`: Rate limited, will retry with backoff
- `5xx`: Server error, will retry
