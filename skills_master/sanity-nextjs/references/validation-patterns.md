# Sanity Validation Patterns

## Basic Validation Rules

```typescript
export const articleType = defineType({
  name: 'article',
  title: 'Article',
  type: 'document',
  fields: [
    defineField({
      title: 'Title',
      name: 'title',
      type: 'string',
      validation: (Rule) => [
        Rule.required().error('Title is required'),
        Rule.min(5).error('Title must be at least 5 characters'),
        Rule.max(120).error('Title cannot exceed 120 characters')
      ]
    }),
    defineField({
      title: 'Email',
      name: 'email',
      type: 'string',
      validation: (Rule) => Rule.required().email()
    }),
    defineField({
      title: 'Website URL',
      name: 'website',
      type: 'url',
      validation: (Rule) => Rule.uri({
        scheme: ['http', 'https'],
        allowRelative: false
      }).error('Please enter a valid URL starting with http or https')
    })
  ]
})
```

## Conditional Validation

Apply validation based on other field values:

```typescript
export const productType = defineType({
  name: 'product',
  title: 'Product',
  type: 'document',
  fields: [
    defineField({
      title: 'Is On Sale',
      name: 'isOnSale',
      type: 'boolean',
      initialValue: false
    }),
    defineField({
      title: 'Regular Price',
      name: 'regularPrice',
      type: 'number',
      validation: (Rule) => Rule.required().min(0)
    }),
    defineField({
      title: 'Sale Price',
      name: 'salePrice',
      type: 'number',
      validation: (Rule) => Rule.custom((value, context) => {
        const { isOnSale, regularPrice } = context.document

        if (!isOnSale) {
          return true // Skip validation if not on sale
        }

        if (!value) {
          return 'Sale price is required when product is on sale'
        }

        if (value >= regularPrice) {
          return 'Sale price must be less than regular price'
        }

        return true
      })
    })
  ]
})
```

## Reusable Validation Functions

Create validation helpers for common patterns:

```typescript
// validations/index.ts
export const validations = {
  urlSlug: (Rule) => Rule.required()
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, {
      name: 'url-slug',
      invert: false
    })
    .error('Slug must be lowercase with hyphens only'),

  phoneNumber: (Rule) => Rule.required()
    .regex(/^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/, {
      name: 'phone'
    })
    .error('Please enter a valid phone number'),

  isJsonString: (Rule) => Rule.custom((value) => {
    if (!value) return true
    try {
      JSON.parse(value)
      return true
    } catch {
      return 'Invalid JSON format'
    }
  }),

  uniqueSlug: (Rule) => Rule.custom(async (slug, context) => {
    if (!slug?.current) return 'Slug is required'
    
    const client = context.getClient({ apiVersion: '2024-12-01' })
    const count = await client.fetch(
      `count(*[_type == $type && slug.current == $slug && _id != $id])`,
      {
        type: context.document?._type,
        slug: slug.current,
        id: context.document?._id,
      }
    )
    
    return count > 0 ? 'Slug already in use' : true
  }),

  requiredForPublished: (Rule) => Rule.custom((value, context) => {
    if (context.document?.status === 'published' && !value) {
      return 'Required for published content'
    }
    return true
  }),

  futureDate: (Rule) => Rule.custom((value) => {
    if (!value) return true
    if (new Date(value) <= new Date()) {
      return 'Date must be in the future'
    }
    return true
  }),

  positiveNumber: (Rule) => Rule.min(0).error('Must be a positive number'),

  maxFileSize: (maxMB: number) => (Rule) => Rule.custom((value) => {
    if (!value?.asset?._ref) return true
    // Note: Full file size check requires asset metadata
    return true
  })
}

// Usage
import { validations } from './validations'

export const codeBlockType = defineType({
  name: 'codeBlock',
  type: 'object',
  fields: [
    defineField({
      title: 'JSON Config',
      name: 'config',
      type: 'text',
      validation: validations.isJsonString
    }),
    defineField({
      title: 'Slug',
      name: 'slug',
      type: 'slug',
      validation: validations.urlSlug
    })
  ]
})
```

## Document-Level Validation

Validate across multiple fields:

```typescript
export const eventType = defineType({
  name: 'event',
  title: 'Event',
  type: 'document',
  fields: [
    defineField({
      title: 'Event Name',
      name: 'title',
      type: 'string',
      validation: (Rule) => Rule.required()
    }),
    defineField({
      title: 'Start Date',
      name: 'startDate',
      type: 'datetime',
      validation: (Rule) => Rule.required()
    }),
    defineField({
      title: 'End Date',
      name: 'endDate',
      type: 'datetime',
      validation: (Rule) => Rule.required()
    })
  ],
  validation: (Rule) => Rule.custom((fields) => {
    if (!fields?.startDate || !fields?.endDate) {
      return true
    }

    if (new Date(fields.startDate) >= new Date(fields.endDate)) {
      return 'End date must be after start date'
    }

    return true
  })
})
```

## Array Validation

