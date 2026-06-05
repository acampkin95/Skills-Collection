---
name: cli-tool-development
description: Use this skill when CLI tool, command line, commander.
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

const main = defineCommand({
  meta: { name: "mycli", version: "1.1.0", description: "My CLI" },
  args: {
    name: { type: "positional", description: "Project name", required: true },
    template: { type: "string", alias: "t", default: "default" },
    force: { type: "boolean", alias: "f", default: false },
  },
  run({ args }) {
    console.log(`Creating ${args.name} with template ${args.template}`);
  },
});

runMain(main);
```

## Commander.js Patterns

### Commands with Arguments

```ts
program
  .command("add <name>")
  .description("Add a new component")
  .argument("[path]", "destination path", "./src/components")
  .option("-f, --force", "overwrite existing files")
  .option("--dry-run", "preview without writing")
  .action(async (name: string, path: string, options) => {
    console.log(`Adding ${name} to ${path}`);
    if (options.dryRun) {
      console.log("(dry run - no files written)");
    }
  });
```

### Subcommands

```ts
const config = program
  .command("config")
  .description("Manage configuration");

config
  .command("set <key> <value>")
  .description("Set a config value")
  .action((key, value) => { /* ... */ });

config
  .command("get <key>")
  .description("Get a config value")
  .action((key) => { /* ... */ });

config
  .command("list")
  .description("List all config values")
  .action(() => { /* ... */ });
```

## Interactive Prompts

### Using @clack/prompts

```ts
import * as p from "@clack/prompts";
import color from "picocolors";

export async function initCommand() {
  p.intro(color.bgCyan(color.black(" project-init ")));

  const project = await p.group(
    {
      name: () =>
        p.text({
          message: "Project name?",
          placeholder: "my-app",
          validate: (v) => {
            if (!v) return "Name is required";
            if (!/^[a-z0-9-]+$/.test(v)) return "Lowercase letters, numbers, hyphens only";
          },
        }),
      framework: () =>
        p.select({
          message: "Pick a framework",
          options: [
            { value: "next", label: "Next.js", hint: "recommended" },
            { value: "remix", label: "Remix" },
            { value: "astro", label: "Astro", hint: "for content sites" },
          ],
        }),
      features: () =>
        p.multiselect({
          message: "Select features",
          options: [
            { value: "typescript", label: "TypeScript", hint: "recommended" },
            { value: "eslint", label: "ESLint" },
            { value: "tailwind", label: "Tailwind CSS" },
          ],
          required: false,
        }),
      install: () =>
        p.confirm({
          message: "Install dependencies?",
          initialValue: true,
        }),
    },
    {
      onCancel: () => {
        p.cancel("Setup cancelled.");
        process.exit(0);
      },
    }
  );

  const s = p.spinner();
  s.start("Creating project...");
  // ... do work
  s.stop("Project created!");

  p.outro(`Done! Run ${color.cyan(`cd ${project.name}`)} to get started.`);
}
```

## Output Formatting

**For patterns, see `references/distribution.md`** — includes:
- Chalk vs picocolors comparison and usage
- Ora spinner states and configuration
- cli-table3 examples for tabular output
- JSON output mode patterns
- Progress bars and animations
  .action(async (options) => {
    const items = await getItems();
    output(items, options.json);
  });
```

### Progress Bars

```ts
import cliProgress from "cli-progress";

const bar = new cliProgress.SingleBar({
  format: "{bar} {percentage}% | {value}/{total} files",
  barCompleteChar: "\u2588",
  barIncompleteChar: "\u2591",
});

bar.start(files.length, 0);
for (const file of files) {
  await processFile(file);
  bar.increment();
}
bar.stop();
```

## Config File Management

### Cosmiconfig with Zod Validation

```ts
import { cosmiconfig } from "cosmiconfig";
import { z } from "zod";

const configSchema = z.object({
  outDir: z.string().default("dist"),
  port: z.number().default(3000),
  plugins: z.array(z.string()).default([]),
});

export type Config = z.infer<typeof configSchema>;

export async function loadConfig(): Promise<Config> {
  const explorer = cosmiconfig("mycli", {
    searchPlaces: [
      "mycli.config.ts",
      "mycli.config.js",
      "mycli.config.json",
      ".myclirc",
      "package.json",
    ],
  });

  const result = await explorer.search();

  if (!result || result.isEmpty) {
    return configSchema.parse({});
  }

  const parsed = configSchema.safeParse(result.config);
  if (!parsed.success) {
    console.error("Invalid config:", parsed.error.format());
    process.exit(1);
  }

  return parsed.data;
}
```

