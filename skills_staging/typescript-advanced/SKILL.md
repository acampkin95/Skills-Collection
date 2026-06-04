---
name: typescript-advanced
description: Advanced TypeScript with generics, conditional types, mapped types, infer, branded types, discriminated unions, and template literal types.
version: 2.0.0
reviewed: "2026-06-04"
---
# Advanced TypeScript Patterns

**Read the relevant reference file before starting work.**

## Quick Navigation

| Topic | Reference |
|-------|-----------|
| Generics, conditional types, infer, recursive types | [references/advanced-generics.md](references/advanced-generics.md) |
| Branded/opaque types, phantom types, type-safe IDs | [references/branded-types.md](references/branded-types.md) |
| Type challenges, practical puzzles, builders | [references/type-challenges.md](references/type-challenges.md) |

---

## Generics with Constraints

```typescript
// Constrain generic to objects with an id
function getById<T extends { id: string }>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id);
}

// Default type parameters
type ApiResponse<T = unknown, E = Error> = { data: T; error: E | null };
```

### Multiple Constraints

```typescript
// Intersection of constraints
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return Object.assign({}, a, b);
}

// Constrain to array-like
function getLength<T extends { length: number }>(obj: T): number {
  return obj.length;
}
```

### Generic Default Type Parameters

```typescript
// Default to unknown if not specified
type Container<T = unknown> = { value: T };

const c1: Container = { value: 'anything' };
const c2: Container<number> = { value: 42 };
```

---

## Conditional Types

### Basic Pattern

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<'hello'>; // true
type B = IsString<number>; // false
```

### Extracting Types with infer

```typescript
// Extract return type from function
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type Fn = () => string;
type Result = ReturnType<Fn>; // string
```

### Distributive Conditional Types

```typescript
// Conditional type that distributes over union types
type Flatten<T> = T extends Array<infer U> ? U : T;

type Str = Flatten<string[]>; // string
type Num = Flatten<number>; // number
type Union = Flatten<string[] | number>; // string | number
```

---

## Mapped Types

### Basic Mapped Type

```typescript
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

interface User {
  name: string;
  age: number;
}


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.