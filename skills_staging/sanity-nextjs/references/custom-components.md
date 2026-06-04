# Custom Sanity Input Components

## Basic Custom Input

Create React components for specialized input scenarios:

```tsx
// components/CharacterCountInput.tsx
import React, { useCallback } from 'react'
import { Stack, Text, TextInput } from '@sanity/ui'
import { set, unset, StringInputProps } from 'sanity'

export const CharacterCountInput = (props: StringInputProps) => {
  const { elementProps, onChange, value = '' } = props
  const maxLength = 100

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.currentTarget.value
    
    if (newValue.length <= maxLength) {
      onChange(newValue ? set(newValue) : unset())
    }
  }, [onChange, maxLength])

  return (
    <Stack space={2}>
      <TextInput
        {...elementProps}
        onChange={handleChange}
        value={value}
        placeholder="Enter text (max 100 characters)"
      />
      <Text size={0} muted>
        {value.length} / {maxLength} characters
      </Text>
    </Stack>
  )
}

// Register in schema
import { CharacterCountInput } from '../components/CharacterCountInput'

export const descriptionField = defineField({
  title: 'Description',
  name: 'description',
  type: 'string',
  components: {
    input: CharacterCountInput
  },
  validation: (Rule) => Rule.required().max(100)
})
```

## Rating Input Component

```tsx
// components/RatingInput.tsx
import React, { useCallback } from 'react'
import { Card, Stack, Text } from '@sanity/ui'
import { set, NumberInputProps } from 'sanity'

const Star = ({ filled, onClick }: { filled: boolean; onClick: () => void }) => (
  <span
    onClick={onClick}
    style={{
      cursor: 'pointer',
      fontSize: '24px',
      color: filled ? '#FFD700' : '#CCCCCC',
      marginRight: '4px'
    }}
  >
    ★
  </span>
)

export const RatingInput = (props: NumberInputProps) => {
  const { value = 0, onChange } = props

  const handleRate = useCallback((rating: number) => {
    onChange(set(rating))
  }, [onChange])

  return (
    <Card padding={3} radius={2} border>
      <Stack space={3}>
        <Text weight="bold">Rate this item</Text>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              filled={star <= value}
              onClick={() => handleRate(star)}
            />
          ))}
        </div>
        <Text size={0} muted>
          {value > 0 ? `${value} out of 5 stars` : 'Not rated'}
        </Text>
      </Stack>
    </Card>
  )
}
```

## External API Selector

```tsx
// components/ExternalDataSelector.tsx
import React, { useState, useEffect } from 'react'
import { Select, Spinner, Card, Text } from '@sanity/ui'
import { set, StringInputProps } from 'sanity'

interface Option {
  title: string
  value: string
}

export const ExternalDataSelector = (props: StringInputProps) => {
  const { value, onChange } = props
  const [options, setOptions] = useState<Option[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('https://api.example.com/items')
        const data = await response.json()
        setOptions(data.map((item: { name: string; id: string }) => ({
          title: item.name,
          value: item.id
        })))
      } catch (err) {
        setError('Failed to fetch options')
        console.error('Failed to fetch data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) return <Spinner />
  
  if (error) {
    return (
      <Card tone="critical" padding={3}>
        <Text>{error}</Text>
      </Card>
    )
  }

  return (
    <Select
      value={value || ''}
      onChange={(e) => onChange(set(e.currentTarget.value))}
    >
      <option value="">Select an option...</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.title}
        </option>
      ))}
    </Select>
  )
}
```

## Color Picker Input

```tsx
// components/ColorPickerInput.tsx
import React, { useCallback } from 'react'
import { Stack, Text, Flex, Card, TextInput } from '@sanity/ui'
import { set, unset, StringInputProps } from 'sanity'

const presetColors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
  '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
]

export const ColorPickerInput = (props: StringInputProps) => {
  const { value = '', onChange, elementProps } = props

  const handleChange = useCallback((newValue: string) => {
    onChange(newValue ? set(newValue) : unset())
  }, [onChange])

  return (
    <Stack space={3}>
      <Flex gap={2} wrap="wrap">
        {presetColors.map((color) => (
          <Card
            key={color}
            padding={0}
            radius={2}
            style={{
              width: 32,
              height: 32,
              backgroundColor: color,
              cursor: 'pointer',
              border: value === color ? '3px solid black' : '1px solid #ccc'
            }}
            onClick={() => handleChange(color)}
          />
        ))}
      </Flex>
      <Flex gap={2} align="center">
        <input
          type="color"
          value={value || '#000000'}
          onChange={(e) => handleChange(e.target.value)}
          style={{ width: 40, height: 32, cursor: 'pointer' }}
        />
        <TextInput
          {...elementProps}
          value={value}
          onChange={(e) => handleChange(e.currentTarget.value)}
          placeholder="#000000"
          style={{ flex: 1 }}
        />
      </Flex>
      {value && (
        <Flex align="center" gap={2}>
          <Card
            padding={2}
            radius={2}
            style={{ backgroundColor: value, width: 24, height: 24 }}
          />
          <Text size={1} muted>Preview</Text>
        </Flex>
      )}
    </Stack>
  )
}
```

## Slug with Preview

