# Advanced Generics Reference

## Generic Constraints in Depth

### Property constraints

```typescript
// Require specific property
function prop<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Constrain to callable
function callWith<T extends (...args: any[]) => any>(
  fn: T,
  ...args: Parameters<T>
): ReturnType<T> {
  return fn(...args);
}

// Constrain to constructable
function create<T extends new (...args: any[]) => any>(
  Ctor: T,
  ...args: ConstructorParameters<T>
): InstanceType<T> {
  return new Ctor(...args);
}
```

### Mutual constraints between parameters

```typescript
// U must be a key of T
function pick<T, U extends keyof T>(obj: T, keys: U[]): Pick<T, U> {
  const result = {} as Pick<T, U>;
  for (const key of keys) result[key] = obj[key];
  return result;
}

// Value type must match the key's type
function setProperty<T, K extends keyof T>(obj: T, key: K, value: T[K]): void {
  obj[key] = value;
}
```

---

## Conditional Types with `infer`

### Extracting from complex structures

```typescript
// Extract element type from array
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;
type Num = ElementOf<number[]>; // number

// Extract value type from Map
type MapValue<T> = T extends Map<any, infer V> ? V : never;

// Extract resolved type of a Promise
type Resolved<T> = T extends Promise<infer U> ? Resolved<U> : T;

// Extract props from React component
type PropsOf<T> = T extends React.ComponentType<infer P> ? P : never;
```

### Multiple infer positions

```typescript
// Extract first and rest from tuple
type Head<T extends any[]> = T extends [infer H, ...any[]] ? H : never;
type Tail<T extends any[]> = T extends [any, ...infer R] ? R : [];

type First = Head<[1, 2, 3]>; // 1
type Rest = Tail<[1, 2, 3]>;  // [2, 3]

// Extract function parts
type FnParts<T> = T extends (this: infer This, ...args: infer A) => infer R
  ? { thisArg: This; args: A; return: R }
  : never;
```

### Conditional type chains

```typescript
type TypeName<T> =
  T extends string ? 'string' :
  T extends number ? 'number' :
  T extends boolean ? 'boolean' :
  T extends Function ? 'function' :
  T extends any[] ? 'array' :
  'object';
```

---

## Recursive Types

### Deeply nested transformations

```typescript
// DeepReadonly - make entire object tree readonly
type DeepReadonly<T> =
  T extends (infer U)[] ? ReadonlyArray<DeepReadonly<U>> :
  T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } :
  T;

// DeepPartial - make entire tree optional
type DeepPartial<T> =
  T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } :
  T;

// DeepRequired - inverse of DeepPartial
type DeepRequired<T> =
  T extends object ? { [K in keyof T]-?: DeepRequired<T[K]> } :
  T;
```

### Recursive path types

```typescript
// Get all dot-notation paths of an object
type Paths<T, Prefix extends string = ''> =
  T extends object
    ? {
        [K in keyof T & string]:
          | `${Prefix}${K}`
          | Paths<T[K], `${Prefix}${K}.`>
      }[keyof T & string]
    : never;

interface Config {
  db: { host: string; port: number };
  app: { name: string };
}

type ConfigPaths = Paths<Config>;
// 'db' | 'db.host' | 'db.port' | 'app' | 'app.name'
```

### Recursive JSON type

```typescript
type Json =
  | string
  | number
  | boolean
  | null
  | Json[]
  | { [key: string]: Json };
```

---

## Variadic Tuple Types

```typescript
// Concat tuples
type Concat<A extends any[], B extends any[]> = [...A, ...B];
type AB = Concat<[1, 2], [3, 4]>; // [1, 2, 3, 4]

// Prepend element
type Prepend<T, A extends any[]> = [T, ...A];

// Last element
type Last<T extends any[]> = T extends [...any[], infer L] ? L : never;
type L = Last<[1, 2, 3]>; // 3

// Typed zip function
function zip<A extends any[], B extends any[]>(
  a: [...A],
  b: [...B]
): { [K in keyof A]: K extends keyof B ? [A[K], B[K]] : never } {
  return a.map((x, i) => [x, b[i]]) as any;
}

const zipped = zip([1, 'hello'], [true, 42]);
// type: [[number, boolean], [string, number]]
```

---

## Higher-Kinded Type Workarounds

TypeScript lacks native HKTs, but we can approximate them:

```typescript
// Define a "type-level function" registry
interface TypeMap<T = unknown> {
  Array: Array<T>;
  Set: Set<T>;
  Promise: Promise<T>;
}

// Apply a "type constructor" by name
type Apply<F extends keyof TypeMap, T> = TypeMap<T>[F];

type StringArray = Apply<'Array', string>;     // string[]
type NumberSet = Apply<'Set', number>;          // Set<number>
type BoolPromise = Apply<'Promise', boolean>;   // Promise<boolean>

// Use in generic function signatures
function lift<F extends keyof TypeMap, T>(
  containerType: F,
  value: T
): Apply<F, T> {
  switch (containerType) {
    case 'Array': return [value] as any;
    case 'Set': return new Set([value]) as any;
    case 'Promise': return Promise.resolve(value) as any;
    default: throw new Error(`Unknown: ${containerType}`);
  }
}
```

---

## Generic Factory Patterns

### Builder pattern with generics

```typescript
class QueryBuilder<T extends Record<string, any>> {
  private filters: Partial<T> = {};

  where<K extends keyof T>(key: K, value: T[K]): this {
    this.filters[key] = value;
    return this;
  }

  build(): Partial<T> {
    return { ...this.filters };
  }
}

interface User { name: string; age: number; active: boolean }

const query = new QueryBuilder<User>()
  .where('name', 'Alice')     // value must be string
  .where('age', 30)            // value must be number
  // .where('age', 'thirty')   // ERROR: string not assignable to number
  .build();
```

### Type-safe factory with registry

```typescript
// Event map as registry
interface EventMap {
  login: { userId: string; timestamp: number };
  purchase: { item: string; amount: number };
  logout: { userId: string };
}

function createEvent<K extends keyof EventMap>(
  type: K,
  payload: EventMap[K]
): { type: K; payload: EventMap[K]; id: string } {
  return { type, payload, id: crypto.randomUUID() };
}

// Type-safe: payload shape is enforced per event type
const event = createEvent('purchase', { item: 'Book', amount: 29.99 });
```

### Constrained class factory

```typescript
// Mixin pattern with generic constraint
type Constructor<T = {}> = new (...args: any[]) => T;

function Timestamped<T extends Constructor>(Base: T) {
  return class extends Base {
    createdAt = new Date();
    updatedAt = new Date();

    touch() { this.updatedAt = new Date(); }
  };
}

function Tagged<T extends Constructor>(Base: T) {
  return class extends Base {
    tags: string[] = [];
    addTag(tag: string) { this.tags.push(tag); }
  };
}

class BaseEntity { id = crypto.randomUUID(); }

// Compose mixins
const TaggedTimestampedEntity = Tagged(Timestamped(BaseEntity));
const entity = new TaggedTimestampedEntity();
entity.touch();
entity.addTag('important');
```
