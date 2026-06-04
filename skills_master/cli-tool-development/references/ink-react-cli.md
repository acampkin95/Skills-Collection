# Ink: React for Terminal UIs

## Setup

```bash
npm install ink react
npm install -D @types/react
```

```json
// tsconfig.json (key settings)
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "moduleResolution": "node16",
    "module": "node16"
  }
}
```

## Basic App

```tsx
#!/usr/bin/env node
// src/index.tsx
import React from "react";
import { render, Box, Text } from "ink";
import { parseArgs } from "node:util";

const { values } = parseArgs({
  options: {
    name: { type: "string", short: "n", default: "World" },
  },
});

function App({ name }: { name: string }) {
  return (
    <Box flexDirection="column" padding={1}>
      <Text bold color="green">
        Hello, {name}!
      </Text>
      <Text dimColor>Welcome to Ink</Text>
    </Box>
  );
}

render(<App name={values.name!} />);
```

## Core Components

### Box (Layout)

```tsx
// Flexbox layout — same mental model as CSS flexbox
<Box flexDirection="column" gap={1}>
  <Box>
    <Text>Left</Text>
    <Box flexGrow={1} />
    <Text>Right</Text>
  </Box>

  <Box borderStyle="round" borderColor="cyan" padding={1}>
    <Text>Bordered content</Text>
  </Box>

  <Box width={40} justifyContent="center">
    <Text>Centered in 40-char box</Text>
  </Box>
</Box>
```

### Text (Styled Output)

```tsx
<Text bold>Bold text</Text>
<Text italic>Italic text</Text>
<Text underline>Underlined</Text>
<Text strikethrough>Struck through</Text>
<Text color="green">Green text</Text>
<Text color="#ff6347">Hex color</Text>
<Text backgroundColor="blue" color="white"> Highlighted </Text>
<Text dimColor>Dimmed text</Text>
<Text inverse> Inverted </Text>
```

### Spinner

```tsx
import { Text } from "ink";
import Spinner from "ink-spinner";

function Loading() {
  return (
    <Text>
      <Text color="green"><Spinner type="dots" /></Text>
      {" Loading..."}
    </Text>
  );
}
```

## Hooks

### useInput

```tsx
import { useInput, useApp, Box, Text } from "ink";
import React, { useState } from "react";

function NavigableList({ items }: { items: string[] }) {
  const [cursor, setCursor] = useState(0);
  const { exit } = useApp();

  useInput((input, key) => {
    if (key.upArrow) {
      setCursor((c) => Math.max(0, c - 1));
    }
    if (key.downArrow) {
      setCursor((c) => Math.min(items.length - 1, c + 1));
    }
    if (key.return) {
      console.log(`Selected: ${items[cursor]}`);
      exit();
    }
    if (input === "q") {
      exit();
    }
  });

  return (
    <Box flexDirection="column">
      {items.map((item, i) => (
        <Text key={item} color={i === cursor ? "cyan" : undefined}>
          {i === cursor ? ">" : " "} {item}
        </Text>
      ))}
      <Text dimColor>Use arrows to navigate, Enter to select, q to quit</Text>
    </Box>
  );
}
```

### useStdin for Raw Input

```tsx
import { useStdin } from "ink";

function RawInput() {
  const { stdin, setRawMode, isRawModeSupported } = useStdin();

  React.useEffect(() => {
    if (!isRawModeSupported) return;
    setRawMode(true);
    return () => setRawMode(false);
  }, [setRawMode, isRawModeSupported]);

  // Process raw character-by-character input from stdin
  React.useEffect(() => {
    if (!stdin) return;
    const handler = (data: Buffer) => {
      const char = data.toString();
      // Handle each character
    };
    stdin.on("data", handler);
    return () => { stdin.off("data", handler); };
  }, [stdin]);
}
```

### useFocus and useFocusManager (Ink v5)

```tsx
import { useFocus, useFocusManager, Box, Text } from "ink";

function FocusableInput({ label }: { label: string }) {
  const { isFocused } = useFocus();
  return (
    <Box>
      <Text color={isFocused ? "cyan" : "gray"}>
        {isFocused ? ">" : " "} {label}
      </Text>
    </Box>
  );
}

function FocusManager() {
  const { focusNext, focusPrevious } = useFocusManager();

  useInput((_input, key) => {
    if (key.tab) {
      if (key.shift) focusPrevious();
      else focusNext();
    }
  });

  return (
    <Box flexDirection="column">
      <FocusableInput label="Name" />
      <FocusableInput label="Email" />
      <FocusableInput label="Password" />
    </Box>
  );
}
```

## Suspense in CLI (Ink v5)

```tsx
import React, { Suspense } from "react";
import { render, Box, Text } from "ink";
import Spinner from "ink-spinner";

// Async data component using React Suspense
function AsyncData({ resource }: { resource: Resource<string[]> }) {
  const data = resource.read(); // Suspends until ready
  return (
    <Box flexDirection="column">
      {data.map((item) => (
        <Text key={item}>- {item}</Text>
      ))}
    </Box>
  );
}

// Simple Suspense resource wrapper
function createResource<T>(promise: Promise<T>): Resource<T> {
  let status = "pending";
  let result: T;
  let error: Error;
  const suspender = promise.then(
    (r) => { status = "success"; result = r; },
    (e) => { status = "error"; error = e; },
  );
  return {
    read() {
      if (status === "pending") throw suspender;
      if (status === "error") throw error;
      return result;
    },
  };
}

interface Resource<T> { read(): T; }

// Usage
const dataResource = createResource(fetchItems());

function App() {
  return (
    <Box flexDirection="column" padding={1}>
      <Text bold>Items:</Text>
      <Suspense fallback={<Text><Spinner type="dots" /> Loading...</Text>}>
        <AsyncData resource={dataResource} />
      </Suspense>
    </Box>
  );
}

render(<App />);
```

