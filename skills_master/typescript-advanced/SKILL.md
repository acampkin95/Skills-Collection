---
name: typescript-advanced
description: Advanced TypeScript patterns and type-safe abstractions.
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

type ReadonlyUser = Readonly<User>;
```

### Transform Property Names

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User {
  name: string;
  age: number;
}

type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number }
```

### Conditional Property Mapping

```typescript
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

interface Mixed {
  name: string;
  age: number;
  active: boolean;
}

type StringProps = PickByType<Mixed, string>; // { name: string }
```

---

## Branded Types (Opaque Types)

### Creating Type-Safe IDs

```typescript
type UserId = string & { readonly __brand: 'UserId' };

function createUserId(id: string): UserId {
  return id as UserId;
}

function getUserName(id: UserId): string {
  return `User: ${id}`;
}

const userId = createUserId('123');
getUserName(userId); // ✓ OK
// getUserName('123'); // ✗ Error: not a UserId
```

### Multiple Branded Types

```typescript
type Email = string & { readonly __brand: 'Email' };
type PhoneNumber = string & { readonly __brand: 'PhoneNumber' };

const validateEmail = (email: string): Email => {
  if (!email.includes('@')) throw new Error('Invalid email');
  return email as Email;
};

const sendEmail = (to: Email): void => {
  console.log(`Sending to ${to}`);
};

const email = validateEmail('user@example.com');
sendEmail(email); // ✓ OK
```

---

## Template Literal Types

### String Union Generation

```typescript
type Greeting = `Hello, ${'World' | 'TypeScript'}`;
// "Hello, World" | "Hello, TypeScript"
```

### Event Handler Names

```typescript
type EventType = 'click' | 'hover' | 'blur';
type EventHandler = `on${Capitalize<EventType>}`;
// "onClick" | "onHover" | "onBlur"
```

### Path Type Safety

```typescript
type Path = `/api/${'users' | 'posts'}/${'list' | 'detail'}`;
// "/api/users/list" | "/api/users/detail" | "/api/posts/list" | "/api/posts/detail"
```

---

## Type Guards

### typeof Guard

```typescript
function processValue(value: string | number): void {
  if (typeof value === 'string') {
    console.log(value.toUpperCase());
  } else {
    console.log(value.toFixed(2));
  }
}
```

### Custom Type Guard (is)

```typescript
interface User {
  name: string;
  age: number;
}

function isUser(obj: any): obj is User {
  return (
    typeof obj === 'object' &&
    typeof obj.name === 'string' &&
    typeof obj.age === 'number'
  );
}

const data: unknown = JSON.parse('{"name": "Alice", "age": 30}');

if (isUser(data)) {
  console.log(data.name, data.age); // type-safe access
}
```

### instanceof Guard

```typescript
class Dog {
  bark(): void {
    console.log('Woof!');
  }
}

class Cat {
  meow(): void {
    console.log('Meow!');
  }
}

function makeSound(animal: Dog | Cat): void {
  if (animal instanceof Dog) {
    animal.bark();
  } else {
    animal.meow();
  }
}
```

---

## Discriminated Unions

### Basic Pattern

```typescript
type Circle = {
  kind: 'circle';
  radius: number;
};

type Square = {
  kind: 'square';
  sideLength: number;
};

type Shape = Circle | Square;

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'square':
      return shape.sideLength ** 2;
  }
}
```

### Result Type Pattern

```typescript
type Success<T> = {
  status: 'success';
  data: T;
};

type Error = {
  status: 'error';
  message: string;
};

type Result<T> = Success<T> | Error;

function handleResult<T>(result: Result<T>): void {
  if (result.status === 'success') {
    console.log(result.data);
  } else {
    console.log(result.message);
  }
}
```

---

## Module Augmentation

### Extending Global Types

```typescript
// global.d.ts
declare global {
  interface Window {
    myCustomAPI: {
      doSomething(): void;
    };
  }
}

export {};

// usage.ts
window.myCustomAPI.doSomething(); // ✓ Type-safe
```

### Extending Library Types

```typescript
import 'express';

declare global {
  namespace Express {
    interface Request {
      userId?: string;
    }
  }
}

// middleware
app.use((req: express.Request, res, next) => {
  req.userId = 'user123'; // ✓ OK
  next();
});
```

---

## Utility Types Reference

| Utility | Purpose |
|---------|---------|
| `Partial<T>` | All properties optional |
| `Required<T>` | All properties required |
| `Readonly<T>` | All properties readonly |
| `Record<K, T>` | Object with keys K of type T |
| `Pick<T, K>` | Extract specific properties |
| `Omit<T, K>` | Exclude specific properties |
| `Exclude<T, U>` | Remove types assignable to U |
| `Extract<T, U>` | Keep types assignable to U |
| `NonNullable<T>` | Remove null and undefined |
| `Parameters<T>` | Extract function parameter types |
| `ReturnType<T>` | Extract function return type |
| `InstanceType<T>` | Extract constructor instance type |

---

## Decorators

### Class Decorators

```typescript
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class BugReport {
  title: string;
  constructor(t: string) {
    this.title = t;
  }
}
```

### Method Decorators

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return originalMethod.apply(this, args);
  };
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}
```

### Property Decorators

```typescript
function readonly(target: any, propertyKey: string) {
  Object.defineProperty(target, propertyKey, {
    writable: false,
  });
}

class User {
  @readonly
  id: string = 'user-123';
}
```

---

## Best Practices

1. **Use generic constraints** to restrict types and improve inference
2. **Leverage conditional types** for complex type relationships
3. **Create branded types** for semantic type safety (IDs, emails, URLs)
4. **Use discriminated unions** for exhaustive type checking
5. **Keep mapped types readable** — add comments explaining transformations
6. **Combine patterns** — conditionals + mapped types unlock powerful abstractions
7. **Test your types** — use type assertions sparingly and document why
8. **Profile complexity** — deeply nested generics impact compile times

---

## Resources

| Resource | Purpose |
|----------|---------|
| [TypeScript Handbook: Advanced Types](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html) | Official guide to advanced type features |
| [TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html) | Generic types and constraints |
| [TypeScript Handbook: Decorators](https://www.typescriptlang.org/docs/handbook/decorators.html) | Decorator syntax and patterns |