### XDG Base Directory

```ts
import { homedir } from "node:os";
import { join } from "node:path";

// XDG-compliant config/data/cache paths
function getXDGPaths(appName: string) {
  const home = homedir();
  return {
    config: join(process.env.XDG_CONFIG_HOME || join(home, ".config"), appName),
    data: join(process.env.XDG_DATA_HOME || join(home, ".local", "share"), appName),
    cache: join(process.env.XDG_CACHE_HOME || join(home, ".cache"), appName),
  };
}

// Usage: const paths = getXDGPaths("mycli");
// paths.config → ~/.config/mycli/
// paths.data   → ~/.local/share/mycli/
// paths.cache  → ~/.cache/mycli/
```

## Error Handling

```ts
// lib/errors.ts
export class CLIError extends Error {
  constructor(
    message: string,
    public exitCode: number = 1,
    public hint?: string
  ) {
    super(message);
    this.name = "CLIError";
  }
}

// Wrap command actions
function withErrorHandler(fn: (...args: any[]) => Promise<void>) {
  return async (...args: any[]) => {
    try {
      await fn(...args);
    } catch (error) {
      if (error instanceof CLIError) {
        console.error(chalk.red("Error:"), error.message);
        if (error.hint) {
          console.error(chalk.dim(`Hint: ${error.hint}`));
        }
        process.exit(error.exitCode);
      }
      // Unexpected error
      console.error(chalk.red("Unexpected error:"), error);
      console.error(chalk.dim("Please report this at https://github.com/..."));
      process.exit(1);
    }
  };
}

// Usage
program
  .command("deploy")
  .action(withErrorHandler(async () => {
    const config = await loadConfig();
    if (!config.outDir) {
      throw new CLIError("No output directory configured", 1, "Set outDir in mycli.config.ts");
    }
    // ...
  }));
```

### Process Signal Handling

```ts
// Handle SIGINT (Ctrl+C)
process.on("SIGINT", () => {
  console.log("\n" + chalk.yellow("Interrupted. Cleaning up..."));
  cleanup();
  process.exit(130); // 128 + signal number (2)
});

// Handle SIGTERM
process.on("SIGTERM", () => {
  cleanup();
  process.exit(143); // 128 + signal number (15)
});

// Handle uncaught exceptions
process.on("uncaughtException", (error) => {
  console.error(chalk.red("Fatal:"), error.message);
  process.exit(1);
});

// Handle unhandled rejections
process.on("unhandledRejection", (reason) => {
  console.error(chalk.red("Unhandled rejection:"), reason);
  process.exit(1);
});

function cleanup() {
  // Remove temp files, close connections, restore terminal state
}
```

### Exit Codes Convention

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Misuse of command (bad args) |
| `126` | Command not executable |
| `127` | Command not found |
| `130` | Interrupted (SIGINT / Ctrl+C) |
| `143` | Terminated (SIGTERM) |

## Testing CLI Tools

```ts
// test/cli.test.ts — using execa
import { execa } from "execa";
import { describe, it, expect } from "vitest";

describe("mycli", () => {
  it("shows help", async () => {
    const { stdout } = await execa("node", ["./dist/index.js", "--help"]);
    expect(stdout).toContain("My awesome CLI tool");
  });

  it("shows version", async () => {
    const { stdout } = await execa("node", ["./dist/index.js", "--version"]);
    expect(stdout).toMatch(/\d+\.\d+\.\d+/);
  });

  it("exits with code 1 on unknown command", async () => {
    const result = await execa("node", ["./dist/index.js", "badcmd"], {
      reject: false,
    });
    expect(result.exitCode).toBe(1);
    expect(result.stderr).toContain("unknown command");
  });

  it("generates output correctly", async () => {
    const { stdout } = await execa("node", ["./dist/index.js", "list", "--json"]);
    const parsed = JSON.parse(stdout);
    expect(parsed).toBeInstanceOf(Array);
  });
});

// Snapshot testing CLI output
it("matches expected output", async () => {
  const { stdout } = await execa("node", ["./dist/index.js", "list"]);
  expect(stdout).toMatchSnapshot();
});
```

For Ink (React-based terminal UI), see [references/ink-react-cli.md](references/ink-react-cli.md).

For distribution and packaging, see [references/distribution.md](references/distribution.md).
