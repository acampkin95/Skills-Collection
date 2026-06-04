---
name: ripgrep
description: Ripgrep (rg) recursive text search for files and codebases. Use for regex pattern matching, codebase search, log analysis, dead code detection, and secret scanning.
version: 2.0.0
reviewed: "2026-06-04"
---

# Ripgrep — Search Skill

`rg` is the fastest recursive search tool. Respects `.gitignore`, supports full regex, Unicode.

## Mental Model

1. **File discovery** — which files (gitignore, hidden, file types, globs)
2. **Pattern matching** — what to find (regex, literal, case)
3. **Output shaping** — how to present (context, format, grouping)

## Essential Commands

```bash
rg 'pattern'                    # Search current dir recursively
rg 'pattern' path/              # Search specific path
rg -i 'pattern'                 # Case-insensitive
rg -l 'pattern'                 # List matching files only
rg -c 'pattern'                 # Count matches per file
rg -n 'pattern'                 # Show line numbers (default)
rg -w 'word'                    # Whole word match
rg -F 'literal.string'         # Fixed string (no regex)
```

## File Filtering

```bash
rg -t ts 'pattern'              # Search TypeScript files only
rg -T json 'pattern'            # Exclude JSON files
rg -g '*.css' 'pattern'         # Glob include
rg -g '!*.min.*' 'pattern'      # Glob exclude
rg --hidden 'pattern'           # Include hidden files
rg --no-ignore 'pattern'        # Ignore .gitignore
```

## Context & Output

```bash
rg -C 3 'pattern'               # 3 lines context before/after
rg -B 2 'pattern'               # 2 lines before
rg -A 5 'pattern'               # 5 lines after
rg --heading 'pattern'          # Group by file
rg --no-filename 'pattern'      # Suppress filename
rg -0 'pattern'                 # Null-separated (pipe to xargs -0)
```

## Advanced Patterns

```bash
rg -U 'import.*from'            # Multi-line mode
rg --regex 'foo\nbar'           # Explicit newline match
rg -e 'pat1' -e 'pat2'          # Multiple patterns (OR)
rg -v 'pattern'                 # Invert match (non-matching lines)
rg --sort path 'pattern'        # Sort output by path
rg --json 'pattern'             # JSON output for tooling
```

## Replace Mode

```bash
rg 'old' -r 'new'               # Preview replacements
sed -i '' 's/old/new/g' file   # For actual file modification
```

## Full Reference

See [full-reference.md](references/full-reference.md) for complete flag reference, regex syntax, advanced recipes, performance tuning, and troubleshooting.
