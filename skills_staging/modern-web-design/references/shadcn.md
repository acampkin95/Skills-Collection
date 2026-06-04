# ShadCN/UI Complete Guide - 2025

## Installation & Setup

### Initialize ShadCN

```bash
# New project with style selection
npx shadcn@latest init

# Available styles: Vega (classic), Nova (compact), Maia (rounded), Lyra (sharp), Mira (dense)

# Add components
npx shadcn@latest add button card dialog input label
npx shadcn@latest add dropdown-menu popover tooltip
npx shadcn@latest add tabs accordion collapsible
npx shadcn@latest add form select checkbox radio-group switch
npx shadcn@latest add table data-table
npx shadcn@latest add toast sonner
npx shadcn@latest add sheet drawer
npx shadcn@latest add avatar badge separator
npx shadcn@latest add skeleton progress spinner
npx shadcn@latest add alert alert-dialog
npx shadcn@latest add command calendar date-picker

# New 2025 components
npx shadcn@latest add field input-group
```

### Project Structure

```
src/
├── components/
│   └── ui/           # ShadCN components (auto-generated)
│       ├── button.tsx
│       ├── card.tsx
│       └── ...
├── lib/
│   └── utils.ts      # cn() utility function
└── styles/
    └── globals.css   # Theme CSS variables
```

### Core Utility Function

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## Theme Customization (OKLCH - 2025 Standard)

### globals.css with OKLCH

```css
@import "tailwindcss";

@layer base {
  :root {
    /* OKLCH provides perceptually uniform colors */
    --background: oklch(1 0 0);
    --foreground: oklch(0.145 0 0);
    
    /* Card */
    --card: oklch(1 0 0);
    --card-foreground: oklch(0.145 0 0);
    
    /* Popover */
    --popover: oklch(1 0 0);
    --popover-foreground: oklch(0.145 0 0);
    
    /* Primary brand color */
    --primary: oklch(0.205 0 0);
    --primary-foreground: oklch(0.985 0 0);
    
    /* Secondary */
    --secondary: oklch(0.97 0 0);
    --secondary-foreground: oklch(0.205 0 0);
    
    /* Muted */
    --muted: oklch(0.97 0 0);
    --muted-foreground: oklch(0.556 0 0);
    
    /* Accent */
    --accent: oklch(0.97 0 0);
    --accent-foreground: oklch(0.205 0 0);
    
    /* Destructive */
    --destructive: oklch(0.577 0.245 27.325);
    --destructive-foreground: oklch(0.985 0 0);
    
    /* Borders & inputs */
    --border: oklch(0.922 0 0);
    --input: oklch(0.922 0 0);
    --ring: oklch(0.708 0 0);
    
    /* Border radius */
    --radius: 0.5rem;
    
    /* Chart colors (OKLCH for consistent lightness) */
    --chart-1: oklch(0.646 0.222 16.439);
    --chart-2: oklch(0.6 0.118 184.704);
    --chart-3: oklch(0.398 0.07 227.392);
    --chart-4: oklch(0.828 0.189 84.429);
    --chart-5: oklch(0.769 0.188 70.08);
  }

  .dark {
    --background: oklch(0.145 0 0);
    --foreground: oklch(0.985 0 0);
    --card: oklch(0.145 0 0);
    --card-foreground: oklch(0.985 0 0);
    --popover: oklch(0.145 0 0);
    --popover-foreground: oklch(0.985 0 0);
    --primary: oklch(0.985 0 0);
    --primary-foreground: oklch(0.205 0 0);
    --secondary: oklch(0.269 0 0);
    --secondary-foreground: oklch(0.985 0 0);
    --muted: oklch(0.269 0 0);
    --muted-foreground: oklch(0.708 0 0);
    --accent: oklch(0.269 0 0);
    --accent-foreground: oklch(0.985 0 0);
    --destructive: oklch(0.396 0.141 25.723);
    --destructive-foreground: oklch(0.985 0 0);
    --border: oklch(0.269 0 0);
    --input: oklch(0.269 0 0);
    --ring: oklch(0.439 0 0);
  }
}

/* Tailwind v4 theme integration */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-muted: var(--muted);
  --color-accent: var(--accent);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}
```

### Custom Brand Colors (OKLCH)

