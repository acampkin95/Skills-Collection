# Type Challenges Reference

Practical type-level puzzles and real-world patterns.

---

## Challenge 1: Implement Pick

```typescript
// Built-in Pick selects properties from a type
type MyPick<T, K extends keyof T> = {
  [P in K]: T[P];
};

// Test
interface Todo {
  title: string;
  description: string;
  done: boolean;
}

type TodoPreview = MyPick<Todo, 'title' | 'done'>;
// { title: string; done: boolean }
```

---

## Challenge 2: Implement DeepReadonly

```typescript
type DeepReadonly<T> =
  T extends Function ? T :
  T extends (infer U)[] ? ReadonlyArray<DeepReadonly<U>> :
  T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } :
  T;

// Test
interface Nested {
  a: { b: { c: number } };
  d: string[];
}

type ReadonlyNested = DeepReadonly<Nested>;
// All properties at every level are readonly
// readonlyNested.a.b.c = 1; // ERROR
```

---

## Challenge 3: Implement Flatten

```typescript
// Flatten one level
type Flatten<T extends any[]> = T extends [infer Head, ...infer Tail]
  ? Head extends any[]
    ? [...Head, ...Flatten<Tail>]
    : [Head, ...Flatten<Tail>]
  : [];

type Flat = Flatten<[[1, 2], [3], 4]>; // [1, 2, 3, 4]

// Deep flatten
type DeepFlatten<T> = T extends [infer Head, ...infer Tail]
  ? Head extends any[]
    ? [...DeepFlatten<Head>, ...DeepFlatten<Tail>]
    : [Head, ...DeepFlatten<Tail>]
  : T extends any[] ? T : [T];

type Deep = DeepFlatten<[[1, [2, [3]]], 4]>; // [1, 2, 3, 4]
```

---

## Challenge 4: Type-Safe Event Emitter

```typescript
interface EventMap {
  connect: { host: string; port: number };
  message: { text: string; from: string };
  disconnect: { reason: string };
}

class TypedEmitter<Events extends Record<string, any>> {
  private listeners = new Map<string, Set<Function>>();

  on<K extends keyof Events>(
    event: K,
    handler: (payload: Events[K]) => void
  ): this {
    if (!this.listeners.has(event as string)) {
      this.listeners.set(event as string, new Set());
    }
    this.listeners.get(event as string)!.add(handler);
    return this;
  }

  off<K extends keyof Events>(
    event: K,
    handler: (payload: Events[K]) => void
  ): this {
    this.listeners.get(event as string)?.delete(handler);
    return this;
  }

  emit<K extends keyof Events>(event: K, payload: Events[K]): void {
    this.listeners.get(event as string)?.forEach(fn => fn(payload));
  }
}

// Usage - fully type-safe
const emitter = new TypedEmitter<EventMap>();

emitter.on('connect', ({ host, port }) => {
  console.log(`Connected to ${host}:${port}`);
});

emitter.emit('message', { text: 'hello', from: 'alice' }); // OK
// emitter.emit('message', { text: 'hello' }); // ERROR: missing 'from'
// emitter.emit('unknown', {}); // ERROR: 'unknown' not in EventMap
```

---

## Challenge 5: Type-Safe API Client Builder

```typescript
// Define API schema at type level
interface ApiSchema {
  '/users': {
    GET: { response: { id: string; name: string }[] };
    POST: { body: { name: string; email: string }; response: { id: string } };
  };
  '/users/:id': {
    GET: { response: { id: string; name: string; email: string } };
    PUT: { body: { name?: string; email?: string }; response: { id: string } };
    DELETE: { response: void };
  };
}

// Extract route params from path
type ExtractParams<P extends string> =
  P extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractParams<`/${Rest}`>
    : P extends `${string}:${infer Param}`
      ? Param
      : never;

type ParamsRecord<P extends string> =
  [ExtractParams<P>] extends [never]
    ? {}
    : Record<ExtractParams<P>, string>;

// Request config type
type RequestConfig<
  Schema extends Record<string, any>,
  Path extends keyof Schema & string,
  Method extends keyof Schema[Path] & string
> = {
  params: ParamsRecord<Path>;
} & (Schema[Path][Method] extends { body: infer B } ? { body: B } : {});

// Response type
type ResponseType<
  Schema extends Record<string, any>,
  Path extends keyof Schema & string,
  Method extends keyof Schema[Path] & string
> = Schema[Path][Method] extends { response: infer R } ? R : never;

// The client class
class ApiClient<Schema extends Record<string, any>> {
  constructor(private baseUrl: string) {}

  async request<
    Path extends keyof Schema & string,
    Method extends keyof Schema[Path] & string
  >(
    method: Method,
    path: Path,
    config: RequestConfig<Schema, Path, Method>
  ): Promise<ResponseType<Schema, Path, Method>> {
    // Implementation: replace :params, build request, etc.
    const url = this.buildUrl(path, (config as any).params);
    const res = await fetch(`${this.baseUrl}${url}`, {
      method,
      body: 'body' in config ? JSON.stringify((config as any).body) : undefined,
      headers: { 'Content-Type': 'application/json' },
    });
    return res.json();
  }

  private buildUrl(path: string, params: Record<string, string>): string {
    return path.replace(/:(\w+)/g, (_, key) => params[key] ?? '');
  }
}

// Usage
const api = new ApiClient<ApiSchema>('https://api.example.com');

// All type-safe:
const users = await api.request('GET', '/users', { params: {} });
// users: { id: string; name: string }[]

const user = await api.request('GET', '/users/:id', { params: { id: '123' } });
// user: { id: string; name: string; email: string }

const created = await api.request('POST', '/users', {
  params: {},
  body: { name: 'Alice', email: 'alice@example.com' },
});
// created: { id: string }
```

