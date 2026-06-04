# Sanity Schema Design Patterns

## Basic Schema with Helpers

Always use `defineType`, `defineField`, and `defineArrayMember` for TypeScript support:

```typescript
import { defineType, defineField, defineArrayMember } from 'sanity'

export const blogPostType = defineType({
  title: 'Blog Post',
  name: 'blogPost',
  type: 'document',
  fields: [
    defineField({
      title: 'Title',
      name: 'title',
      type: 'string',
      validation: (Rule) => Rule.required().min(5).max(100)
    }),
    defineField({
      title: 'Content',
      name: 'content',
      type: 'array',
      of: [
        defineArrayMember({ type: 'block' }),
        defineArrayMember({ type: 'image' })
      ]
    })
  ]
})
```

## Reusable Field Definitions

Extract common fields into modules for consistency:

```typescript
// schemas/fields/seoFields.ts
import { defineField } from 'sanity'

export const seoFields = {
  metaTitle: defineField({
    title: 'Meta Title',
    name: 'metaTitle',
    type: 'string',
    validation: (Rule) => Rule.max(60).warning('Keep under 60 characters for SEO')
  }),
  metaDescription: defineField({
    title: 'Meta Description',
    name: 'metaDescription',
    type: 'text',
    rows: 3,
    validation: (Rule) => Rule.max(155).warning('Keep under 155 characters')
  }),
  metaImage: defineField({
    title: 'Meta Image',
    name: 'metaImage',
    type: 'image',
    options: { hotspot: true },
    description: '1200x630px recommended'
  })
}

// Usage in any schema
import { seoFields } from './fields/seoFields'

export const pageType = defineType({
  name: 'page',
  type: 'document',
  fields: [
    defineField({ name: 'title', type: 'string' }),
    seoFields.metaTitle,
    seoFields.metaDescription,
    seoFields.metaImage
  ]
})
```

## Fieldsets for Organization

Group related fields to improve editor experience:

```typescript
export const productType = defineType({
  name: 'product',
  title: 'Product',
  type: 'document',
  fieldsets: [
    {
      name: 'pricing',
      title: 'Pricing',
      options: { collapsible: true }
    },
    {
      name: 'inventory',
      title: 'Inventory Management',
      options: { collapsible: true, collapsed: true }
    },
    {
      name: 'seo',
      title: 'SEO Settings',
      options: { collapsible: true, collapsed: true }
    }
  ],
  fields: [
    defineField({
      name: 'name',
      type: 'string',
      validation: (Rule) => Rule.required()
    }),
    defineField({
      name: 'basePrice',
      type: 'number',
      fieldset: 'pricing',
      validation: (Rule) => Rule.required().min(0)
    }),
    defineField({
      name: 'discountPrice',
      type: 'number',
      fieldset: 'pricing'
    }),
    defineField({
      name: 'stockQuantity',
      type: 'number',
      fieldset: 'inventory',
      validation: (Rule) => Rule.required().min(0)
    }),
    defineField({
      name: 'metaTitle',
      type: 'string',
      fieldset: 'seo'
    })
  ]
})
```

## Field Groups (Alternative to Fieldsets)

```typescript
export const product = defineType({
  name: 'product',
  title: 'Product',
  type: 'document',
  groups: [
    { name: 'content', title: 'Content', default: true },
    { name: 'pricing', title: 'Pricing' },
    { name: 'seo', title: 'SEO' },
  ],
  fields: [
    defineField({
      name: 'title',
      type: 'string',
      group: 'content',
    }),
    defineField({
      name: 'price',
      type: 'number',
      group: 'pricing',
    }),
    defineField({
      name: 'seo',
      type: 'seo',
      group: 'seo',
    }),
  ],
})
```

## Singleton Documents

For unique documents like settings or homepage:

```typescript
export const siteSettings = defineType({
  name: 'siteSettings',
  title: 'Site Settings',
  type: 'document',
  // Prevent creating multiple instances
  __experimental_actions: ['update', 'publish'],
  fields: [
    defineField({
      name: 'title',
      title: 'Site Title',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Site Description',
      type: 'text',
    }),
    defineField({
      name: 'logo',
      title: 'Logo',
      type: 'image',
    }),
  ],
})

// Desk structure for singleton
S.listItem()
  .title('Site Settings')
  .icon(CogIcon)
  .child(
    S.document()
      .schemaType('siteSettings')
      .documentId('siteSettings')
  )
```

## Modular Link Object

Reusable internal/external link pattern:

```typescript
export const linkObject = defineType({
  name: 'link',
  type: 'object',
  title: 'Link',
  fields: [
    defineField({
      name: 'text',
      title: 'Link Text',
      type: 'string'
    }),
    defineField({
      name: 'isExternal',
      title: 'External Link',
      type: 'boolean',
      initialValue: false
    }),
    defineField({
      name: 'url',
      title: 'URL',
      type: 'url',
      hidden: ({ parent }) => !parent?.isExternal,
      validation: (Rule) => Rule.custom((value, context) => {
        if (context.parent?.isExternal && !value) {
          return 'URL is required for external links'
        }
        return true
      })
    }),
    defineField({
      name: 'page',
      title: 'Internal Page',
      type: 'reference',
      to: [{ type: 'page' }, { type: 'post' }],
      hidden: ({ parent }) => parent?.isExternal
    })
  ]
})
```

## Modular Page Builder

