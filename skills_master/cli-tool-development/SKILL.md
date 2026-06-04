---
name: cli-tool-development
description: CLI tool development with argument parsing, interactive UIs (@clack), output formatting, config management (cosmiconfig), packaging, and distribution.
version: 2.0.0
reviewed: "2026-06-04"
---
# CLI Tool Development

## Project Setup

```bash
mkdir my-cli && cd my-cli
npm init -y
npm install commander chalk ora cli-table3 cosmiconfig
npm install -D typescript @types/node tsup
```

```json
// package.json
{
  "name": "my-cli",
  "version": "1.0.0",
  "bin": {
    "mycli": "./dist/index.js"
  },
  "type": "module",
  "files": ["dist"],
  "scripts": {
    "build": "tsup src/index.ts --format esm --dts",
    "dev": "tsup src/index.ts --format esm --watch"
  }
}
```

```ts
// src/index.ts
#!/usr/bin/env node
import { program } from "commander";
import { version } from "../package.json" with { type: "json" };

program
  .name("mycli")
  .description("My awesome CLI tool")
  .version(version);

// Register commands
program
  .command("init")
  .description("Initialize a new project")
  .option("-t, --template <name>", "template to use", "default")
  .option("--no-git", "skip git initialization")
  .action(async (options) => {
    const { init } = await import("./commands/init.js");
    await init(options);
  });

program
  .command("build")
  .description("Build the project")
  .option("-w, --watch", "watch for changes")
  .option("-o, --outdir <dir>", "output directory", "dist")
  .action(async (options) => {
    const { build } = await import("./commands/build.js");
    await build(options);
  });

program.parse();
```

## Argument Parsing Comparison

| Feature | Commander.js | yargs | citty | `node:util` parseArgs |
|---------|-------------|-------|-------|----------------------|
| **Size** | ~50KB | ~200KB | ~12KB | 0 (built-in) |
| **TypeScript** | Built-in types | @types/yargs | Built-in | Built-in (Node 18+) |
| **Subcommands** | Yes | Yes | Yes | No |
| **Auto help** | Yes | Yes | Yes | No |
| **Validation** | Basic | Rich (choices, coerce) | Zod-compatible | No |
| **Async actions** | Yes | Yes | Yes | N/A |
| **Interactive** | No (use @clack) | No | No | No |
| **Best for** | Most CLIs | Complex CLIs | Lightweight/Bun | Minimal scripts |

```ts
// citty — lightweight alternative (works great with Bun)
import { defineCommand, runMain } from "citty";


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.