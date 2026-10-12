#!/usr/bin/env python3
"""
Component Scaffolding Script

Generates production-ready component boilerplate for React, Vue, and Svelte.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase.

    Splits on hyphens, underscores, and spaces, then capitalizes each word
    and joins without separators.

    Args:
        name: Input string to convert (e.g., 'my-component', 'my_component').

    Returns:
        PascalCase string (e.g., 'MyComponent').
    """
    return ''.join(word.capitalize() for word in re.split(r'[-_\s]+', name))


def to_kebab_case(name: str) -> str:
    """Convert string to kebab-case.

    Inserts hyphens before uppercase letters while handling PascalCase and
    camelCase patterns, then converts to lowercase.

    Args:
        name: Input string to convert (e.g., 'MyComponent', 'myComponent').

    Returns:
        kebab-case string (e.g., 'my-component').
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


# React Templates
REACT_COMPONENT = '''import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface {name}Props extends React.HTMLAttributes<HTMLDivElement> {{
  /** Optional variant */
  variant?: 'default' | 'secondary'
}}

export const {name} = forwardRef<HTMLDivElement, {name}Props>(
  ({{ className, variant = 'default', children, ...props }}, ref) => {{
    return (
      <div
        ref={{ref}}
        className={{cn(
          'rounded-lg border p-4',
          variant === 'default' && 'bg-background',
          variant === 'secondary' && 'bg-secondary',
          className
        )}}
        {{...props}}
      >
        {{children}}
      </div>
    )
  }}
)
{name}.displayName = '{name}'
'''

REACT_COMPOUND = '''import {{ createContext, useContext, forwardRef }} from 'react'
import {{ cn }} from '@/lib/utils'

// Context
interface {name}ContextValue {{
  variant: 'default' | 'secondary'
}}

const {name}Context = createContext<{name}ContextValue | null>(null)

function use{name}Context() {{
  const context = useContext({name}Context)
  if (!context) {{
    throw new Error('{name} components must be used within <{name}>')
  }}
  return context
}}

// Root
export interface {name}Props extends React.HTMLAttributes<HTMLDivElement> {{
  variant?: 'default' | 'secondary'
}}

export const {name} = forwardRef<HTMLDivElement, {name}Props>(
  ({{ className, variant = 'default', children, ...props }}, ref) => {{
    return (
      <{name}Context.Provider value={{{{ variant }}}}>
        <div
          ref={{ref}}
          className={{cn('rounded-lg border', className)}}
          {{...props}}
        >
          {{children}}
        </div>
      </{name}Context.Provider>
    )
  }}
)
{name}.displayName = '{name}'

// Header
export interface {name}HeaderProps extends React.HTMLAttributes<HTMLDivElement> {{}}

const {name}Header = forwardRef<HTMLDivElement, {name}HeaderProps>(
  ({{ className, ...props }}, ref) => {{
    return (
      <div
        ref={{ref}}
        className={{cn('border-b p-4 font-semibold', className)}}
        {{...props}}
      />
    )
  }}
)
{name}Header.displayName = '{name}Header'

// Content
export interface {name}ContentProps extends React.HTMLAttributes<HTMLDivElement> {{}}

const {name}Content = forwardRef<HTMLDivElement, {name}ContentProps>(
  ({{ className, ...props }}, ref) => {{
    return (
      <div
        ref={{ref}}
        className={{cn('p-4', className)}}
        {{...props}}
      />
    )
  }}
)
{name}Content.displayName = '{name}Content'

// Footer
export interface {name}FooterProps extends React.HTMLAttributes<HTMLDivElement> {{}}

const {name}Footer = forwardRef<HTMLDivElement, {name}FooterProps>(
  ({{ className, ...props }}, ref) => {{
    return (
      <div
        ref={{ref}}
        className={{cn('border-t p-4', className)}}
        {{...props}}
      />
    )
  }}
)
{name}Footer.displayName = '{name}Footer'

// Exports
export {{ {name}Header, {name}Content, {name}Footer }}
'''

REACT_HOOK = '''import {{ useState, useCallback, useEffect }} from 'react'

interface Use{name}Options {{
  /** Initial value */
  initialValue?: string
  /** Callback when value changes */
  onChange?: (value: string) => void
}}

interface Use{name}Return {{
  value: string
  setValue: (value: string) => void
  reset: () => void
  isDefault: boolean
}}

export function use{name}(options: Use{name}Options = {{}}): Use{name}Return {{
  const {{ initialValue = '', onChange }} = options
  const [value, setValueState] = useState(initialValue)

  const setValue = useCallback((newValue: string) => {{
    setValueState(newValue)
    onChange?.(newValue)
  }}, [onChange])

  const reset = useCallback(() => {{
    setValueState(initialValue)
    onChange?.(initialValue)
  }}, [initialValue, onChange])

  const isDefault = value === initialValue

  return {{ value, setValue, reset, isDefault }}
}}
'''

REACT_TEST = '''import {{ render, screen, fireEvent }} from '@testing-library/react'
import {{ describe, it, expect, vi }} from 'vitest'
import {{ {name} }} from './{kebab}'

describe('{name}', () => {{
  it('renders children', () => {{
    render(<{name}>Test content</{name}>)
    expect(screen.getByText('Test content')).toBeInTheDocument()
  }})

  it('applies className', () => {{
    render(<{name} className="custom-class">Content</{name}>)
    expect(screen.getByText('Content').parentElement).toHaveClass('custom-class')
  }})

  it('supports different variants', () => {{
    const {{ rerender }} = render(<{name} variant="default">Content</{name}>)
    expect(screen.getByText('Content').parentElement).toHaveClass('bg-background')
    
    rerender(<{name} variant="secondary">Content</{name}>)
    expect(screen.getByText('Content').parentElement).toHaveClass('bg-secondary')
  }})

  it('forwards ref', () => {{
    const ref = vi.fn()
    render(<{name} ref={{ref}}>Content</{name}>)
    expect(ref).toHaveBeenCalled()
  }})
}})
'''

REACT_STORY = '''import type {{ Meta, StoryObj }} from '@storybook/react'
import {{ {name} }} from './{kebab}'

const meta: Meta<typeof {name}> = {{
  title: 'Components/{name}',
  component: {name},
  tags: ['autodocs'],
  argTypes: {{
    variant: {{
      control: 'select',
      options: ['default', 'secondary'],
    }},
  }},
}}

export default meta
type Story = StoryObj<typeof {name}>

export const Default: Story = {{
  args: {{
    children: '{name} content',
  }},
}}

export const Secondary: Story = {{
  args: {{
    variant: 'secondary',
    children: 'Secondary variant',
  }},
}}
'''

# Vue Templates
VUE_COMPONENT = '''<script setup lang="ts">
import {{ computed }} from 'vue'
import {{ cn }} from '@/lib/utils'

interface Props {{
  variant?: 'default' | 'secondary'
  class?: string
}}

const props = withDefaults(defineProps<Props>(), {{
  variant: 'default',
}})

const classes = computed(() =>
  cn(
    'rounded-lg border p-4',
    props.variant === 'default' && 'bg-background',
    props.variant === 'secondary' && 'bg-secondary',
    props.class
  )
)
</script>

<template>
  <div :class="classes">
    <slot />
  </div>
</template>
'''

VUE_COMPOSABLE = '''import {{ ref, computed, watch }} from 'vue'

interface Use{name}Options {{
  initialValue?: string
  onChange?: (value: string) => void
}}

export function use{name}(options: Use{name}Options = {{}}) {{
  const {{ initialValue = '', onChange }} = options
  const value = ref(initialValue)

  const isDefault = computed(() => value.value === initialValue)

  function setValue(newValue: string) {{
    value.value = newValue
  }}

  function reset() {{
    value.value = initialValue
  }}

  watch(value, (newValue) => {{
    onChange?.(newValue)
  }})

  return {{ value, setValue, reset, isDefault }}
}}
'''

# Svelte Templates
SVELTE_COMPONENT = '''<script lang="ts">
  import {{ cn }} from '$lib/utils'

  export let variant: 'default' | 'secondary' = 'default'
  let className = ''
  export {{ className as class }}

  $: classes = cn(
    'rounded-lg border p-4',
    variant === 'default' && 'bg-background',
    variant === 'secondary' && 'bg-secondary',
    className
  )
</script>

<div class={{classes}} {{...$$restProps}}>
  <slot />
</div>
'''

INDEX_EXPORT = '''export {{ {name} }} from './{kebab}'
export type {{ {name}Props }} from './{kebab}'
'''

INDEX_COMPOUND = '''export {{ {name}, {name}Header, {name}Content, {name}Footer }} from './{kebab}'
export type {{ {name}Props, {name}HeaderProps, {name}ContentProps, {name}FooterProps }} from './{kebab}'
'''


def create_component(
    name: str,
    framework: str = 'react',
    path: str = './components',
    compound: bool = False,
    hook: bool = False,
    test: bool = False,
    story: bool = False,
    dry_run: bool = False
) -> list:
    """Generate component scaffold files for React, Vue, or Svelte.

    Creates production-ready component boilerplate with optional compound
    pattern, custom hooks/composables, tests, and Storybook stories.

    Args:
        name: Component name (converted to PascalCase internally).
        framework: Framework to target ('react', 'vue', or 'svelte').
        path: Output directory for component scaffold.
        compound: Generate compound component pattern (subcomponents).
        hook: Generate custom hook/composable alongside component.
        test: Generate test file for the component.
        story: Generate Storybook story file (React only).
        dry_run: Preview without creating files (no disk writes).

    Returns:
        List of (filename, content) tuples representing generated files.

    Raises:
        OSError: If directory creation or file writing fails.
    """
    pascal = to_pascal_case(name)
    kebab = to_kebab_case(name)
    
    base_path = Path(path) / kebab
    files = []
    
    if framework == 'react':
        if compound:
            files.append((f'{kebab}.tsx', REACT_COMPOUND.format(name=pascal)))
            files.append(('index.ts', INDEX_COMPOUND.format(name=pascal, kebab=kebab)))
        else:
            files.append((f'{kebab}.tsx', REACT_COMPONENT.format(name=pascal)))
            files.append(('index.ts', INDEX_EXPORT.format(name=pascal, kebab=kebab)))
        
        if hook:
            files.append((f'use-{kebab}.ts', REACT_HOOK.format(name=pascal)))
        
        if test:
            files.append((f'{kebab}.test.tsx', REACT_TEST.format(name=pascal, kebab=kebab)))
        
        if story:
            files.append((f'{kebab}.stories.tsx', REACT_STORY.format(name=pascal, kebab=kebab)))
    
    elif framework == 'vue':
        files.append((f'{pascal}.vue', VUE_COMPONENT.format(name=pascal)))
        files.append(('index.ts', f"export {{ default as {pascal} }} from './{pascal}.vue'"))
        
        if hook:
            files.append((f'use-{kebab}.ts', VUE_COMPOSABLE.format(name=pascal)))
    
    elif framework == 'svelte':
        files.append((f'{pascal}.svelte', SVELTE_COMPONENT.format(name=pascal)))
        files.append(('index.ts', f"export {{ default as {pascal} }} from './{pascal}.svelte'"))
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Creating {pascal} component")
    print(f"Framework: {framework}")
    print(f"Path: {base_path}")
    print("\nFiles:")
    
    for filename, content in files:
        filepath = base_path / filename
        print(f"  • {filepath}")
        
        if not dry_run:
            base_path.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
    
    if not dry_run:
        print(f"\n✓ Created {len(files)} files")
    
    return files


def main() -> None:
    """CLI entry point for component scaffolding tool.

    Parses command-line arguments and delegates to create_component() to
    generate framework-specific component boilerplate files.

    Command-line Arguments:
        name: Component name (auto-converted to appropriate case).
        --framework/-f: Target framework ('react', 'vue', or 'svelte').
        --path/-p: Output directory for generated component.
        --compound/-c: Generate compound component pattern with subcomponents.
        --hook: Generate custom hook or composable alongside component.
        --test/-t: Generate accompanying test file.
        --story/-s: Generate Storybook story file (React only).
        --dry-run/-n: Preview changes without writing files.

    Exit Codes:
        0: Success (component files generated or previewed).
        1: Error (argument validation failure).

    Raises:
        SystemExit: With code 0 or 1 depending on success/failure.
    """
    parser = argparse.ArgumentParser(
        description='Generate component boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s Button                    # Basic React component
  %(prog)s Card --compound           # Compound component (Card.Header, etc.)
  %(prog)s Dialog --test --story     # With test and Storybook
  %(prog)s Modal --framework vue     # Vue component
  %(prog)s Tabs --hook               # With custom hook
'''
    )

    parser.add_argument('name', help='Component name (PascalCase or kebab-case)')
    parser.add_argument('--framework', '-f', choices=['react', 'vue', 'svelte'],
                        default='react', help='Framework (default: react)')
    parser.add_argument('--path', '-p', default='./components',
                        help='Output path (default: ./components)')
    parser.add_argument('--compound', '-c', action='store_true',
                        help='Generate compound component pattern')
    parser.add_argument('--hook', action='store_true',
                        help='Generate custom hook/composable')
    parser.add_argument('--test', '-t', action='store_true',
                        help='Generate test file')
    parser.add_argument('--story', '-s', action='store_true',
                        help='Generate Storybook story')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Preview without creating files')

    args = parser.parse_args()

    create_component(
        name=args.name,
        framework=args.framework,
        path=args.path,
        compound=args.compound,
        hook=args.hook,
        test=args.test,
        story=args.story,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()
