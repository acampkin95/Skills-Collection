# Learned: Biome Overrides for TSX Components

**Pattern type:** `error_resolution`
**Extracted from:** MyKinkFile triple-loop session (2026-05-05)

## Problem

Inline `// biome-ignore` comments in TSX prop positions are silently ignored by Biome.
The lint rule fires anyway, and the comment sits there looking like it's working but isn't.

```tsx
// ❌ DOES NOT WORK — biome-ignore in prop position is ignored
<div
  role="img" // biome-ignore lint/a11y/useSemanticElements: decorative
  aria-hidden="true"
>
```

This happens because Biome's comment-based suppression only works when the comment
is on the line immediately before the **statement** or **declaration** — not inside
JSX attribute lists.

## Solution

Move suppressions to `biome.json` `overrides` array. This is reliable and centralized.

```jsonc
// biome.json
{
  "overrides": [
    {
      "include": ["apps/frontend/src/app/quiz/components/milestone-toast.tsx"],
      "linter": {
        "rules": {
          "a11y": {
            "useSemanticElements": "off"
          }
        }
      }
    },
    {
      "include": ["apps/frontend/src/app/_components/hero-artwork.tsx"],
      "linter": {
        "rules": {
          "a11y": {
            "noSvgWithoutTitle": "off",
            "noArrayIndexKey": "off"
          }
        }
      }
    }
  ]
}
```

Then remove the inline `// biome-ignore` comments from the TSX files.

## When to Apply

- Any time Biome reports a lint error in a TSX file and inline suppression doesn't work
- Decorative SVGs without `title` (use `aria-hidden="true"` + override)
- Semantic element warnings on custom components that serve a valid role
- Array index keys in stable SVG element lists (e.g., `<path>` arrays in icons)

## Anti-Patterns

- Don't blanket-disable rules across the whole project — target specific files
- Don't use overrides to silence genuine a11y issues — fix the HTML first
- Always pair `noSvgWithoutTitle: off` with `aria-hidden="true"` on the SVG

## Related

- Biome v2.4+ `overrides` with `include` glob patterns
- Also applies to `include` blocks for groups of files sharing the same pattern