```typescript
export const page = defineType({
  name: 'page',
  title: 'Page',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      type: 'slug',
      options: { source: 'title' },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'sections',
      title: 'Page Sections',
      type: 'array',
      of: [
        { type: 'hero' },
        { type: 'textBlock' },
        { type: 'imageGallery' },
        { type: 'ctaSection' },
        { type: 'testimonials' },
        { type: 'faq' },
      ],
    }),
  ],
})

// Section type example
export const hero = defineType({
  name: 'hero',
  title: 'Hero Section',
  type: 'object',
  fields: [
    defineField({ name: 'heading', type: 'string' }),
    defineField({ name: 'subheading', type: 'text' }),
    defineField({ name: 'backgroundImage', type: 'image', options: { hotspot: true } }),
    defineField({
      name: 'cta',
      title: 'Call to Action',
      type: 'link',
    }),
  ],
  preview: {
    select: { heading: 'heading' },
    prepare: ({ heading }) => ({
      title: heading || 'Hero Section',
      subtitle: 'Hero',
    }),
  },
})
```

## Hierarchical Content (Parent-Child)

```typescript
export const category = defineType({
  name: 'category',
  title: 'Category',
  type: 'document',
  fields: [
    defineField({ name: 'title', type: 'string' }),
    defineField({
      name: 'slug',
      type: 'slug',
      options: { source: 'title' },
    }),
    defineField({
      name: 'parent',
      title: 'Parent Category',
      type: 'reference',
      to: [{ type: 'category' }],
      // Prevent circular references
      options: {
        filter: ({ document }) => ({
          filter: '_id != $id',
          params: { id: document._id },
        }),
      },
    }),
  ],
})

// Query hierarchical data
const categoriesQuery = `
  *[_type == "category" && !defined(parent)]{
    _id,
    title,
    "slug": slug.current,
    "children": *[_type == "category" && parent._ref == ^._id]{
      _id,
      title,
      "slug": slug.current
    }
  }
`
```

## Image with Required Alt Text

```typescript
export const imageWithAlt = defineType({
  name: 'imageWithAlt',
  type: 'object',
  title: 'Image',
  fields: [
    defineField({
      name: 'image',
      type: 'image',
      title: 'Image',
      options: { hotspot: true },
      validation: (Rule) => Rule.required()
    }),
    defineField({
      name: 'alt',
      type: 'string',
      title: 'Alt Text',
      description: 'Important for SEO and accessibility',
      validation: (Rule) => Rule.required().min(10).max(120)
    }),
    defineField({
      name: 'caption',
      type: 'string',
      title: 'Caption'
    })
  ],
  preview: {
    select: {
      imageUrl: 'image.asset.url',
      alt: 'alt'
    },
    prepare({ imageUrl, alt }) {
      return {
        title: alt || 'Image',
        media: imageUrl
      }
    }
  }
})
```

## Localization / i18n

### Field-Level Translation

```typescript
const supportedLanguages = [
  { id: 'en', title: 'English', isDefault: true },
  { id: 'es', title: 'Spanish' },
  { id: 'fr', title: 'French' }
]

export const localeString = defineType({
  title: 'Localized String',
  name: 'localeString',
  type: 'object',
  fieldsets: [
    {
      title: 'Translations',
      name: 'translations',
      options: { collapsible: true }
    }
  ],
  fields: supportedLanguages.map(lang => 
    defineField({
      title: lang.title,
      name: lang.id,
      type: 'string',
      fieldset: lang.isDefault ? undefined : 'translations'
    })
  )
})

// Query with language
`*[_type == "product"][0] {
  name {
    en,
    es,
    fr
  }
}`
```

### Document-Level Translation

```typescript
export const articleType = defineType({
  name: 'article',
  type: 'document',
  fields: [
    defineField({
      name: 'language',
      type: 'string',
      options: {
        list: [
          { title: 'English', value: 'en' },
          { title: 'Spanish', value: 'es' },
          { title: 'French', value: 'fr' }
        ]
      },
      validation: (Rule) => Rule.required()
    }),
    defineField({
      name: 'title',
      type: 'string',
      validation: (Rule) => Rule.required()
    }),
    defineField({
      name: 'baseDocument',
      type: 'reference',
      to: [{ type: 'article' }],
      description: 'Reference to the base language version'
    })
  ]
})
```

## Slug Patterns

```typescript
// Auto-generate from title
defineField({
  name: 'slug',
  type: 'slug',
  options: {
    source: 'title',
    maxLength: 96,
    slugify: (input) =>
      input
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w-]+/g, '')
        .slice(0, 96),
  },
})

// Composite slug from multiple fields
defineField({
  name: 'slug',
  type: 'slug',
  options: {
    source: (doc) => `${doc.category}-${doc.title}`,
  },
})

// Unique slug validation
defineField({
  name: 'slug',
  type: 'slug',
  validation: (rule) =>
    rule.required().custom(async (slug, context) => {
      if (!slug?.current) return 'Required'
      
      const client = context.getClient({ apiVersion: '2024-12-01' })
      const count = await client.fetch(
        `count(*[_type == $type && slug.current == $slug && _id != $id])`,
        {
          type: context.document?._type,
          slug: slug.current,
          id: context.document?._id,
        }
      )
      
      return count > 0 ? 'Slug must be unique' : true
    }),
})
```

## Ordered Content

```typescript
export const navigation = defineType({
  name: 'navigation',
  title: 'Navigation',
  type: 'document',
  fields: [
    defineField({
      name: 'items',
      title: 'Menu Items',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'label', type: 'string' },
            { name: 'link', type: 'link' },
            {
              name: 'children',
              type: 'array',
              of: [
                {
                  type: 'object',
                  fields: [
                    { name: 'label', type: 'string' },
                    { name: 'link', type: 'link' },
                  ],
                },
              ],
            },
          ],
        },
      ],
    }),
  ],
})
```
