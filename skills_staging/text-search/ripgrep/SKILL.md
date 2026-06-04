---

## Parent router

This skill is a leaf of the [text-search](../text-search/SKILL.md) master router.
name: ripgrep
description: Fastest recursive text search tool for files and codebases using ripgrep (rg). Use when ripgrep, rg, recursive grep, fast text search, file-type filter, .gitignore aware, JSON output, search codebase.
---

# Ripgrep — Comprehensive Search Skill

ripgrep (`rg`) is the fastest general-purpose recursive search tool. It respects `.gitignore` by default, searches recursively, supports full regex, and handles Unicode correctly. It should be the default choice for any file content search.

## Core Mental Model

ripgrep works in layers of filtering:

1. **File discovery** — which files to search (gitignore, hidden files, file types, globs)
2. **Pattern matching** — what to find (regex, literal, case sensitivity)
3. **Output shaping** — how to present results (context, format, grouping)

Understanding these layers helps you compose the right flags for any search task.

---

## Essential Patterns

### Basic Search

```bash
# Search current directory recursively
rg 'pattern'

# Search specific path
rg 'pattern' src/

# Search specific file
rg 'pattern' path/to/file.ts

# Literal string (no regex interpretation)
rg -F 'exact.string()'

# Case insensitive
rg -i 'pattern'

# Smart case (case-insensitive if all lowercase, sensitive if any uppercase)
rg -S 'pattern'
```

### File Type Filtering

ripgrep has built-in type definitions — use them instead of glob patterns when possible. They're faster and cover edge cases (e.g. `--type ts` matches `.ts` and `.tsx`).

```bash
# Search only TypeScript files
rg -t ts 'pattern'

# Search only Python files
rg -t py 'pattern'

# Exclude a file type
rg -T css 'pattern'

# Multiple types
rg -t ts -t js 'pattern'

# List all known types
rg --type-list

# Define a custom type inline
rg --type-add 'config:*.{json,yaml,yml,toml}' -t config 'pattern'
```

### Glob Filtering

For fine-grained file selection beyond built-in types:

```bash
# Only search .env files
rg -g '*.env' 'API_KEY'

# Search specific directory pattern
rg -g 'src/components/**/*.tsx' 'useState'

# Exclude patterns (prefix with !)
rg -g '!*.min.js' -g '!node_modules' 'function'

# Combine type and glob
rg -t ts -g '!*.test.ts' 'export default'
```

### Context Lines

```bash
# Lines after match
rg -A 3 'pattern'

# Lines before match
rg -B 2 'pattern'

# Lines before and after (context)
rg -C 5 'pattern'
```

### Output Modes

```bash
# Only filenames (files with matches)
rg -l 'pattern'

# Only filenames (files without matches)
rg --files-without-match 'pattern'

# Count matches per file
rg -c 'pattern'

# Only the matched text (not whole line)
rg -o 'pattern'

# Show line numbers (default in terminal, explicit for scripts)
rg -n 'pattern'

# No line numbers
rg --no-line-number 'pattern'

# No filename prefix
rg --no-filename 'pattern'

# Vimgrep format (file:line:col:match) — useful for editor integration
rg --vimgrep 'pattern'
```

---

## Regex Patterns

ripgrep uses Rust's regex engine by default — fast, Unicode-aware, but no lookaround or backreferences. For those, use `--engine pcre2` (if compiled with PCRE2 support).

### Common Regex Recipes

```bash
# Word boundary — match whole words only
rg -w 'TODO'
# Equivalent to: rg '\bTODO\b'

# Match whole line
rg -x 'exactly this line'

# Alternation
rg 'error|warning|fatal'

# Character classes
rg '[A-Z]{2,4}-\d+' # Match issue IDs like AB-123, PROJ-4567

# Capture groups (useful with --replace)
rg '(\w+)@(\w+)\.com'

# Non-greedy
rg 'href=".*?"'

# Named groups
rg '(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'

# Unicode property classes
rg '\p{Emoji}'
rg '\p{Greek}'
```

### Multiline Matching

```bash
# Enable multiline mode (. matches newline)
rg -U 'struct \{[^}]*\}'

# Multiline with dotall (. matches \n)
rg -U --multiline-dotall 'BEGIN.*?END'

# Match across lines — e.g. function with its body
rg -U 'function \w+\([^)]*\)\s*\{[^}]*\}'
```

### PCRE2 (Advanced Regex)

When available, PCRE2 unlocks lookaround and backreferences:

```bash
# Lookahead — lines containing 'error' but not 'timeout'
rg -P 'error(?!.*timeout)'

# Lookbehind — values after 'price: '
rg -P '(?<=price:\s)\d+\.\d{2}'

# Backreference — repeated words
rg -P '\b(\w+)\s+\1\b'
```

