# SEO Optimization Complete Guide - 2025

## AI Overview Optimization (Critical for 2025)

AI Overviews now appear in **85%+ of Google searches**, fundamentally shifting success metrics from rankings to citation frequency. Sites cited in AI Overviews report 2.3x traffic increases through branded searches.

### Content Structure for AI Parsing

```markdown
## TL;DR (50-70 words at article start)
Summarize key takeaways immediately. AI systems extract this for snippets.

## Clear Hierarchical Headers
Use H2 for main sections, H3 for subsections. AI parses structure.

## Scannable Formats
- Bullet points for lists
- Tables for comparisons
- Numbered steps for processes

## E-E-A-T Signals
Include author credentials, publication dates, citations to sources.
```

### Author Structured Data (Critical for E-E-A-T)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title Here",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "jobTitle": "Senior Specialist",
    "url": "https://example.com/authors/name",
    "sameAs": [
      "https://linkedin.com/in/author",
      "https://twitter.com/author"
    ],
    "alumniOf": {
      "@type": "Organization",
      "name": "University Name"
    }
  },
  "datePublished": "2025-01-15",
  "dateModified": "2025-01-20",
  "publisher": {
    "@type": "Organization",
    "name": "Site Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  }
}
</script>
```

## Meta Tags (Next.js 15)

### Essential Meta Tags

```tsx
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  // Basic meta
  title: {
    default: 'Site Name - Tagline',
    template: '%s | Site Name',
  },
  description: 'Compelling description under 160 characters that includes primary keywords and a call to action.',
  keywords: ['keyword1', 'keyword2', 'keyword3'],
  authors: [{ name: 'Author Name', url: 'https://author.com' }],
  creator: 'Creator Name',
  publisher: 'Publisher Name',
  
  // Canonical URL
  metadataBase: new URL('https://example.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'es-ES': '/es-ES',
    },
  },
  
  // Open Graph
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://example.com',
    siteName: 'Site Name',
    title: 'Page Title',
    description: 'Page description for social sharing',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Descriptive alt text for the image',
        type: 'image/jpeg',
      },
    ],
  },
  
  // Twitter Card
  twitter: {
    card: 'summary_large_image',
    site: '@sitehandle',
    creator: '@creatorhandle',
    title: 'Page Title',
    description: 'Page description for Twitter',
    images: ['/twitter-image.jpg'],
  },
  
  // Robots
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: false,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  
  // Verification
  verification: {
    google: 'google-verification-code',
    yandex: 'yandex-verification-code',
  },
  
  // Icons
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  
  // Manifest
  manifest: '/manifest.json',
}
```

### Page-Specific Metadata

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from 'next'

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.publishedAt,
      modifiedTime: post.updatedAt,
      authors: [post.author.name],
      images: [
        {
          url: post.featuredImage,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
  };
}
```

## Structured Data (JSON-LD)

### Organization Schema

```tsx
export function OrganizationSchema() {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Company Name",
    "url": "https://example.com",
    "logo": "https://example.com/logo.png",
    "description": "Company description",
    "foundingDate": "2020",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "123 Main St",
      "addressLocality": "City",
      "addressRegion": "State",
      "postalCode": "12345",
      "addressCountry": "US"
    },
    "contactPoint": {
      "@type": "ContactPoint",
      "telephone": "+1-555-555-5555",
      "contactType": "customer service"
    },
    "sameAs": [
      "https://twitter.com/company",
      "https://linkedin.com/company/company",
      "https://github.com/company"
    ]
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### Product Schema (with Reviews)

```tsx
export function ProductSchema({ product }: { product: Product }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": product.name,
    "description": product.description,
    "image": product.images,
    "brand": {
      "@type": "Brand",
      "name": product.brand
    },
    "sku": product.sku,
    "offers": {
      "@type": "Offer",
      "url": `https://example.com/products/${product.slug}`,
      "priceCurrency": "USD",
      "price": product.price,
      "availability": product.inStock 
        ? "https://schema.org/InStock" 
        : "https://schema.org/OutOfStock",
      "priceValidUntil": "2025-12-31"
    },
    "aggregateRating": product.reviews.length > 0 ? {
      "@type": "AggregateRating",
      "ratingValue": product.averageRating,
      "reviewCount": product.reviews.length,
      "bestRating": 5,
      "worstRating": 1
    } : undefined,
    "review": product.reviews.slice(0, 5).map(review => ({
      "@type": "Review",
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": review.rating
      },
      "author": {
        "@type": "Person",
        "name": review.authorName
      },
      "reviewBody": review.text,
      "datePublished": review.date
    }))
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### FAQ Schema