```tsx
// components/SlugPreviewInput.tsx
import React from 'react'
import { Stack, Text, Card } from '@sanity/ui'
import { SlugInputProps } from 'sanity'

export const SlugPreviewInput = (props: SlugInputProps) => {
  const { value, renderDefault } = props
  const baseUrl = 'https://example.com/blog'

  return (
    <Stack space={3}>
      {renderDefault(props)}
      {value?.current && (
        <Card padding={3} radius={2} tone="primary">
          <Text size={1}>
            Preview URL: {baseUrl}/{value.current}
          </Text>
        </Card>
      )}
    </Stack>
  )
}
```

## JSON Editor Input

```tsx
// components/JsonEditorInput.tsx
import React, { useState, useCallback } from 'react'
import { Stack, Text, Card, Code } from '@sanity/ui'
import { set, unset, TextInputProps } from 'sanity'

export const JsonEditorInput = (props: TextInputProps) => {
  const { value = '', onChange, renderDefault } = props
  const [error, setError] = useState<string | null>(null)

  const validate = useCallback((jsonString: string) => {
    if (!jsonString) {
      setError(null)
      return true
    }
    try {
      JSON.parse(jsonString)
      setError(null)
      return true
    } catch (e) {
      setError('Invalid JSON format')
      return false
    }
  }, [])

  const handleBlur = useCallback(() => {
    if (value) {
      validate(value)
      // Auto-format valid JSON
      try {
        const parsed = JSON.parse(value)
        const formatted = JSON.stringify(parsed, null, 2)
        if (formatted !== value) {
          onChange(set(formatted))
        }
      } catch {
        // Keep as-is if invalid
      }
    }
  }, [value, onChange, validate])

  return (
    <Stack space={3}>
      <div onBlur={handleBlur}>
        {renderDefault(props)}
      </div>
      {error && (
        <Card tone="critical" padding={2} radius={2}>
          <Text size={1}>{error}</Text>
        </Card>
      )}
      {value && !error && (
        <Card padding={3} radius={2} tone="positive">
          <Code language="json" size={1}>
            {value}
          </Code>
        </Card>
      )}
    </Stack>
  )
}
```

## Conditional Field Wrapper

```tsx
// components/ConditionalInput.tsx
import React from 'react'
import { Card, Text } from '@sanity/ui'
import { InputProps, useFormValue } from 'sanity'

interface ConditionalInputProps extends InputProps {
  dependsOn: string
  expectedValue: unknown
  message?: string
}

export const ConditionalInput = (props: ConditionalInputProps) => {
  const { dependsOn, expectedValue, message, renderDefault } = props
  const dependentValue = useFormValue([dependsOn])

  if (dependentValue !== expectedValue) {
    return (
      <Card padding={3} radius={2} tone="caution">
        <Text size={1} muted>
          {message || `This field is only available when ${dependsOn} is set to ${String(expectedValue)}`}
        </Text>
      </Card>
    )
  }

  return renderDefault(props)
}
```

## Array Item Preview

Custom preview for array items:

```tsx
// components/ArrayItemPreview.tsx
import React from 'react'
import { Flex, Text, Badge, Card } from '@sanity/ui'
import { PreviewProps } from 'sanity'

export const FeatureItemPreview = (props: PreviewProps) => {
  const { title, subtitle, media } = props

  return (
    <Card padding={2}>
      <Flex align="center" gap={3}>
        {media}
        <Flex direction="column" gap={1} flex={1}>
          <Text weight="semibold">{title}</Text>
          {subtitle && <Text size={1} muted>{subtitle}</Text>}
        </Flex>
        <Badge tone="primary">Feature</Badge>
      </Flex>
    </Card>
  )
}

// Usage in schema
defineField({
  name: 'features',
  type: 'array',
  of: [{
    type: 'object',
    fields: [
      { name: 'title', type: 'string' },
      { name: 'description', type: 'text' }
    ],
    preview: {
      select: { title: 'title', subtitle: 'description' }
    },
    components: {
      preview: FeatureItemPreview
    }
  }]
})
```

## Document Actions

Custom publish action with confirmation:

```tsx
// actions/ConfirmPublishAction.tsx
import { useState } from 'react'
import { useDocumentOperation, DocumentActionProps } from 'sanity'
import { Button, Dialog, Card, Text, Stack } from '@sanity/ui'

export function ConfirmPublishAction(props: DocumentActionProps) {
  const { id, type, draft, onComplete } = props
  const { publish } = useDocumentOperation(id, type)
  const [showDialog, setShowDialog] = useState(false)

  if (!draft) return null

  return {
    label: 'Publish',
    onHandle: () => setShowDialog(true),
    dialog: showDialog && {
      type: 'dialog',
      onClose: () => setShowDialog(false),
      content: (
        <Stack space={4} padding={4}>
          <Text>Are you sure you want to publish this document?</Text>
          <Button
            tone="positive"
            onClick={() => {
              publish.execute()
              setShowDialog(false)
              onComplete()
            }}
          >
            Confirm Publish
          </Button>
        </Stack>
      )
    }
  }
}

// Register in sanity.config.ts
document: {
  actions: (prev, context) => {
    if (context.schemaType === 'post') {
      return prev.map((action) =>
        action.action === 'publish' ? ConfirmPublishAction : action
      )
    }
    return prev
  }
}
```

## Field-Level Components Reference

```typescript
// Available component slots
defineField({
  name: 'myField',
  type: 'string',
  components: {
    input: CustomInput,      // The input control itself
    field: CustomField,      // Wrapper around input + label
    item: CustomItem,        // For array items
    preview: CustomPreview,  // Preview in lists
  }
})
```
