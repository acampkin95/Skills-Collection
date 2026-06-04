# Forms & Validation Patterns

## Form Libraries

### React Hook Form + Zod (Recommended)

```bash
npm install react-hook-form @hookform/resolvers zod
```

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

// Schema
const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

type FormData = z.infer<typeof schema>

// Component
export function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    await submitToAPI(data)
    reset()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register('email')}
          aria-invalid={errors.email ? 'true' : undefined}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p id="email-error" role="alert" className="text-red-500 text-sm">
            {errors.email.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          {...register('password')}
          aria-invalid={errors.password ? 'true' : undefined}
        />
        {errors.password && (
          <p role="alert" className="text-red-500 text-sm">
            {errors.password.message}
          </p>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Sign Up'}
      </button>
    </form>
  )
}
```

### Server Actions (Next.js 15)

```tsx
// actions.ts
'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'

const schema = z.object({
  title: z.string().min(1, 'Required'),
  content: z.string().min(10, 'Min 10 characters'),
})

export type State = {
  errors?: { title?: string[]; content?: string[] }
  message?: string
} | null

export async function createPost(prevState: State, formData: FormData): Promise<State> {
  const parsed = schema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  })

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors }
  }

  try {
    await db.post.create({ data: parsed.data })
    revalidatePath('/posts')
    return { message: 'Post created!' }
  } catch (e) {
    return { message: 'Database error' }
  }
}

// Component
'use client'
import { useActionState } from 'react'
import { createPost, type State } from './actions'

export function CreatePostForm() {
  const [state, formAction, pending] = useActionState<State, FormData>(createPost, null)

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <label htmlFor="title">Title</label>
        <input id="title" name="title" disabled={pending} />
        {state?.errors?.title && (
          <p className="text-red-500">{state.errors.title[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="content">Content</label>
        <textarea id="content" name="content" disabled={pending} />
        {state?.errors?.content && (
          <p className="text-red-500">{state.errors.content[0]}</p>
        )}
      </div>

      <button type="submit" disabled={pending}>
        {pending ? 'Creating...' : 'Create Post'}
      </button>

      {state?.message && <p className="text-green-500">{state.message}</p>}
    </form>
  )
}
```

## Zod Schema Patterns

### Common Validations

```typescript
import { z } from 'zod'

// String validations
const stringSchema = z.object({
  required: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
  url: z.string().url('Invalid URL'),
  uuid: z.string().uuid(),
  minMax: z.string().min(2).max(100),
  regex: z.string().regex(/^[A-Z]+$/, 'Uppercase only'),
  trim: z.string().trim(),
  lowercase: z.string().toLowerCase(),
})

// Number validations
const numberSchema = z.object({
  age: z.number().int().positive().max(120),
  price: z.number().positive().multipleOf(0.01),
  quantity: z.coerce.number().int().min(1),  // Coerce from string
})

// Date validations
const dateSchema = z.object({
  birthDate: z.coerce.date(),
  futureDate: z.date().min(new Date(), 'Must be in future'),
})

// Boolean
const boolSchema = z.object({
  acceptTerms: z.literal(true, {
    errorMap: () => ({ message: 'Must accept terms' }),
  }),
})

// Arrays
const arraySchema = z.object({
  tags: z.array(z.string()).min(1, 'At least one tag'),
  items: z.array(z.object({
    name: z.string(),
    quantity: z.number(),
  })),
})

// Enums
const enumSchema = z.object({
  role: z.enum(['admin', 'user', 'guest']),
  status: z.nativeEnum(StatusEnum),
})

// Optional & Nullable
const optionalSchema = z.object({
  nickname: z.string().optional(),
  bio: z.string().nullable(),
  phone: z.string().nullish(),  // null | undefined
})

// Unions & Discriminated Unions
const paymentSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('card'), cardNumber: z.string() }),
  z.object({ type: z.literal('paypal'), email: z.string().email() }),
])
```

### Cross-Field Validation

```typescript
const passwordSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  }
)

// Multiple refinements
const dateRangeSchema = z.object({
  startDate: z.coerce.date(),
  endDate: z.coerce.date(),
}).refine(
  (data) => data.endDate > data.startDate,
  {
    message: 'End date must be after start date',
    path: ['endDate'],
  }
).refine(
  (data) => {
    const diff = data.endDate.getTime() - data.startDate.getTime()
    return diff <= 30 * 24 * 60 * 60 * 1000  // Max 30 days
  },
  {
    message: 'Range cannot exceed 30 days',
    path: ['endDate'],
  }
)
```

### Transform & Preprocess

```typescript
const profileSchema = z.object({
  // Transform output
  username: z.string().transform((val) => val.toLowerCase().trim()),
  
  // Preprocess input
  age: z.preprocess(
    (val) => (typeof val === 'string' ? parseInt(val, 10) : val),
    z.number().int().positive()
  ),
  
  // Default values
  role: z.string().default('user'),
  
  // Catch invalid with default
  count: z.number().catch(0),
})
```

## Form Components

### Reusable Input

```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  description?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, description, id, ...props }, ref) => {
    const inputId = id || label.toLowerCase().replace(/\s/g, '-')
    const errorId = `${inputId}-error`
    const descId = `${inputId}-desc`

    return (
      <div className="space-y-1">
        <label htmlFor={inputId} className="block text-sm font-medium">
          {label}
        </label>
        
        <input
          ref={ref}
          id={inputId}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={cn(
            error && errorId,
            description && descId
          )}
          className={cn(
            'block w-full rounded-md border px-3 py-2',
            error ? 'border-red-500' : 'border-gray-300'
          )}
          {...props}
        />
        
        {description && !error && (
          <p id={descId} className="text-sm text-gray-500">
            {description}
          </p>
        )}
        
        {error && (
          <p id={errorId} role="alert" className="text-sm text-red-500">
            {error}
          </p>
        )}
      </div>
    )
  }
)
```

### Form Field Wrapper

```tsx
interface FormFieldProps {
  name: string
  label: string
  control: Control<any>
  description?: string
  children?: (field: ControllerRenderProps) => React.ReactNode
}