Check PCRE2 availability: `rg --pcre2-version`. If unavailable, restructure the search or pipe through `grep -P`.

---

## Search-and-Replace

ripgrep doesn't modify files, but `--replace` (-r) transforms output, which you can pipe to create replacements:

```bash
# Preview replacement
rg 'oldFunction' --replace 'newFunction'

# With capture groups
rg '(\w+)\.forEach\(' --replace '$1.map('

# Named captures
rg '(?P<name>\w+)Error' --replace '${name}Exception'

# For actual file modification, pipe through sed or use sd:
rg -l 'oldPattern' | xargs sed -i 's/oldPattern/newPattern/g'

# Or with sd (simpler syntax, respects rg output):
rg -l 'oldPattern' | xargs sd 'oldPattern' 'newPattern'
```

---

## Ignoring and Including Files

### Understanding the Ignore Hierarchy

ripgrep checks these in order (first match wins):

1. `--glob` / `-g` flags (highest priority)
2. `.rgignore` (ripgrep-specific)
3. `.gitignore` (if in a git repo)
4. `.ignore` (universal ignore)
5. Global gitignore (`core.excludesFile`)

### Unrestricted Modes

```bash
# -u: don't respect .gitignore
rg -u 'pattern'

# -uu: also search hidden files/directories
rg -uu 'pattern'

# -uuu: also search binary files (equivalent to grep -r)
rg -uuu 'pattern'
```

### Searching Hidden and Ignored Files

```bash
# Include hidden files (dotfiles)
rg --hidden 'pattern'

# Skip gitignore rules
rg --no-ignore 'pattern'

# Both (search everything except binary)
rg --hidden --no-ignore 'pattern'

# Follow symlinks
rg -L 'pattern'
```

---

## Performance Techniques

### When Speed Matters

ripgrep is already fast, but for very large searches:

```bash
# Fixed string (skip regex compilation)
rg -F 'exact string'

# Limit thread count (useful on constrained systems)
rg -j 4 'pattern'

# Limit search depth
rg --max-depth 2 'pattern'

# Limit file size (skip huge files)
rg --max-filesize 1M 'pattern'

# Memory-map files (can be faster for large files)
rg --mmap 'pattern'

# Statistics (benchmark your search)
rg --stats 'pattern'
```

### Sorting Results

Sorting forces single-threaded execution — only use when output order matters:

```bash
rg --sort path 'pattern'
rg --sort modified 'pattern'
rg --sortr modified 'pattern' # Reverse (newest first)
```

---

## Composing with Other Tools

### Piping and Chaining

```bash
# Search within search results (progressive filtering)
rg 'error' logs/ | rg 'database'

# Feed filenames to another command
rg -l 'TODO' | xargs wc -l

# Use as input filter
cat large_log.txt | rg 'ERROR' | rg -v 'known_issue'

# JSON output for programmatic use
rg --json 'pattern' | jq '.data.lines.text'

# Search compressed files
rg -z 'pattern' archive.gz
```

### Common Workflows

```bash
# Find all files rg would search (without searching)
rg --files

# Find files matching a type
rg --files -t py

# Find files matching glob
rg --files -g '*.config.*'

# Count total matches across all files
rg -c 'pattern' | awk -F: '{sum+=$NF} END {print sum}'

# Find and open in editor
rg -l 'pattern' | xargs code
# Or with vim:
vim $(rg -l 'pattern')

# Unique matched values
rg -o -N --no-filename 'version:\s*"([^"]+)"' -r '$1' | sort -u
```

---

## Configuration

### Config File

ripgrep reads `$RIPGREP_CONFIG_PATH` if set. Create a config file for persistent defaults:

```bash
# ~/.ripgreprc
--smart-case
--hidden
--glob=!.git
--glob=!node_modules
--glob=!.next
--glob=!dist
--glob=!build
--max-columns=200
--max-columns-preview
```

Then: `export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"`

### Type Definitions

Custom types persist via config:

```
# In ~/.ripgreprc
--type-add=web:*.{html,css,js,ts,tsx,jsx,vue,svelte}
--type-add=config:*.{json,yaml,yml,toml,ini,env}
--type-add=docs:*.{md,mdx,rst,txt,adoc}
```

---

## Codebase Search Recipes

For detailed recipes covering specific languages and frameworks, see `references/recipes.md`. Key patterns:

