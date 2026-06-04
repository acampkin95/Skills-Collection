# shadcn/ui Patterns

## Overview

shadcn/ui is a collection of reusable components built with Radix UI and Tailwind CSS. Components are copied into your project (not installed as a dependency), giving full control over code.

## Setup

### Next.js (App Router)

```bash
npx shadcn@latest init
```

Configuration prompts:
```
Style: Default or New York
Base color: Slate, Gray, Zinc, Neutral, Stone
CSS variables: Yes (recommended)
```

### Generated Files

```
components/
└── ui/
    ├── button.tsx
    ├── card.tsx
    └── ...

lib/
└── utils.ts        # cn() helper

styles/
└── globals.css     # CSS variables
```

### globals.css Structure

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark mode values */
  }
}
```

## Adding Components

```bash
# Single component
npx shadcn@latest add button

# Multiple components
npx shadcn@latest add button card input

# All components
npx shadcn@latest add --all
```

## Core Components

### Button

```tsx
import { Button } from "@/components/ui/button"

// Variants
<Button>Default</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon"><IconComponent /></Button>

// With loading state
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Please wait
</Button>

// As child (polymorphic)
<Button asChild>
  <Link href="/login">Login</Link>
</Button>
```

### Card

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Dialog

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        Dialog description goes here.
      </DialogDescription>
    </DialogHeader>
    <div className="py-4">
      {/* Content */}
    </div>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="outline">Cancel</Button>
      </DialogClose>
      <Button>Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Form with React Hook Form + Zod

```tsx
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"

import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="you@example.com" {...field} />
              </FormControl>
              <FormDescription>Your email address</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

### Data Table

```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Status</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {data.map((row) => (
      <TableRow key={row.id}>
        <TableCell>{row.name}</TableCell>
        <TableCell>
          <Badge variant={row.status === 'active' ? 'default' : 'secondary'}>
            {row.status}
          </Badge>
        </TableCell>
        <TableCell className="text-right">${row.amount}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

## Customization

### Extending Button Variants

```tsx
// components/ui/button.tsx
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        // Add custom variant
        brand: "bg-amber-500 text-white hover:bg-amber-600",
        gradient: "bg-gradient-to-r from-violet-500 to-cyan-500 text-white hover:opacity-90",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        xl: "h-14 rounded-md px-10 text-lg",  // Add xl size
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### Custom Theme Colors

```css
/* globals.css */
@layer base {
  :root {
    /* Custom brand colors */
    --brand: 245 100% 60%;  /* violet */
    --brand-foreground: 0 0% 100%;
    
    /* Override primary */
    --primary: 245 100% 60%;
    --primary-foreground: 0 0% 100%;
  }
  
  .dark {
    --brand: 245 100% 70%;
  }
}
```

```tsx
// Use in components
<div className="bg-brand text-brand-foreground">Brand colored</div>
```

### Custom Border Radius

```css
:root {
  --radius: 0.75rem;  /* More rounded */
  /* Or */
  --radius: 0;  /* Sharp corners */
}
```

## Patterns

### Controlled Dialog

```tsx
'use client'
import { useState } from 'react'
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"

export function ControlledDialog() {
  const [open, setOpen] = useState(false)
  
  async function handleSubmit() {
    await saveData()
    setOpen(false)  // Close on success
  }
  
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Open</Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          {/* form fields */}
          <Button type="submit">Save</Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
```

### Combobox (Searchable Select)

```tsx
import { Check, ChevronsUpDown } from "lucide-react"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function Combobox({ options, value, onChange }) {
  const [open, setOpen] = useState(false)
  
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" role="combobox" aria-expanded={open}>
          {value ? options.find(o => o.value === value)?.label : "Select..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search..." />
          <CommandEmpty>No results.</CommandEmpty>
          <CommandGroup>
            {options.map((option) => (
              <CommandItem
                key={option.value}
                onSelect={() => {
                  onChange(option.value)
                  setOpen(false)
                }}
              >
                <Check
                  className={cn(
                    "mr-2 h-4 w-4",
                    value === option.value ? "opacity-100" : "opacity-0"
                  )}
                />
                {option.label}
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
```

### Toast Notifications

```tsx
// Setup in layout
import { Toaster } from "@/components/ui/toaster"

export default function Layout({ children }) {
  return (
    <>
      {children}
      <Toaster />
    </>
  )
}

// Use in components
import { useToast } from "@/components/ui/use-toast"

export function MyComponent() {
  const { toast } = useToast()
  
  function handleClick() {
    toast({
      title: "Success!",
      description: "Your changes have been saved.",
    })
    
    // Or with action
    toast({
      title: "Uh oh!",
      description: "Something went wrong.",
      variant: "destructive",
      action: <ToastAction altText="Try again">Try again</ToastAction>,
    })
  }
}
```

## Dark Mode

### With next-themes

```bash
npm install next-themes
```

```tsx
// app/providers.tsx
'use client'
import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  )
}

// Toggle component
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
    </Button>
  )
}
```

## Common Issues

### Hydration Mismatch with Theme

```tsx
// Use mounted state
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null
```

### Dialog/Popover Not Closing

```tsx
// Use controlled state
const [open, setOpen] = useState(false)
<Dialog open={open} onOpenChange={setOpen}>
```

### Form Not Validating

```tsx
// Ensure resolver is set
const form = useForm({
  resolver: zodResolver(schema),  // Required!
  defaultValues: { ... }
})
```