export function FormField({
  name,
  label,
  control,
  description,
  children,
}: FormFieldProps) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className="space-y-1">
          <label htmlFor={name} className="block text-sm font-medium">
            {label}
          </label>
          
          {children ? (
            children(field)
          ) : (
            <input
              id={name}
              {...field}
              className="block w-full rounded-md border px-3 py-2"
            />
          )}
          
          {description && !fieldState.error && (
            <p className="text-sm text-gray-500">{description}</p>
          )}
          
          {fieldState.error && (
            <p role="alert" className="text-sm text-red-500">
              {fieldState.error.message}
            </p>
          )}
        </div>
      )}
    />
  )
}
```

## Advanced Patterns

### Multi-Step Form

```tsx
const steps = ['Account', 'Profile', 'Confirm'] as const

export function MultiStepForm() {
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({})

  const handleNext = (data: Partial<FormData>) => {
    setFormData(prev => ({ ...prev, ...data }))
    setStep(s => s + 1)
  }

  const handleBack = () => setStep(s => s - 1)

  return (
    <div>
      {/* Progress */}
      <div className="flex gap-2 mb-8">
        {steps.map((label, i) => (
          <div
            key={label}
            className={cn(
              'flex-1 h-2 rounded',
              i <= step ? 'bg-blue-500' : 'bg-gray-200'
            )}
          />
        ))}
      </div>

      {/* Steps */}
      {step === 0 && <AccountStep onNext={handleNext} />}
      {step === 1 && <ProfileStep onNext={handleNext} onBack={handleBack} />}
      {step === 2 && <ConfirmStep data={formData} onBack={handleBack} />}
    </div>
  )
}

function AccountStep({ onNext }: { onNext: (data: any) => void }) {
  const { register, handleSubmit } = useForm({
    resolver: zodResolver(accountSchema),
  })

  return (
    <form onSubmit={handleSubmit(onNext)}>
      <Input label="Email" {...register('email')} />
      <Input label="Password" type="password" {...register('password')} />
      <button type="submit">Next</button>
    </form>
  )
}
```

### Dynamic Form Fields

```tsx
const schema = z.object({
  items: z.array(z.object({
    name: z.string().min(1),
    quantity: z.coerce.number().min(1),
  })).min(1, 'At least one item'),
})

export function DynamicForm() {
  const { control, register, handleSubmit } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { items: [{ name: '', quantity: 1 }] },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  })

  return (
    <form onSubmit={handleSubmit(console.log)}>
      {fields.map((field, index) => (
        <div key={field.id} className="flex gap-2">
          <input {...register(`items.${index}.name`)} placeholder="Name" />
          <input
            {...register(`items.${index}.quantity`)}
            type="number"
            placeholder="Qty"
          />
          <button type="button" onClick={() => remove(index)}>
            Remove
          </button>
        </div>
      ))}

      <button type="button" onClick={() => append({ name: '', quantity: 1 })}>
        Add Item
      </button>

      <button type="submit">Submit</button>
    </form>
  )
}
```

### Debounced Validation

```tsx
export function SearchForm() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setIsSearching(true)
      const data = await searchAPI(query)
      setResults(data)
      setIsSearching(false)
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
        aria-describedby="search-status"
      />
      
      <div id="search-status" aria-live="polite">
        {isSearching && 'Searching...'}
        {!isSearching && results.length > 0 && `${results.length} results`}
      </div>

      <ul>
        {results.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

## Error Handling

### Focus First Error

```tsx
export function FormWithFocus() {
  const {
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onError = (errors: FieldErrors) => {
    const firstError = Object.keys(errors)[0]
    const element = document.querySelector(`[name="${firstError}"]`)
    element?.focus()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit, onError)}>
      {/* fields */}
    </form>
  )
}
```

### Toast on Success/Error

```tsx
import { toast } from 'sonner'

async function onSubmit(data: FormData) {
  try {
    await submitAPI(data)
    toast.success('Form submitted successfully!')
    reset()
  } catch (error) {
    if (error instanceof APIError) {
      toast.error(error.message)
    } else {
      toast.error('Something went wrong. Please try again.')
    }
  }
}
```