```tsx
export function FAQSchema({ faqs }: { faqs: FAQ[] }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map((faq) => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### HowTo Schema

```tsx
export function HowToSchema({ guide }: { guide: HowToGuide }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": guide.title,
    "description": guide.description,
    "totalTime": guide.totalTime, // e.g., "PT30M"
    "estimatedCost": {
      "@type": "MonetaryAmount",
      "currency": "USD",
      "value": guide.cost
    },
    "step": guide.steps.map((step, index) => ({
      "@type": "HowToStep",
      "position": index + 1,
      "name": step.title,
      "text": step.description,
      "image": step.image,
      "url": `${guide.url}#step-${index + 1}`
    }))
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### Breadcrumb Schema

```tsx
export function BreadcrumbSchema({ items }: { items: BreadcrumbItem[] }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": item.url
    }))
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

## Core Web Vitals 2025

### Current Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤2.5s | 2.5-4.0s | >4.0s |
| INP | ≤200ms | 200-500ms | >500ms |
| CLS | ≤0.1 | 0.1-0.25 | >0.25 |

**Note**: INP (Interaction to Next Paint) replaced FID in March 2024. Only 47% of websites currently pass all three metrics.

### LCP Optimization

```tsx
// 1. Preload critical images with fetchpriority
<head>
  <link 
    rel="preload" 
    as="image" 
    href="/hero-image.webp" 
    fetchpriority="high"
  />
</head>

// 2. Priority hints on hero images
import Image from 'next/image';

<Image
  src="/hero.webp"
  priority
  fetchPriority="high"
  loading="eager"
  width={1200}
  height={600}
  alt="Hero image description"
/>

// 3. Font optimization
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
});

// 4. Avoid render-blocking resources
// Move non-critical CSS to async loading
<link rel="preload" href="/non-critical.css" as="style" onLoad="this.onload=null;this.rel='stylesheet'" />
```

### INP Optimization (Critical for 2025)

```javascript
// 1. Break long tasks to improve INP
textBox.addEventListener('input', (inputEvent) => {
  // Critical: update UI immediately
  updateTextBox(inputEvent);

  // Defer non-critical work until after paint
  requestAnimationFrame(() => {
    setTimeout(() => {
      updateWordCount(textBox.textContent);
      checkSpelling(textBox.textContent);
    }, 0);
  });
});

// 2. Modern scheduler.yield() API
async function handleInteraction() {
  updateUI();
  if ('scheduler' in window && 'yield' in scheduler) {
    await scheduler.yield();
  }
  processData();
}

// 3. Use transitions for non-urgent updates
import { useTransition, startTransition } from 'react';

const [isPending, startTransition] = useTransition();

function handleClick() {
  // Urgent: show loading state
  setIsLoading(true);
  
  // Non-urgent: update list
  startTransition(() => {
    setFilteredItems(filter(items, query));
  });
}

// 4. Virtualize long lists
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              height: virtualItem.size,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### CLS Optimization

```tsx
// 1. Set explicit dimensions on images
<Image
  src="/photo.jpg"
  width={800}
  height={600}
  alt="Photo"
/>

// 2. Reserve space for dynamic content
<div className="min-h-[200px]">
  {isLoading ? <Skeleton className="h-[200px]" /> : <Content />}
</div>

// 3. Use aspect-ratio for responsive images
<div className="aspect-video relative">
  <Image src="/video-thumb.jpg" fill alt="Thumbnail" />
</div>

// 4. Font fallback with similar metrics
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  adjustFontFallback: true,
});

// 5. Avoid inserting content above existing
// ❌ Bad: Banner appears at top pushing content down
// ✅ Good: Reserve space or use fixed/sticky positioning
```

### Speculation Rules API (Prefetching)