## Full-Screen App with useStdout (Ink v5)

```tsx
import React, { useState, useEffect } from "react";
import { render, Box, Text, useInput, useApp, useStdout } from "ink";

function FullScreenApp() {
  const { stdout } = useStdout();
  const [rows, setRows] = useState(stdout?.rows ?? 24);
  const [cols, setCols] = useState(stdout?.columns ?? 80);
  const { exit } = useApp();

  useEffect(() => {
    const onResize = () => {
      if (stdout) {
        setRows(stdout.rows);
        setCols(stdout.columns);
      }
    };
    stdout?.on("resize", onResize);
    return () => { stdout?.off("resize", onResize); };
  }, [stdout]);

  useInput((input) => {
    if (input === "q") exit();
  });

  return (
    <Box flexDirection="column" height={rows} width={cols}>
      {/* Header */}
      <Box borderStyle="single" paddingX={1}>
        <Text bold color="cyan">Full Screen App</Text>
        <Box flexGrow={1} />
        <Text dimColor>{cols}x{rows}</Text>
      </Box>

      {/* Main content area fills remaining space */}
      <Box flexGrow={1} padding={1}>
        <Text>Content area ({cols - 4} x {rows - 4} usable)</Text>
      </Box>

      {/* Footer */}
      <Box borderStyle="single" paddingX={1}>
        <Text dimColor>Press q to quit</Text>
      </Box>
    </Box>
  );
}

render(<FullScreenApp />);
```

## Full-Screen TUI Layout

```tsx
import React, { useState } from "react";
import { Box, Text, useInput, useApp } from "ink";

function Dashboard() {
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ["Overview", "Logs", "Settings"];
  const { exit } = useApp();

  useInput((input, key) => {
    if (key.tab) setActiveTab((t) => (t + 1) % tabs.length);
    if (input === "q") exit();
  });

  return (
    <Box flexDirection="column" width="100%">
      {/* Header */}
      <Box borderStyle="single" borderBottom paddingX={1}>
        <Text bold color="cyan">My CLI Dashboard</Text>
        <Box flexGrow={1} />
        <Text dimColor>Press Tab to switch, q to quit</Text>
      </Box>

      {/* Tab Bar */}
      <Box gap={2} paddingX={1}>
        {tabs.map((tab, i) => (
          <Text
            key={tab}
            bold={i === activeTab}
            color={i === activeTab ? "cyan" : "gray"}
            underline={i === activeTab}
          >
            {tab}
          </Text>
        ))}
      </Box>

      {/* Content */}
      <Box flexGrow={1} padding={1} flexDirection="column">
        {activeTab === 0 && <OverviewPanel />}
        {activeTab === 1 && <LogsPanel />}
        {activeTab === 2 && <SettingsPanel />}
      </Box>

      {/* Status Bar */}
      <Box borderStyle="single" borderTop paddingX={1}>
        <Text color="green">Ready</Text>
        <Box flexGrow={1} />
        <Text dimColor>{new Date().toLocaleTimeString()}</Text>
      </Box>
    </Box>
  );
}

function OverviewPanel() {
  return (
    <Box flexDirection="column" gap={1}>
      <Text bold>System Status</Text>
      <Box gap={2}>
        <Text>CPU: <Text color="green">12%</Text></Text>
        <Text>Memory: <Text color="yellow">67%</Text></Text>
        <Text>Disk: <Text color="green">45%</Text></Text>
      </Box>
    </Box>
  );
}

function LogsPanel() {
  return <Text dimColor>No recent logs</Text>;
}

function SettingsPanel() {
  return <Text>Settings panel content</Text>;
}
```

## Forms in Terminal

```tsx
import React, { useState } from "react";
import { Box, Text, useInput, useApp } from "ink";
import TextInput from "ink-text-input";

function Form() {
  const [step, setStep] = useState(0);
  const [values, setValues] = useState({ name: "", email: "" });
  const { exit } = useApp();

  const fields = [
    { key: "name" as const, label: "Name", placeholder: "John Doe" },
    { key: "email" as const, label: "Email", placeholder: "john@example.com" },
  ];

  const current = fields[step];

  const handleSubmit = (value: string) => {
    setValues((v) => ({ ...v, [current.key]: value }));
    if (step < fields.length - 1) {
      setStep((s) => s + 1);
    } else {
      console.log("Submitted:", { ...values, [current.key]: value });
      exit();
    }
  };

  return (
    <Box flexDirection="column" gap={1}>
      <Text bold>Setup Wizard ({step + 1}/{fields.length})</Text>

      {fields.map((field, i) => (
        <Box key={field.key} gap={1}>
          <Text color={i === step ? "cyan" : "gray"}>
            {i < step ? "v" : i === step ? ">" : " "}
          </Text>
          <Text color={i <= step ? "white" : "gray"}>{field.label}:</Text>
          {i < step && <Text color="green">{values[field.key]}</Text>}
          {i === step && (
            <TextInput
              placeholder={field.placeholder}
              onSubmit={handleSubmit}
            />
          )}
        </Box>
      ))}
    </Box>
  );
}
```

## Useful Ink Packages

| Package | Purpose |
|---------|---------|
| `ink-text-input` | Text input field |
| `ink-select-input` | Select list |
| `ink-spinner` | Loading spinners |
| `ink-table` | Table output |
| `ink-progress-bar` | Progress bars |
| `ink-big-text` | Large ASCII text |
| `ink-gradient` | Gradient colored text |
| `ink-link` | Clickable terminal links |