```css
/* Blue theme */
.theme-blue {
  --primary: oklch(0.546 0.245 262.881);
  --primary-foreground: oklch(0.985 0 0);
}

/* Emerald theme */
.theme-emerald {
  --primary: oklch(0.696 0.17 162.48);
  --primary-foreground: oklch(0.985 0 0);
}

/* Rose theme */
.theme-rose {
  --primary: oklch(0.645 0.246 16.439);
  --primary-foreground: oklch(0.985 0 0);
}

/* Orange theme */
.theme-orange {
  --primary: oklch(0.705 0.213 47.604);
  --primary-foreground: oklch(0.985 0 0);
}

/* Purple theme */
.theme-purple {
  --primary: oklch(0.627 0.265 303.9);
  --primary-foreground: oklch(0.985 0 0);
}
```

## React 19 Component Patterns

### No More forwardRef

```tsx
// React 19 - ref is just a regular prop
function AccordionItem({
  className,
  ref,
  ...props
}: React.ComponentProps<typeof AccordionPrimitive.Item> & {
  ref?: React.Ref<HTMLDivElement>;
}) {
  return (
    <AccordionPrimitive.Item
      ref={ref}
      data-slot="accordion-item"
      className={cn("border-b last:border-b-0", className)}
      {...props}
    />
  );
}

// Usage - refs work naturally
function Parent() {
  const ref = useRef<HTMLDivElement>(null);
  return <AccordionItem ref={ref} value="item-1">...</AccordionItem>;
}
```

### Button Variants (Updated for Tailwind v4)

```tsx
// components/ui/button.tsx
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  // Note: outline-hidden replaces outline-none in Tailwind v4
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-sm hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground shadow-xs hover:bg-destructive/90",
        outline: "border border-input bg-background shadow-xs hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        // Custom additions
        success: "bg-emerald-600 text-white shadow-sm hover:bg-emerald-700",
        warning: "bg-amber-500 text-white shadow-sm hover:bg-amber-600",
        gradient: "bg-gradient-to-r from-primary to-purple-600 text-white shadow-sm hover:opacity-90",
        glow: "bg-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3 text-xs",
        lg: "h-11 rounded-md px-8",
        xl: "h-14 rounded-lg px-10 text-base",
        icon: "h-10 w-10",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-12 w-12",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}
```

## New 2025 Components

### Field Component (Form Layouts)

```tsx
import { Field, FieldContent, FieldLabel, FieldDescription } from "@/components/ui/field"

// Horizontal layout
<Field orientation="horizontal">
  <FieldContent>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <FieldDescription>We'll never share your email</FieldDescription>
  </FieldContent>
  <Input id="email" type="email" />
</Field>

// Responsive layout (stacks on mobile)
<Field orientation="responsive">
  <FieldContent>
    <FieldLabel htmlFor="name">Full Name</FieldLabel>
    <FieldDescription>Enter your legal name</FieldDescription>
  </FieldContent>
  <Input id="name" />
</Field>

// With error state
<Field orientation="vertical">
  <FieldLabel htmlFor="password">Password</FieldLabel>
  <Input id="password" type="password" aria-invalid={!!error} />
  {error && <FieldError>{error}</FieldError>}
</Field>
```

### Input Group (Addons)

```tsx
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group"

// With icon addon
<InputGroup>
  <InputGroupAddon><SearchIcon className="h-4 w-4" /></InputGroupAddon>
  <InputGroupInput placeholder="Search..." />
</InputGroup>

// With text addons
<InputGroup>
  <InputGroupAddon><span>https://</span></InputGroupAddon>
  <InputGroupInput placeholder="example.com" />
  <InputGroupAddon><span>.com</span></InputGroupAddon>
</InputGroup>

// Currency input
<InputGroup>
  <InputGroupAddon><DollarIcon className="h-4 w-4" /></InputGroupAddon>
  <InputGroupInput type="number" placeholder="0.00" />
  <InputGroupAddon><span>USD</span></InputGroupAddon>
</InputGroup>
```

## Form Patterns with React 19

### useActionState Pattern