```html
<!-- Prerender likely navigation targets -->
<script type="speculationrules">
{
  "prerender": [{
    "where": {
      "and": [
        { "href_matches": "/*" },
        { "not": { "href_matches": "/logout" }},
        { "not": { "href_matches": "/api/*" }},
        { "not": { "selector_matches": ".no-prerender" }}
      ]
    },
    "eagerness": "moderate"
  }],
  "prefetch": [{
    "where": {
      "selector_matches": "a[href]"
    },
    "eagerness": "conservative"
  }]
}
</script>
```

```tsx
// Next.js implementation
// app/speculation-rules.tsx
export function SpeculationRules() {
  const rules = {
    prerender: [{
      where: {
        and: [
          { href_matches: "/*" },
          { not: { href_matches: "/logout" }},
          { not: { href_matches: "/api/*" }}
        ]
      },
      eagerness: "moderate"
    }]
  };

  return (
    <script
      type="speculationrules"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(rules) }}
    />
  );
}
```

## Semantic HTML for SEO

### Heading Structure

```html
<!-- Every page should have exactly one h1 -->
<h1>Main Page Title with Primary Keyword</h1>

<!-- Logical hierarchy, don't skip levels -->
<h2>Section Heading</h2>
  <h3>Subsection</h3>
  <h3>Subsection</h3>
<h2>Another Section</h2>
  <h3>Subsection</h3>
    <h4>Sub-subsection</h4>
```

### Article Markup

```html
<article>
  <header>
    <h1>Article Title</h1>
    <p class="byline">
      By <a rel="author" href="/authors/name">Author Name</a>
    </p>
    <time datetime="2025-01-15T10:00:00Z">January 15, 2025</time>
  </header>
  
  <div class="article-content">
    <p>Article content...</p>
  </div>
  
  <footer>
    <nav aria-label="Tags">
      <a href="/tags/seo" rel="tag">SEO</a>
      <a href="/tags/web" rel="tag">Web Development</a>
    </nav>
  </footer>
</article>
```

## Sitemap & Robots

### sitemap.ts (Next.js 15)

```tsx
// app/sitemap.ts
import { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getPosts();
  const products = await getProducts();
  
  const postUrls = posts.map((post) => ({
    url: `https://example.com/blog/${post.slug}`,
    lastModified: post.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));
  
  const productUrls = products.map((product) => ({
    url: `https://example.com/products/${product.slug}`,
    lastModified: product.updatedAt,
    changeFrequency: 'daily' as const,
    priority: 0.9,
  }));
  
  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 1,
    },
    {
      url: 'https://example.com/about',
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    ...postUrls,
    ...productUrls,
  ];
}
```

### robots.ts (Next.js 15)

```tsx
// app/robots.ts
import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/admin/', '/api/', '/private/'],
      },
      {
        userAgent: 'GPTBot',
        disallow: '/',  // Block AI crawlers if desired
      },
      {
        userAgent: 'Google-Extended',
        disallow: '/',  // Block Google AI training
      },
    ],
    sitemap: 'https://example.com/sitemap.xml',
  };
}
```

## SEO Checklist 2025

### On-Page SEO

- [ ] Unique, descriptive title tag (50-60 characters)
- [ ] Compelling meta description (150-160 characters)
- [ ] One H1 per page containing primary keyword
- [ ] TL;DR summary in first 100 words (for AI Overviews)
- [ ] Logical heading hierarchy (H1 → H2 → H3)
- [ ] Descriptive, keyword-rich URLs
- [ ] Alt text on all images
- [ ] Internal links to related content
- [ ] Author bio with credentials (E-E-A-T)
- [ ] Publication and modification dates

### Technical SEO

- [ ] XML sitemap submitted to search engines
- [ ] robots.txt properly configured
- [ ] Canonical URLs set
- [ ] Hreflang for multilingual sites
- [ ] HTTPS enabled
- [ ] Core Web Vitals passing (LCP ≤2.5s, INP ≤200ms, CLS ≤0.1)
- [ ] Mobile-responsive design
- [ ] Structured data validates (Schema.org)
- [ ] No duplicate content
- [ ] 404 page customized
- [ ] Speculation Rules for prefetching

### Content for AI Overviews

- [ ] Clear, scannable structure with headers
- [ ] Bullet points, tables, numbered lists
- [ ] Direct answers to common questions
- [ ] Original evidence (photos, case studies)
- [ ] Expert author credentials visible
- [ ] Updated regularly with fresh content
