# CLI Distribution & Packaging

## npm bin Field

```json
// package.json
{
  "name": "my-cli",
  "version": "1.0.0",
  "bin": {
    "mycli": "./dist/index.js"
  },
  "files": ["dist"],
  "type": "module",
  "engines": {
    "node": ">=18"
  }
}
```

## Shebang Line

The first line of your entry file must be:

```ts
#!/usr/bin/env node
// rest of your code...
```

After build, ensure the output file has the shebang and is executable:

```bash
# tsup preserves shebangs automatically
# For other bundlers, verify:
head -1 dist/index.js  # should show #!/usr/bin/env node
chmod +x dist/index.js  # ensure executable
```

## Build Configuration

### tsup (Recommended)

```ts
// tsup.config.ts
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm"],
  target: "node18",
  clean: true,
  dts: true,
  splitting: false,
  banner: {
    js: "#!/usr/bin/env node",
  },
});
```

### package.json Scripts

```json
{
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "prepublishOnly": "npm run build",
    "postbuild": "chmod +x dist/index.js"
  }
}
```

## Cross-Platform Compatibility

### File Paths

```ts
import { join } from "node:path";
import { homedir, platform } from "node:os";

// NEVER hardcode path separators
const configDir = join(homedir(), ".mycli");

// Platform-specific config locations
function getConfigDir(): string {
  switch (platform()) {
    case "win32":
      return join(process.env.APPDATA || homedir(), "mycli");
    case "darwin":
      return join(homedir(), "Library", "Application Support", "mycli");
    default:
      return join(process.env.XDG_CONFIG_HOME || join(homedir(), ".config"), "mycli");
  }
}
```

### Spawning Processes

```ts
import { execSync } from "node:child_process";
import { platform } from "node:os";

// Use cross-spawn for cross-platform child processes
import spawn from "cross-spawn";

const result = spawn.sync("npm", ["install"], {
  stdio: "inherit",
  shell: platform() === "win32", // needed on Windows
});
```

### Line Endings

```ts
import { EOL } from "node:os";

// Use os.EOL for platform-correct line endings
const output = lines.join(EOL);
```

## Compile to Binary

### Bun Compile

```bash
bun build ./src/index.ts --compile --outfile mycli
# Produces a standalone binary, no Node.js required
```

### pkg (deprecated but still used)

```bash
npx pkg dist/index.js --targets node18-linux-x64,node18-macos-x64,node18-win-x64
```

### Node.js Single Executable (SEA)

```bash
# Node.js 20+
echo '{"main":"dist/index.js","output":"sea-prep.blob"}' > sea-config.json
node --experimental-sea-config sea-config.json
cp $(which node) mycli
npx postject mycli NODE_SEA_BLOB sea-prep.blob --sentinel-fuse NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2
```

## Auto-Update

### update-notifier

```ts
import updateNotifier from "update-notifier";
import pkg from "../package.json" with { type: "json" };

// Check once per day, non-blocking
const notifier = updateNotifier({
  pkg,
  updateCheckInterval: 1000 * 60 * 60 * 24, // 1 day
});

// Show notification if update available
notifier.notify({
  isGlobal: true,
  message: "Update available: {currentVersion} -> {latestVersion}\nRun `npm i -g {packageName}` to update",
});
```

## Publishing Checklist

```bash
# 1. Ensure clean build
npm run build

# 2. Test the CLI locally
npm link
mycli --version
mycli --help
npm unlink

# 3. Verify package contents
npm pack --dry-run

# 4. Publish
npm publish

# 5. Verify installation
npx my-cli@latest --version
```

## Versioning

```bash
# Bump version (updates package.json, creates git tag)
npm version patch   # 1.0.0 -> 1.0.1
npm version minor   # 1.0.0 -> 1.1.0
npm version major   # 1.0.0 -> 2.0.0

# With changelog (using conventional commits)
npx standard-version
```

## Man Pages

```json
// package.json
{
  "man": ["./man/mycli.1"]
}
```

```roff
.\" man/mycli.1
.TH MYCLI 1 "2025-01-01" "1.0.0" "My CLI Manual"
.SH NAME
mycli \- description of the tool
.SH SYNOPSIS
.B mycli
[\fIcommand\fR]
[\fIoptions\fR]
.SH DESCRIPTION
Detailed description of what the tool does.
.SH COMMANDS
.TP
.B init
Initialize a new project
.TP
.B build
Build the project
.SH OPTIONS
.TP
.B \-h, \-\-help
Show help
.TP
.B \-v, \-\-version
Show version
.SH EXAMPLES
.TP
Initialize a project:
.B mycli init my-project
.SH AUTHOR
Your Name <you@example.com>
```

## GitHub Releases with Binaries

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]
jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: linux-x64
          - os: macos-latest
            target: darwin-x64
          - os: macos-latest
            target: darwin-arm64
          - os: windows-latest
            target: win-x64
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun build src/index.ts --compile --outfile mycli-${{ matrix.target }}
      - uses: softprops/action-gh-release@v1
        with:
          files: mycli-${{ matrix.target }}*
```