```tsx
'use client';
import { useActionState } from 'react';
import { Form, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

async function updateProfile(prevState: any, formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  
  try {
    await saveToDatabase({ name, email });
    return { error: null, success: true };
  } catch (e) {
    return { error: 'Update failed', success: false };
  }
}

export function ProfileForm() {
  const [state, formAction, isPending] = useActionState(
    updateProfile,
    { error: null, success: false }
  );
  
  return (
    <form action={formAction} className="space-y-6">
      <Field>
        <FieldLabel htmlFor="name">Name</FieldLabel>
        <Input id="name" name="name" required />
      </Field>
      
      <Field>
        <FieldLabel htmlFor="email">Email</FieldLabel>
        <Input id="email" name="email" type="email" required />
      </Field>
      
      <Button type="submit" disabled={isPending}>
        {isPending ? 'Saving...' : 'Save'}
      </Button>
      
      {state.error && (
        <p className="text-sm text-destructive">{state.error}</p>
      )}
      {state.success && (
        <p className="text-sm text-emerald-600">Profile updated!</p>
      )}
    </form>
  );
}
```

### useOptimistic Pattern

```tsx
'use client';
import { useOptimistic, startTransition } from 'react';

interface Comment {
  id: string;
  text: string;
  isPending?: boolean;
}

export function CommentList({ 
  comments, 
  onAddComment 
}: { 
  comments: Comment[];
  onAddComment: (text: string) => Promise<void>;
}) {
  const [optimisticComments, addOptimistic] = useOptimistic(
    comments,
    (state, newComment: string) => [
      ...state,
      { id: crypto.randomUUID(), text: newComment, isPending: true }
    ]
  );
  
  async function handleSubmit(formData: FormData) {
    const text = formData.get('comment') as string;
    
    startTransition(async () => {
      addOptimistic(text);
      await onAddComment(text);
    });
  }
  
  return (
    <div>
      <ul className="space-y-2">
        {optimisticComments.map(comment => (
          <li 
            key={comment.id}
            className={cn(
              "p-3 rounded-lg bg-muted",
              comment.isPending && "opacity-60"
            )}
          >
            {comment.text}
            {comment.isPending && <span className="ml-2 text-xs">Posting...</span>}
          </li>
        ))}
      </ul>
      
      <form action={handleSubmit} className="mt-4 flex gap-2">
        <Input name="comment" placeholder="Add a comment..." />
        <Button type="submit">Post</Button>
      </form>
    </div>
  );
}
```

## Dialog/Modal Pattern

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"

function ControlledDialog() {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Profile</DialogTitle>
          <DialogDescription>
            Make changes to your profile here. Click save when done.
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          {/* Form content */}
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={() => setOpen(false)}>Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

## Toast Notifications (Sonner)

```tsx
import { toast } from "sonner"
import { Toaster } from "@/components/ui/sonner"

// In layout
export default function Layout({ children }) {
  return (
    <>
      {children}
      <Toaster richColors position="top-right" />
    </>
  );
}

// Usage
function Component() {
  return (
    <>
      <Button onClick={() => toast.success("Successfully saved!")}>
        Success
      </Button>
      <Button onClick={() => toast.error("Something went wrong")}>
        Error
      </Button>
      <Button
        onClick={() =>
          toast.promise(saveData(), {
            loading: "Saving...",
            success: "Data saved successfully!",
            error: "Failed to save data",
          })
        }
      >
        With Promise
      </Button>
      <Button
        onClick={() =>
          toast("Event created", {
            description: "Monday, January 3rd at 6:00 PM",
            action: {
              label: "Undo",
              onClick: () => console.log("Undo"),
            },
          })
        }
      >
        With Action
      </Button>
    </>
  );
}
```

## Command Palette (Cmd+K)

```tsx
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"

function CommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>
            <CalendarIcon className="mr-2 h-4 w-4" />
            Calendar
            <CommandShortcut>⌘C</CommandShortcut>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
```

## Dark Mode Implementation

```tsx
// components/theme-toggle.tsx
"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ThemeToggle() {
  const { setTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

```tsx
// app/providers.tsx
"use client"

import { ThemeProvider } from "next-themes"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  );
}
```

## Best Practices

1. **Keep components in ui/ folder** - Don't modify in place, extend via composition
2. **Use cn() for all class merging** - Ensures proper Tailwind class priority
3. **Prefer asChild over wrapper divs** - Maintains semantic HTML
4. **Use controlled components for complex state** - Don't fight the library
5. **Extend variants, don't override defaults** - Add new variants instead
6. **Keep theme in CSS variables** - Single source of truth for colors
7. **Use OKLCH for colors** - Perceptually uniform, better dark mode
8. **No forwardRef in React 19** - ref is just a prop now
9. **Use data-slot for styling** - ShadCN convention for nested elements
10. **Use Radix primitives** - ShadCN is built on Radix, understand the patterns
