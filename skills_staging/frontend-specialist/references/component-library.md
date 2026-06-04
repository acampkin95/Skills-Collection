# Component Library Patterns

## Directory Structure

### Recommended Structure

```
components/
├── ui/              # Primitives (Button, Input, Badge)
│   ├── button.tsx
│   ├── input.tsx
│   └── index.ts
├── blocks/          # Compositions (Card, FormField, SearchBar)
│   ├── card.tsx
│   └── index.ts
├── sections/        # Page sections (Hero, Features, Pricing)
│   ├── hero.tsx
│   └── index.ts
└── layouts/         # Page wrappers
    ├── dashboard-layout.tsx
    └── index.ts
```

### Alternative: Feature-Based

```
features/
├── auth/
│   ├── components/
│   │   ├── login-form.tsx
│   │   └── signup-form.tsx
│   ├── hooks/
│   │   └── use-auth.ts
│   └── api/
│       └── auth.ts
└── products/
    ├── components/
    ├── hooks/
    └── api/
```

## Essential Utility

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Usage
cn('px-4 py-2', condition && 'bg-blue-500', className)
cn('px-2', 'px-4')  // Returns 'px-4' (merges correctly)
```

## Component Patterns

### Basic Component with Variants

```typescript
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:pointer-events-none disabled:opacity-50',
          // Variants
          variant === 'default' && 'bg-primary text-primary-foreground hover:bg-primary/90',
          variant === 'secondary' && 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
          variant === 'outline' && 'border border-input bg-background hover:bg-accent',
          variant === 'ghost' && 'hover:bg-accent hover:text-accent-foreground',
          variant === 'destructive' && 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
          // Sizes
          size === 'sm' && 'h-8 px-3 text-sm rounded-md',
          size === 'md' && 'h-10 px-4 text-sm rounded-md',
          size === 'lg' && 'h-12 px-6 text-base rounded-md',
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'
```

### CVA (Class Variance Authority)

```typescript
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
}
```

### Compound Component

```typescript
import { createContext, useContext, useState } from 'react'

// Context
const AccordionContext = createContext<{
  openItems: string[]
  toggle: (id: string) => void
} | null>(null)

// Root
export function Accordion({ children, type = 'single' }) {
  const [openItems, setOpenItems] = useState<string[]>([])
  
  const toggle = (id: string) => {
    setOpenItems(prev => 
      prev.includes(id)
        ? prev.filter(i => i !== id)
        : type === 'single' ? [id] : [...prev, id]
    )
  }
  
  return (
    <AccordionContext.Provider value={{ openItems, toggle }}>
      <div className="divide-y">{children}</div>
    </AccordionContext.Provider>
  )
}

// Item
Accordion.Item = function AccordionItem({ id, children }) {
  const ctx = useContext(AccordionContext)
  const isOpen = ctx?.openItems.includes(id)
  
  return (
    <div data-state={isOpen ? 'open' : 'closed'}>
      {children}
    </div>
  )
}

// Trigger
Accordion.Trigger = function AccordionTrigger({ id, children }) {
  const ctx = useContext(AccordionContext)
  
  return (
    <button
      onClick={() => ctx?.toggle(id)}
      className="flex w-full justify-between py-4"
    >
      {children}
      <ChevronDown className={cn('transition-transform', ctx?.openItems.includes(id) && 'rotate-180')} />
    </button>
  )
}

// Content
Accordion.Content = function AccordionContent({ id, children }) {
  const ctx = useContext(AccordionContext)
  const isOpen = ctx?.openItems.includes(id)
  
  if (!isOpen) return null
  return <div className="pb-4">{children}</div>
}

// Usage
<Accordion type="single">
  <Accordion.Item id="1">
    <Accordion.Trigger id="1">Section 1</Accordion.Trigger>
    <Accordion.Content id="1">Content 1</Accordion.Content>
  </Accordion.Item>
</Accordion>
```

### Polymorphic Component

```typescript
type PolymorphicProps<E extends React.ElementType, P = {}> = P & {
  as?: E
} & Omit<React.ComponentPropsWithoutRef<E>, keyof P | 'as'>

