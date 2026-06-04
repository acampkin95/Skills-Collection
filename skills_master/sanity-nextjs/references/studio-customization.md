# Sanity Studio Customization

## Modern Desk Structure (Structure Tool)

```typescript
// sanity/desk/structure.ts
import { StructureBuilder } from 'sanity/structure'
import { DocumentIcon, CogIcon, ComposeIcon, TagIcon } from '@sanity/icons'

export const structure = (S: StructureBuilder) =>
  S.list()
    .title('Content')
    .items([
      // Custom document list with ordering
      S.listItem()
        .title('Blog Posts')
        .icon(ComposeIcon)
        .child(
          S.documentTypeList('post')
            .title('Blog Posts')
            .defaultOrdering([{ field: 'publishedAt', direction: 'desc' }])
        ),

      // Singleton document
      S.listItem()
        .title('Site Settings')
        .icon(CogIcon)
        .child(
          S.document()
            .schemaType('siteSettings')
            .documentId('siteSettings')
        ),

      S.divider(),

      // Filter by reference
      S.listItem()
        .title('Posts by Category')
        .icon(TagIcon)
        .child(
          S.documentTypeList('category')
            .title('Categories')
            .child((categoryId) =>
              S.documentList()
                .title('Posts')
                .filter('_type == "post" && $categoryId in categories[]._ref')
                .params({ categoryId })
            )
        ),

      // Auto-generate remaining types
      ...S.documentTypeListItems().filter(
        (item) => !['post', 'siteSettings', 'category'].includes(item.getId()!)
      ),
    ])
```

## Studio Configuration

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { presentationTool } from 'sanity/presentation'
import { schemaTypes } from './schemaTypes'
import { structure } from './desk/structure'

export default defineConfig({
  name: 'default',
  title: 'My Project',
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,

  plugins: [
    structureTool({ structure }),
    visionTool({ defaultApiVersion: '2024-12-01' }),
    presentationTool({
      previewUrl: {
        draftMode: {
          enable: '/api/draft-mode/enable',
        },
      },
    }),
  ],

  schema: {
    types: schemaTypes,
  },
})
```

## Custom Document Actions

```typescript
// sanity/actions/publishWithNotification.ts
import { DocumentActionComponent, useDocumentOperation } from 'sanity'
import { useState } from 'react'
import { PublishIcon } from '@sanity/icons'

export const PublishWithNotification: DocumentActionComponent = (props) => {
  const { publish } = useDocumentOperation(props.id, props.type)
  const [isPublishing, setIsPublishing] = useState(false)

  return {
    icon: PublishIcon,
    disabled: publish.disabled,
    label: isPublishing ? 'Publishing...' : 'Publish & Notify',
    onHandle: async () => {
      setIsPublishing(true)
      
      publish.execute()
      
      // Send notification
      await fetch('/api/notify', {
        method: 'POST',
        body: JSON.stringify({ documentId: props.id, type: props.type }),
      })
      
      setIsPublishing(false)
      props.onComplete()
    },
  }
}

// sanity.config.ts
export default defineConfig({
  // ...
  document: {
    actions: (prev, context) => {
      if (context.schemaType === 'post') {
        return prev.map((action) =>
          action.action === 'publish' ? PublishWithNotification : action
        )
      }
      return prev
    },
  },
})
```

## Custom Input Components

```typescript
// sanity/components/CharacterCountInput.tsx
import { Stack, Text, TextInput } from '@sanity/ui'
import { StringInputProps, set, unset } from 'sanity'
import { useCallback } from 'react'

export function CharacterCountInput(props: StringInputProps) {
  const { value = '', onChange, schemaType, elementProps } = props
  const maxLength = (schemaType.options as any)?.maxLength || 160

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = event.target.value
      onChange(newValue ? set(newValue) : unset())
    },
    [onChange]
  )

  const remaining = maxLength - value.length
  const isOver = remaining < 0

  return (
    <Stack space={2}>
      <TextInput
        {...elementProps}
        value={value}
        onChange={handleChange}
      />
      <Text
        size={1}
        style={{ color: isOver ? 'red' : remaining < 20 ? 'orange' : 'inherit' }}
      >
        {remaining} characters remaining
      </Text>
    </Stack>
  )
}

// Usage in schema
defineField({
  name: 'metaDescription',
  title: 'Meta Description',
  type: 'string',
  components: { input: CharacterCountInput },
  options: { maxLength: 160 },
})
```

## Custom Preview Components

```typescript
// sanity/components/PostPreview.tsx
import { Card, Flex, Text, Box } from '@sanity/ui'
import { PreviewProps } from 'sanity'

export function PostPreview(props: PreviewProps) {
  const { title, subtitle, media } = props

  return (
    <Card padding={2}>
      <Flex align="center" gap={3}>
        {media && <Box>{props.renderDefault({ ...props, layout: 'media' })}</Box>}
        <Box flex={1}>
          <Text weight="semibold">{title}</Text>
          {subtitle && <Text size={1} muted>{subtitle}</Text>}
        </Box>
      </Flex>
    </Card>
  )
}
```

## Popular Plugins

```typescript
// sanity.config.ts
import { defineConfig } from 'sanity'
import { visionTool } from '@sanity/vision'
import { codeInput } from '@sanity/code-input'
import { colorInput } from '@sanity/color-input'
import { media } from 'sanity-plugin-media'
import { scheduledPublishing } from '@sanity/scheduled-publishing'
import { documentInternationalization } from '@sanity/document-internationalization'

