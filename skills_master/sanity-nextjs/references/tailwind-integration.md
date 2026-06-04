# Tailwind CSS Integration with Sanity

## Setup Tailwind Typography Plugin

The Typography plugin provides excellent default styling for rich text content.

```bash
npm install -D @tailwindcss/typography
```

```javascript
// tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

## Basic Portable Text with Prose

The simplest approach wraps PortableText in a prose container:

```tsx
<div className="prose prose-lg dark:prose-invert max-w-none">
  <PortableText value={body} />
</div>
```

## Advanced: ProseableText Component

When you have custom block types (images, videos, CTAs) mixed with text, the `not-prose` class helps escape inherited styles:

```tsx
// components/ProseableText.tsx
import { useMemo } from 'react'
import { PortableText } from '@portabletext/react'

interface ProseableTextProps {
  value: any[]
  components?: any
}

export function ProseableText({ value = [], components }: ProseableTextProps) {
  // Group standard blocks separately from custom types
  const valueGroups = useMemo(() => {
    if (!value?.length) return []
    
    return value.reduce<any[][]>(
      (acc, item) => {
        const lastIdx = acc.length - 1
        const lastGroup = acc[lastIdx]
        
        if (
          lastGroup.length === 0 ||
          lastGroup[0]._type === item._type
        ) {
          lastGroup.push(item)
        } else {
          acc.push([item])
        }
        return acc
      },
      [[]]
    )
  }, [value])

  if (!valueGroups?.length) return null

  return (
    <>
      {valueGroups.map((group, i) =>
        group[0]._type === 'block' ? (
          <div key={i} className="prose prose-lg dark:prose-invert max-w-none">
            <PortableText value={group} components={components} />
          </div>
        ) : (
          <div key={i} className="not-prose">
            <PortableText value={group} components={components} />
          </div>
        )
      )}
    </>
  )
}
```

## Portable Text Components with Tailwind

```tsx
// components/PortableTextComponents.tsx
import Image from 'next/image'
import Link from 'next/link'
import { PortableTextComponents } from '@portabletext/react'
import { urlFor } from '@/sanity/lib/image'

export const portableTextComponents: PortableTextComponents = {
  types: {
    image: ({ value }) => {
      if (!value?.asset) return null
      return (
        <figure className="not-prose my-8">
          <Image
            src={urlFor(value).width(800).auto('format').url()}
            alt={value.alt || ''}
            width={800}
            height={450}
            className="rounded-xl shadow-lg"
          />
          {value.caption && (
            <figcaption className="text-center text-sm text-gray-500 mt-3">
              {value.caption}
            </figcaption>
          )}
        </figure>
      )
    },
    
    code: ({ value }) => (
      <pre className="not-prose bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-6">
        <code className={`language-${value.language || 'text'}`}>
          {value.code}
        </code>
      </pre>
    ),
    
    callout: ({ value }) => (
      <aside className={`not-prose my-6 p-4 rounded-lg border-l-4 ${
        value.tone === 'warning' 
          ? 'bg-yellow-50 border-yellow-400 text-yellow-800' 
          : value.tone === 'error'
          ? 'bg-red-50 border-red-400 text-red-800'
          : 'bg-blue-50 border-blue-400 text-blue-800'
      }`}>
        {value.text}
      </aside>
    ),
    
    youtube: ({ value }) => (
      <div className="not-prose aspect-video my-8">
        <iframe
          className="w-full h-full rounded-xl"
          src={`https://www.youtube.com/embed/${value.videoId}`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    ),
  },

  marks: {
    link: ({ value, children }) => {
      const href = value?.href || ''
      const isExternal = href.startsWith('http')
      
      const className = "text-blue-600 hover:text-blue-800 underline decoration-blue-300 hover:decoration-blue-500 transition-colors"
      
      return isExternal ? (
        <a 
          href={href} 
          target="_blank" 
          rel="noopener noreferrer"
          className={className}
        >
          {children}
        </a>
      ) : (
        <Link href={href} className={className}>
          {children}
        </Link>
      )
    },
    
    highlight: ({ children }) => (
      <mark className="bg-yellow-200 px-1 rounded">{children}</mark>
    ),
    
    code: ({ children }) => (
      <code className="bg-gray-100 text-pink-600 px-1.5 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    ),
  },

  block: {
    h1: ({ children }) => (
      <h1 className="text-4xl font-bold mt-12 mb-6 text-gray-900 dark:text-white">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-3xl font-bold mt-10 mb-4 text-gray-900 dark:text-white">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-2xl font-semibold mt-8 mb-3 text-gray-900 dark:text-white">
        {children}
      </h3>
    ),
    h4: ({ children }) => (
      <h4 className="text-xl font-semibold mt-6 mb-2 text-gray-900 dark:text-white">
        {children}
      </h4>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 py-1 my-6 italic text-gray-700 dark:text-gray-300">
        {children}
      </blockquote>
    ),
    normal: ({ children }) => (
      <p className="text-gray-700 dark:text-gray-300 leading-relaxed my-4">
        {children}
      </p>
    ),
  },

  list: {
    bullet: ({ children }) => (
      <ul className="list-disc list-inside space-y-2 my-4 text-gray-700 dark:text-gray-300">
        {children}
      </ul>
    ),
    number: ({ children }) => (
      <ol className="list-decimal list-inside space-y-2 my-4 text-gray-700 dark:text-gray-300">
        {children}
      </ol>
    ),
  },

  listItem: {
    bullet: ({ children }) => <li className="ml-4">{children}</li>,
    number: ({ children }) => <li className="ml-4">{children}</li>,
  },
}
```

## Usage

```tsx
// In your page component
import { PortableText } from '@portabletext/react'
import { portableTextComponents } from '@/components/PortableTextComponents'

export default function BlogPost({ post }) {
  return (
    <article className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">{post.title}</h1>
      
      {/* Option 1: With prose wrapper */}
      <div className="prose prose-lg dark:prose-invert max-w-none">
        <PortableText 
          value={post.body} 
          components={portableTextComponents} 
        />
      </div>
      
      {/* Option 2: Without prose (all styles in components) */}
      <PortableText 
        value={post.body} 
        components={portableTextComponents} 
      />
    </article>
  )
}
```

## Customizing Prose Colors

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-links': 'theme(colors.blue.600)',
            '--tw-prose-bold': 'theme(colors.gray.900)',
            'code::before': { content: '""' },
            'code::after': { content: '""' },
          },
        },
        invert: {
          css: {
            '--tw-prose-links': 'theme(colors.blue.400)',
          },
        },
      },
    },
  },
}
```

## Tailwind v4 Notes

For Tailwind CSS v4, use the new import syntax:

```css
/* globals.css */
@import "tailwindcss";
```

The typography plugin works the same way with v4.

## Sanity Studio Custom Apps with Tailwind

For custom Sanity apps using the App SDK:

```typescript
// sanity.cli.ts
import { defineCliConfig } from 'sanity/cli'

export default defineCliConfig({
  app: {
    organizationId: 'your-org-id',
    entry: './src/App.tsx',
  },
  vite: async (viteConfig) => {
    const { default: tailwindcss } = await import('@tailwindcss/vite')
    return {
      ...viteConfig,
      plugins: [...viteConfig.plugins, tailwindcss()],
    }
  },
})
```
