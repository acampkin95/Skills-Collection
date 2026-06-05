# Learned: Safe CSS Deduplication Strategy

**Pattern type:** `workflow`
**Extracted from:** MyKinkFile triple-loop session (2026-05-05)

## Problem

Large CSS files (~1600+ lines) accumulate duplicate `@keyframes` and utility class
definitions over time. Blind removal causes subtle visual regressions because CSS
cascade means the **last** definition wins — removing it changes behavior.

## Classification Framework

Before removing any duplicate, classify it:

### 1. IDENTICAL duplicates → SAFE to remove first occurrence
Both definitions have the exact same properties and values.

```
@keyframes fadeInScale {        ← line 465 (REMOVE)
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
...
@keyframes fadeInScale {        ← line 1506 (KEEP — last wins)
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

### 2. DIFFERENT values, same name → DO NOT REMOVE
Two genuinely different animations share a name. The second overrides the first,
so the first is "dead code" — but renaming requires checking all usages.

```
@keyframes pulseSubtle {           ← line 877: box-shadow glow
  50% { box-shadow: 0 0 20px 4px rgba(99,102,241,0.2); }
}
@keyframes pulseSubtle {           ← line 1487: opacity fade (WINS)
  50% { opacity: 1; }
}
```

Removing the first is safe (already overridden), but renaming the second to give
the first its own name requires auditing every component using the class.

### 3. Utility class duplicates → check values carefully
```css
.text-gradient-indigo {              ← v1: #818cf8 → #a78bfa (REMOVE)
.text-gradient-indigo {              ← v2: #818cf8 → #c084fc (KEEP)
```
Different endpoint colors — the second was clearly an intentional update.

## Removal Checklist

1. `grep` for ALL occurrences of the keyframe/class name
2. Read each occurrence and compare values
3. If identical → remove all but the last
4. If different → leave both, add a `/* FIXME: conflicting definitions */` comment
5. After removals, run type-check + lint + tests + build
6. Visual smoke test on production

## A11y Focus Ring Pattern

While auditing CSS, also check for focus-visible gaps:

```bash
# Find elements with outline:none but no focus ring replacement
rg 'outline-none' --include='*.tsx' | grep -v 'focus:ring'
```

Every `focus:outline-none` MUST be paired with `focus:ring-*` or similar.
Elements with only `focus:outline-none` suppress the global focus indicator
without providing a replacement — this is an a11y violation.

## Metrics

On MyKinkFile globals.css:
- Removed 4 safe duplicates (~30 lines)
- Identified 3 conflicting keyframe pairs (noted for future rename)
- Fixed 3 a11y focus ring gaps
- File reduced from ~1604 to ~1570 lines with zero regressions
