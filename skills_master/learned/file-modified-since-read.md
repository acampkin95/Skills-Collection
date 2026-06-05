# Learned: File Modified Since Read Recovery

**Pattern type:** `error_resolution`
**Extracted from:** HUD fix session (2026-02-22)

## Problem

When calling `Edit` on a file, Claude Code may return:

```
File has been modified since read, either by the user or by a linter.
Read it again before attempting to write it.
```

This happens when settings sync, formatters (Prettier, Biome), or background processes
touch the file between the initial `Read` and the subsequent `Edit`.

## Solution

Immediately re-read the file, then retry the edit. No other changes needed.

```
1. Read <file> again (captures current on-disk state)
2. Retry the Edit with the same old_string/new_string
```

## Notes

- Common with `~/.claude/settings.json` (Claude Code rewrites it on plugin changes)
- Common with files watched by Prettier/Biome/ESLint auto-format on save
- The re-read does NOT need to be followed by any analysis — just proceed directly to the edit
- If the edit fails a second time, the file content may have changed substantially; inspect the new content before constructing old_string