---

## Challenge 6: Type-Safe Form Validation

```typescript
// Define validation rules at type level
type ValidationRule<T> =
  | { type: 'required' }
  | { type: 'minLength'; value: number }
  | { type: 'maxLength'; value: number }
  | { type: 'pattern'; value: RegExp }
  | { type: 'custom'; validate: (value: T) => boolean; message: string };

type FieldConfig<T> = {
  defaultValue: T;
  rules: ValidationRule<T>[];
};

type FormSchema = Record<string, FieldConfig<any>>;

// Infer form values from schema
type FormValues<S extends FormSchema> = {
  [K in keyof S]: S[K]['defaultValue'];
};

// Infer error shape
type FormErrors<S extends FormSchema> = {
  [K in keyof S]?: string;
};

// Form state
type FormState<S extends FormSchema> = {
  values: FormValues<S>;
  errors: FormErrors<S>;
  touched: { [K in keyof S]?: boolean };
  isValid: boolean;
};

// The form class
class TypedForm<S extends FormSchema> {
  private state: FormState<S>;

  constructor(private schema: S) {
    const values = {} as FormValues<S>;
    for (const key in schema) {
      values[key] = schema[key].defaultValue;
    }
    this.state = { values, errors: {}, touched: {}, isValid: true };
  }

  setValue<K extends keyof S & string>(field: K, value: S[K]['defaultValue']): void {
    this.state.values[field] = value;
    this.state.touched[field] = true;
    this.validateField(field);
  }

  getValue<K extends keyof S & string>(field: K): S[K]['defaultValue'] {
    return this.state.values[field];
  }

  private validateField<K extends keyof S & string>(field: K): void {
    const config = this.schema[field];
    const value = this.state.values[field];

    for (const rule of config.rules) {
      switch (rule.type) {
        case 'required':
          if (!value) this.state.errors[field] = 'Required' as any;
          break;
        case 'minLength':
          if (typeof value === 'string' && value.length < rule.value)
            this.state.errors[field] = `Min length: ${rule.value}` as any;
          break;
        case 'custom':
          if (!rule.validate(value))
            this.state.errors[field] = rule.message as any;
          break;
      }
    }
  }

  getState(): Readonly<FormState<S>> {
    return this.state;
  }
}

// Usage
const loginForm = new TypedForm({
  email: {
    defaultValue: '' as string,
    rules: [
      { type: 'required' },
      { type: 'pattern', value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
    ],
  },
  password: {
    defaultValue: '' as string,
    rules: [
      { type: 'required' },
      { type: 'minLength', value: 8 },
    ],
  },
  rememberMe: {
    defaultValue: false as boolean,
    rules: [],
  },
});

loginForm.setValue('email', 'user@test.com');    // OK: string
loginForm.setValue('rememberMe', true);           // OK: boolean
// loginForm.setValue('email', 123);              // ERROR: number not string
// loginForm.setValue('missing', 'x');            // ERROR: 'missing' not in schema
```

---

## Challenge 7: Implement String Utilities

```typescript
// Trim whitespace from both ends (type level)
type TrimLeft<S extends string> =
  S extends ` ${infer R}` ? TrimLeft<R> : S;

type TrimRight<S extends string> =
  S extends `${infer R} ` ? TrimRight<R> : S;

type Trim<S extends string> = TrimLeft<TrimRight<S>>;

type Trimmed = Trim<'  hello world  '>; // 'hello world'

// Replace all occurrences
type ReplaceAll<
  S extends string,
  From extends string,
  To extends string
> = From extends ''
  ? S
  : S extends `${infer L}${From}${infer R}`
    ? `${L}${To}${ReplaceAll<R, From, To>}`
    : S;

type Replaced = ReplaceAll<'foo-bar-baz', '-', '_'>; // 'foo_bar_baz'

// Split string into tuple
type Split<
  S extends string,
  D extends string
> = S extends `${infer Head}${D}${infer Tail}`
  ? [Head, ...Split<Tail, D>]
  : [S];

type Parts = Split<'a.b.c', '.'>; // ['a', 'b', 'c']

// Join tuple into string
type Join<
  T extends string[],
  D extends string
> = T extends [infer H extends string]
  ? H
  : T extends [infer H extends string, ...infer R extends string[]]
    ? `${H}${D}${Join<R, D>}`
    : '';

type Joined = Join<['a', 'b', 'c'], '-'>; // 'a-b-c'
```

---

## Challenge 8: Type-Safe State Machine

```typescript
// Define states and transitions at type level
type StateMachine<
  States extends string,
  Transitions extends Record<States, Partial<Record<string, States>>>
> = {
  states: States;
  transitions: Transitions;
};

// Traffic light example
type TrafficStates = 'red' | 'yellow' | 'green';
type TrafficTransitions = {
  red: { timer: 'green' };
  green: { timer: 'yellow' };
  yellow: { timer: 'red' };
};

class Machine<
  States extends string,
  Trans extends Record<States, Partial<Record<string, States>>>
> {
  constructor(
    private current: States,
    private transitions: Trans
  ) {}

  send<E extends keyof Trans[States] & string>(
    event: E
  ): Trans[States][E] extends States ? Machine<States, Trans> : never {
    const nextState = this.transitions[this.current][event] as States;
    if (!nextState) throw new Error(`Invalid transition: ${this.current} + ${event}`);
    return new Machine(nextState, this.transitions) as any;
  }

  getState(): States {
    return this.current;
  }
}

// Usage
const traffic = new Machine<TrafficStates, TrafficTransitions>('red', {
  red: { timer: 'green' },
  green: { timer: 'yellow' },
  yellow: { timer: 'red' },
});

const next = traffic.send('timer'); // Valid: red -> green
// traffic.send('invalid'); // ERROR at type level
```