export default defineConfig({
  plugins: [
    // GROQ query playground
    visionTool({ defaultApiVersion: '2024-12-01' }),
    
    // Code blocks with syntax highlighting
    codeInput(),
    
    // Color picker field
    colorInput(),
    
    // Enhanced media library
    media(),
    
    // Schedule content publishing
    scheduledPublishing(),
    
    // Multi-language support
    documentInternationalization({
      supportedLanguages: [
        { id: 'en', title: 'English' },
        { id: 'es', title: 'Spanish' },
        { id: 'fr', title: 'French' },
      ],
      schemaTypes: ['post', 'page'],
    }),
  ],
})
```

## Custom Dashboard Tool

```typescript
// sanity/tools/dashboard.tsx
import { definePlugin } from 'sanity'
import { DashboardIcon } from '@sanity/icons'
import { Card, Stack, Heading, Text, Grid } from '@sanity/ui'
import { useClient } from 'sanity'
import { useState, useEffect } from 'react'

function DashboardComponent() {
  const client = useClient({ apiVersion: '2024-12-01' })
  const [stats, setStats] = useState({ posts: 0, drafts: 0, authors: 0 })

  useEffect(() => {
    async function fetchStats() {
      const [posts, drafts, authors] = await Promise.all([
        client.fetch('count(*[_type == "post" && !(_id in path("drafts.**"))])'),
        client.fetch('count(*[_type == "post" && _id in path("drafts.**")])'),
        client.fetch('count(*[_type == "author"])'),
      ])
      setStats({ posts, drafts, authors })
    }
    fetchStats()
  }, [client])

  return (
    <Card padding={4}>
      <Stack space={4}>
        <Heading size={2}>Content Dashboard</Heading>
        <Grid columns={3} gap={3}>
          <Card padding={3} tone="positive" radius={2}>
            <Stack space={2}>
              <Text size={4} weight="bold">{stats.posts}</Text>
              <Text size={1} muted>Published Posts</Text>
            </Stack>
          </Card>
          <Card padding={3} tone="caution" radius={2}>
            <Stack space={2}>
              <Text size={4} weight="bold">{stats.drafts}</Text>
              <Text size={1} muted>Drafts</Text>
            </Stack>
          </Card>
          <Card padding={3} tone="primary" radius={2}>
            <Stack space={2}>
              <Text size={4} weight="bold">{stats.authors}</Text>
              <Text size={1} muted>Authors</Text>
            </Stack>
          </Card>
        </Grid>
      </Stack>
    </Card>
  )
}

export const dashboardTool = definePlugin({
  name: 'dashboard',
  tools: [
    {
      name: 'dashboard',
      title: 'Dashboard',
      icon: DashboardIcon,
      component: DashboardComponent,
    },
  ],
})
```

## Validation Patterns

```typescript
// Required with custom message
validation: (rule) => rule.required().error('Title is required')

// Min/max length
validation: (rule) => rule.min(5).max(100)

// Regex pattern
validation: (rule) => rule.regex(/^[a-z0-9-]+$/, {
  name: 'slug',
  invert: false,
}).error('Only lowercase letters, numbers, and hyphens')

// Custom async validation
validation: (rule) => rule.custom(async (value, context) => {
  if (!value) return true
  const client = context.getClient({ apiVersion: '2024-12-01' })
  const exists = await client.fetch(
    `count(*[_type == "post" && slug.current == $slug && _id != $id]) > 0`,
    { slug: value, id: context.document?._id }
  )
  return exists ? 'Slug already in use' : true
})

// Conditional validation
validation: (rule) => rule.custom((value, context) => {
  if (context.document?.status === 'published' && !value) {
    return 'Required for published content'
  }
  return true
})

// Warning vs error
validation: (rule) => [
  rule.required().error('Required'),
  rule.max(50).warning('Consider shorter title for SEO'),
]
```

## Conditional Fields

```typescript
// Show/hide based on other field values
defineField({
  name: 'contentType',
  type: 'string',
  options: {
    list: ['article', 'video', 'podcast'],
    layout: 'radio',
  },
}),
defineField({
  name: 'videoUrl',
  type: 'url',
  hidden: ({ parent }) => parent?.contentType !== 'video',
}),
defineField({
  name: 'podcastUrl',
  type: 'url',
  hidden: ({ parent }) => parent?.contentType !== 'podcast',
}),
defineField({
  name: 'body',
  type: 'blockContent',
  hidden: ({ parent }) => parent?.contentType !== 'article',
})
```

## Document Badges

```typescript
// sanity.config.ts
export default defineConfig({
  document: {
    badges: (prev, context) => {
      if (context.schemaType === 'post') {
        return [
          ...prev,
          {
            label: context.published?.featured ? 'Featured' : null,
            title: 'This post is featured',
            color: 'success',
          },
        ].filter((badge) => badge.label)
      }
      return prev
    },
  },
})
```