```bash
# Find function/class definitions
rg 'function\s+\w+|class\s+\w+|const\s+\w+\s*=' -t ts
rg 'def \w+|class \w+' -t py

# Find imports of a module
rg "from ['\"].*module-name" -t ts
rg 'from\s+\w+\s+import' -t py

# Find TODO/FIXME/HACK comments
rg 'TODO|FIXME|HACK|XXX|WARN' --trim

# Find exported functions/components
rg 'export (default |)(function|const|class) \w+' -t ts

# Find unused exports (files that export but are never imported)
# Step 1: find all exported names
rg -o 'export (?:default )?(?:function|const|class|interface|type) (\w+)' -r '$1' -t ts --no-filename | sort -u > /tmp/exports.txt
# Step 2: check which are imported
while read name; do
  count=$(rg -c "import.*$name|from.*$name" -t ts 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  [ "$count" -eq 0 ] && echo "Potentially unused: $name"
done < /tmp/exports.txt

# Find environment variable usage
rg 'process\.env\.\w+|import\.meta\.env\.\w+' -o --no-filename | sort -u

# Find hardcoded URLs
rg 'https?://[^\s"'"'"'`>)]+' -o --no-filename | sort -u

# Find large React components (files with many hooks)
rg -c 'use[A-Z]\w+\(' -t tsx --sort path | awk -F: '$NF > 5'

# Find API route handlers (Next.js)
rg 'export (async )?function (GET|POST|PUT|DELETE|PATCH)' -t ts src/app/

# Git-aware: search only staged files
git diff --cached --name-only | xargs rg 'console\.log'

# Search specific git revision
git show HEAD:src/file.ts | rg 'pattern'
```

---

## Log Analysis Recipes

```bash
# Filter log level
rg '^\[ERROR\]|^\[FATAL\]' app.log

# Extract timestamps from errors
rg -o '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' -B0 error.log

# Find slow requests (>1000ms)
rg 'duration[=:]\s*(\d{4,})' --replace 'slow: $1ms'

# Count errors per hour
rg -o '\d{4}-\d{2}-\d{2}T\d{2}' error.log | sort | uniq -c | sort -rn

# Find stack traces (multiline)
rg -U 'Error:.*\n(\s+at .+\n)+' app.log

# Tail + filter (live log watching)
tail -f app.log | rg --line-buffered 'ERROR|WARN'
```

---

## Gotchas and Tips

1. **Escaping in shells**: Single-quote patterns to avoid shell expansion. Use `-e` for patterns starting with `-`.

2. **Braces need escaping**: ripgrep uses Rust regex, not glob syntax in patterns. To match literal `{`, use `\{`. But in `--glob`, braces work as expected: `-g '*.{ts,tsx}'`.

3. **No lookaround by default**: Use `-P` (PCRE2) for lookahead/lookbehind. Check availability with `rg --pcre2-version`.

4. **Binary files skipped silently**: If results seem incomplete, try `-a` (text mode) or check with `rg --debug`.

5. **Line-buffered for pipes**: When piping rg output through other commands in real-time, add `--line-buffered`.

6. **Max columns**: Long lines get truncated in terminal output. Use `--max-columns 0` to disable truncation, or `--max-columns-preview` to show a preview.

7. **Null data mode**: For NUL-delimited input (e.g., from `find -print0`), use `rg --null-data`.

8. **Exit codes**: 0 = matches found, 1 = no matches, 2 = error. Useful in scripts.

---

## Quick Reference

| Task | Command |
|---|---|
| Search recursively | `rg 'pattern'` |
| Case insensitive | `rg -i 'pattern'` |
| Smart case | `rg -S 'pattern'` |
| Whole word | `rg -w 'word'` |
| Fixed string | `rg -F 'literal'` |
| File type filter | `rg -t py 'pattern'` |
| Exclude type | `rg -T js 'pattern'` |
| Glob filter | `rg -g '*.tsx' 'pattern'` |
| Exclude glob | `rg -g '!test/**' 'pattern'` |
| Context lines | `rg -C 3 'pattern'` |
| Files only | `rg -l 'pattern'` |
| Count | `rg -c 'pattern'` |
| Match only | `rg -o 'pattern'` |
| Replace output | `rg 'old' -r 'new'` |
| Multiline | `rg -U 'multi\nline'` |
| PCRE2 | `rg -P '(?<=prefix)\w+'` |
| Hidden files | `rg --hidden 'pattern'` |
| No gitignore | `rg --no-ignore 'pattern'` |
| Search everything | `rg -uuu 'pattern'` |
| Max depth | `rg --max-depth 2 'pattern'` |
| JSON output | `rg --json 'pattern'` |
| Sorted by path | `rg --sort path 'pattern'` |
| List searchable files | `rg --files` |
| Statistics | `rg --stats 'pattern'` |

For extended recipes (language-specific, framework-specific, and complex pipeline patterns), see `references/recipes.md`.
