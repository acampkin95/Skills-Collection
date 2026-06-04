# Branded / Opaque Types Reference

## The Problem

TypeScript uses structural typing, so identical shapes are interchangeable:

```typescript
type UserId = string;
type PostId = string;

function getPost(postId: PostId) { /* ... */ }

const userId: UserId = 'user_123';
getPost(userId); // No error! Both are just string
```

Branded types add a phantom property to create nominal-like typing.

---

## Creating Branded Types

### Basic brand pattern

```typescript
// The brand symbol (unique to prevent collisions)
declare const __brand: unique symbol;

type Brand<T, B extends string> = T & { readonly [__brand]: B };

// Define branded types
type UserId = Brand<string, 'UserId'>;
type PostId = Brand<string, 'PostId'>;

// Constructor functions (the only way to create branded values)
function UserId(id: string): UserId { return id as UserId; }
function PostId(id: string): PostId { return id as PostId; }

// Now this is an error
function getPost(postId: PostId) { /* ... */ }
const userId = UserId('user_123');
// getPost(userId); // ERROR: UserId not assignable to PostId

const postId = PostId('post_456');
getPost(postId); // OK
```

### Alternative: intersection brand

```typescript
type Branded<T, Brand extends string> = T & { __brand: Brand };

type Email = Branded<string, 'Email'>;
type URL = Branded<string, 'URL'>;

// Branded values are still usable as their base type
const email = 'user@example.com' as Email;
email.toUpperCase(); // OK - string methods work
```

---

## Phantom Types

Phantom types carry type information without runtime representation:

```typescript
// Currency-safe arithmetic
type Currency<C extends string> = number & { readonly __currency: C };
type USD = Currency<'USD'>;
type EUR = Currency<'EUR'>;

function usd(amount: number): USD { return amount as USD; }
function eur(amount: number): EUR { return amount as EUR; }

function addUSD(a: USD, b: USD): USD {
  return (a + b) as USD;
}

const price = usd(10);
const tax = usd(2);
const fee = eur(5);

addUSD(price, tax); // OK
// addUSD(price, fee); // ERROR: EUR not assignable to USD
```

---

## Type-Safe IDs

### Per-entity ID types

```typescript
declare const __brand: unique symbol;
type Brand<T, B extends string> = T & { readonly [__brand]: B };

// ID types for each entity
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;
type ProductId = Brand<string, 'ProductId'>;

// Generic ID constructor
function makeId<B extends string>(brand: B) {
  return (raw: string): Brand<string, B> => raw as Brand<string, B>;
}

const userId = makeId('UserId');
const orderId = makeId('OrderId');
const productId = makeId('ProductId');

// Usage
interface Order {
  id: OrderId;
  userId: UserId;
  products: ProductId[];
}

function getOrder(id: OrderId): Order { /* ... */ }
function getUser(id: UserId): void { /* ... */ }

const oid = orderId('ord_123');
const uid = userId('usr_456');

getOrder(oid); // OK
// getOrder(uid); // ERROR: UserId not assignable to OrderId
```

### Numeric IDs

```typescript
type NumericId<B extends string> = number & { readonly __brand: B };
type RowId = NumericId<'RowId'>;
type Timestamp = NumericId<'Timestamp'>;

function RowId(n: number): RowId { return n as RowId; }
function Timestamp(n: number): Timestamp { return n as Timestamp; }

// Arithmetic still works
const row = RowId(1);
const nextRow = RowId(row + 1); // Must re-brand after arithmetic
```

---

## Type-Safe Units

```typescript
type Meters = Brand<number, 'Meters'>;
type Kilometers = Brand<number, 'Kilometers'>;
type Seconds = Brand<number, 'Seconds'>;
type MetersPerSecond = Brand<number, 'MetersPerSecond'>;

function meters(n: number): Meters { return n as Meters; }
function km(n: number): Kilometers { return n as Kilometers; }
function seconds(n: number): Seconds { return n as Seconds; }

function speed(distance: Meters, time: Seconds): MetersPerSecond {
  return (distance / time) as MetersPerSecond;
}

function kmToMeters(d: Kilometers): Meters {
  return (d * 1000) as Meters;
}

const dist = meters(100);
const time = seconds(10);
const v = speed(dist, time); // OK: MetersPerSecond

// speed(km(5), time); // ERROR: Kilometers not assignable to Meters
speed(kmToMeters(km(5)), time); // OK: explicit conversion
```

---

## Runtime Validation Bridges

Branded types should pair with runtime validation:

```typescript
type Email = Brand<string, 'Email'>;
type PositiveInt = Brand<number, 'PositiveInt'>;
type NonEmptyString = Brand<string, 'NonEmptyString'>;

// Validated constructors that return Result-like types
function parseEmail(input: string): Email {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!re.test(input)) throw new Error(`Invalid email: ${input}`);
  return input as Email;
}

function positiveInt(n: number): PositiveInt {
  if (!Number.isInteger(n) || n <= 0) throw new Error(`Not a positive int: ${n}`);
  return n as PositiveInt;
}

function nonEmpty(s: string): NonEmptyString {
  if (s.trim().length === 0) throw new Error('String is empty');
  return s as NonEmptyString;
}

// Safe variant returning union
function safeParseEmail(input: string): Email | null {
  try { return parseEmail(input); }
  catch { return null; }
}
```

### Using type guards with brands

```typescript
function isEmail(input: string): input is Email {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input);
}

function processInput(input: string) {
  if (isEmail(input)) {
    sendEmail(input); // input is Email here
  }
}

function sendEmail(to: Email) { /* ... */ }
```

---

## Zod Integration

```typescript
import { z } from 'zod';

// Define branded type
type Email = Brand<string, 'Email'>;

// Zod schema that produces branded output
const EmailSchema = z
  .string()
  .email()
  .transform((val): Email => val as Email);

// Parse returns branded type
const result = EmailSchema.parse('user@example.com'); // type: Email

// Full entity schema with branded IDs
type UserId = Brand<string, 'UserId'>;

const UserIdSchema = z
  .string()
  .uuid()
  .transform((val): UserId => val as UserId);

const UserSchema = z.object({
  id: UserIdSchema,
  email: EmailSchema,
  name: z.string().min(1),
});

type User = z.infer<typeof UserSchema>;
// { id: UserId; email: Email; name: string }
```

### Zod branded() built-in

```typescript
// Zod has a built-in brand method
const EmailZ = z.string().email().brand<'Email'>();
type EmailZ = z.infer<typeof EmailZ>; // string & { __brand: 'Email' }

const UserZ = z.object({
  id: z.string().uuid().brand<'UserId'>(),
  email: EmailZ,
});
```

---

## Best Practices

| Practice | Reason |
|----------|--------|
| Always provide constructor functions | Prevents raw `as` casts in consumer code |
| Pair brands with runtime validation | Brands are meaningless without validation |
| Use `unique symbol` for brand key | Prevents accidental brand collisions |
| Keep branded types in a shared module | Single source of truth for type + constructor |
| Document conversion functions | `kmToMeters`, `emailToString`, etc. |
| Don't over-brand | Only brand types that are genuinely confused |