```typescript
defineField({
  name: 'tags',
  type: 'array',
  of: [{ type: 'string' }],
  validation: (Rule) => [
    Rule.required().min(1).error('At least one tag is required'),
    Rule.max(10).error('Maximum 10 tags allowed'),
    Rule.unique().error('Tags must be unique')
  ]
})

// Validate array items
defineField({
  name: 'images',
  type: 'array',
  of: [{ type: 'image' }],
  validation: (Rule) => Rule.custom((images) => {
    if (!images || images.length === 0) {
      return 'At least one image is required'
    }
    
    const missingAlt = images.some(img => !img.alt)
    if (missingAlt) {
      return 'All images must have alt text'
    }
    
    return true
  })
})
```

## Reference Validation

```typescript
defineField({
  name: 'author',
  type: 'reference',
  to: [{ type: 'author' }],
  validation: (Rule) => Rule.required().error('Author is required')
})

// Validate reference exists
defineField({
  name: 'category',
  type: 'reference',
  to: [{ type: 'category' }],
  validation: (Rule) => Rule.custom(async (ref, context) => {
    if (!ref?._ref) return 'Category is required'
    
    const client = context.getClient({ apiVersion: '2024-12-01' })
    const exists = await client.fetch(
      `count(*[_id == $id]) > 0`,
      { id: ref._ref }
    )
    
    return exists ? true : 'Selected category no longer exists'
  })
})
```

## Async Validation

```typescript
defineField({
  name: 'username',
  type: 'string',
  validation: (Rule) => Rule.custom(async (username, context) => {
    if (!username) return 'Username is required'
    
    // Check external API
    try {
      const response = await fetch(`/api/check-username?name=${username}`)
      const { available } = await response.json()
      return available ? true : 'Username is already taken'
    } catch {
      return 'Could not verify username availability'
    }
  })
})
```

## Warning vs Error

```typescript
defineField({
  name: 'title',
  type: 'string',
  validation: (Rule) => [
    // Errors - blocks publishing
    Rule.required().error('Title is required'),
    Rule.min(5).error('Title must be at least 5 characters'),
    
    // Warnings - allows publishing but shows warning
    Rule.max(60).warning('Titles over 60 characters may be truncated in search results'),
    Rule.custom((value) => {
      if (value && value.includes('!')) {
        return { valid: true, message: 'Consider removing exclamation marks for professional tone' }
      }
      return true
    }).warning()
  ]
})
```

## Image Validation

```typescript
defineField({
  name: 'heroImage',
  type: 'image',
  options: { hotspot: true },
  validation: (Rule) => [
    Rule.required().error('Hero image is required'),
    Rule.custom((image) => {
      if (!image?.asset) return true
      
      // Check for alt text in image fields
      if (!image.alt) {
        return 'Alt text is required for accessibility'
      }
      
      return true
    })
  ],
  fields: [
    defineField({
      name: 'alt',
      type: 'string',
      title: 'Alt Text',
      validation: (Rule) => Rule.required().min(10).max(120)
    })
  ]
})
```

## Portable Text Validation

```typescript
defineField({
  name: 'body',
  type: 'array',
  of: [{ type: 'block' }, { type: 'image' }],
  validation: (Rule) => [
    Rule.required().error('Content is required'),
    Rule.custom((blocks) => {
      if (!blocks || blocks.length === 0) {
        return 'Content cannot be empty'
      }
      
      // Check minimum text length
      const textContent = blocks
        .filter(b => b._type === 'block')
        .map(b => b.children?.map(c => c.text).join('') || '')
        .join('')
      
      if (textContent.length < 100) {
        return 'Content must be at least 100 characters'
      }
      
      return true
    })
  ]
})
```

## Complex Business Logic

```typescript
export const orderType = defineType({
  name: 'order',
  type: 'document',
  fields: [
    defineField({
      name: 'items',
      type: 'array',
      of: [{
        type: 'object',
        fields: [
          { name: 'product', type: 'reference', to: [{ type: 'product' }] },
          { name: 'quantity', type: 'number' },
          { name: 'price', type: 'number' }
        ]
      }],
      validation: (Rule) => Rule.required().min(1).error('Order must have at least one item')
    }),
    defineField({
      name: 'discountCode',
      type: 'string'
    }),
    defineField({
      name: 'discountAmount',
      type: 'number',
      validation: (Rule) => Rule.custom((discount, context) => {
        const { discountCode, items } = context.document
        
        if (discountCode && !discount) {
          return 'Discount amount is required when using a discount code'
        }
        
        if (discount) {
          const subtotal = items?.reduce((sum, item) => 
            sum + (item.price * item.quantity), 0
          ) || 0
          
          if (discount > subtotal) {
            return 'Discount cannot exceed order subtotal'
          }
          
          if (discount > subtotal * 0.5) {
            return 'Discount cannot exceed 50% of order total'
          }
        }
        
        return true
      })
    })
  ]
})
```

## Validation Error Messages

Best practices for error messages:

```typescript
// ❌ Bad - vague messages
Rule.required().error('Required')
Rule.max(100).error('Too long')

// ✅ Good - specific, actionable messages
Rule.required().error('Title is required')
Rule.max(100).error('Title cannot exceed 100 characters (currently 120)')

// ✅ Include field context
Rule.custom((value, context) => {
  if (!value) {
    return `${context.path[context.path.length - 1]} is required`
  }
  return true
})
```