export function Box<E extends React.ElementType = 'div'>({
  as,
  className,
  ...props
}: PolymorphicProps<E, { className?: string }>) {
  const Component = as || 'div'
  return <Component className={className} {...props} />
}

// Usage
<Box as="section" className="p-4">Content</Box>
<Box as="article">Article content</Box>
<Box as="button" onClick={handleClick}>Click me</Box>
```

### Controlled/Uncontrolled

```typescript
import { useState, useCallback } from 'react'

interface ToggleProps {
  defaultPressed?: boolean
  pressed?: boolean
  onPressedChange?: (pressed: boolean) => void
}

export function Toggle({
  defaultPressed = false,
  pressed: controlledPressed,
  onPressedChange,
  children,
}: ToggleProps) {
  const [uncontrolledPressed, setUncontrolledPressed] = useState(defaultPressed)
  
  const isControlled = controlledPressed !== undefined
  const pressed = isControlled ? controlledPressed : uncontrolledPressed
  
  const handleClick = useCallback(() => {
    const newPressed = !pressed
    if (!isControlled) {
      setUncontrolledPressed(newPressed)
    }
    onPressedChange?.(newPressed)
  }, [pressed, isControlled, onPressedChange])
  
  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={handleClick}
      className={cn('rounded-md px-3 py-2', pressed ? 'bg-accent' : 'bg-transparent')}
    >
      {children}
    </button>
  )
}

// Uncontrolled
<Toggle onPressedChange={console.log}>Toggle</Toggle>

// Controlled
const [pressed, setPressed] = useState(false)
<Toggle pressed={pressed} onPressedChange={setPressed}>Toggle</Toggle>
```

## Custom Hooks

### useControllableState

```typescript
export function useControllableState<T>({
  value: controlledValue,
  defaultValue,
  onChange,
}: {
  value?: T
  defaultValue?: T
  onChange?: (value: T) => void
}) {
  const [uncontrolledValue, setUncontrolledValue] = useState(defaultValue)
  const isControlled = controlledValue !== undefined
  const value = isControlled ? controlledValue : uncontrolledValue
  
  const setValue = useCallback(
    (nextValue: T | ((prev: T) => T)) => {
      const newValue = typeof nextValue === 'function'
        ? (nextValue as (prev: T) => T)(value as T)
        : nextValue
      
      if (!isControlled) {
        setUncontrolledValue(newValue)
      }
      onChange?.(newValue)
    },
    [isControlled, onChange, value]
  )
  
  return [value, setValue] as const
}
```

### useMediaQuery

```typescript
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)
  
  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)
    
    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [query])
  
  return matches
}

// Usage
const isMobile = useMediaQuery('(max-width: 768px)')
```

### useOnClickOutside

```typescript
export function useOnClickOutside(
  ref: React.RefObject<HTMLElement>,
  handler: () => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return
      }
      handler()
    }
    
    document.addEventListener('mousedown', listener)
    document.addEventListener('touchstart', listener)
    
    return () => {
      document.removeEventListener('mousedown', listener)
      document.removeEventListener('touchstart', listener)
    }
  }, [ref, handler])
}
```

## Type Definitions

```typescript
// types/components.ts
import type { ComponentPropsWithoutRef, ElementType, ReactNode } from 'react'

export interface BaseProps {
  children?: ReactNode
  className?: string
}

export type ElementProps<T extends ElementType> = BaseProps & 
  Omit<ComponentPropsWithoutRef<T>, keyof BaseProps>

export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
export type Variant = 'default' | 'secondary' | 'outline' | 'ghost' | 'destructive'
```

## Barrel Exports

```typescript
// components/ui/index.ts
export { Button, type ButtonProps } from './button'
export { Card } from './card'
export { Input, type InputProps } from './input'
export { Badge, type BadgeProps } from './badge'

// components/index.ts
export * from './ui'
export * from './blocks'
export * from './sections'
```

## Testing

```typescript
// button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './button'

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })
  
  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  it('applies variant classes', () => {
    render(<Button variant="secondary">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-secondary')
  })
  
  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Button</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```
