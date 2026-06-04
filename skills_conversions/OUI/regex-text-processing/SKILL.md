---
name: regex-text-processing
description: "Regular expressions and text processing patterns for non-CLI agents. Covers regex syntax, common validation/extraction patterns, Unicode handling, performance optimization, and text transformation recipes. Use when matching patterns, validating input, extracting data from text, or transforming string content."
version: "1.0.0"
metadata:
  category: data-skills
  scope: non-cli
---

# Regular Expressions and Text Processing

Pattern matching, text validation, extraction, and transformation across any context. Covers regex syntax, Unicode handling, performance optimization, and production-ready patterns.

## Quick Reference

### Character Classes

| Pattern | Matches |
|---------|---------|
| `.` | Any character (except newline, or any with `s` flag) |
| `\d` | Digit: 0-9 |
| `\D` | Non-digit |
| `\w` | Word character: [a-zA-Z0-9_] |
| `\W` | Non-word |
| `\s` | Whitespace: space, tab, newline, etc. |
| `\S` | Non-whitespace |
| `[abc]` | a, b, or c |
| `[^abc]` | NOT a, b, or c |
| `[a-z]` | Range: a through z |

### Quantifiers

| Pattern | Meaning |
|---------|---------|
| `*` | 0 or more (greedy) |
| `+` | 1 or more (greedy) |
| `?` | 0 or 1 (greedy) |
| `{n}` | Exactly n |
| `{n,}` | n or more |
| `{n,m}` | Between n and m |
| `*?`, `+?`, `??` | Non-greedy versions |

### Groups and Captures

```regex
(abc)           # Capturing group
(?:abc)         # Non-capturing group
(?<name>abc)    # Named capture group
\1              # Backreference to group 1
```

### Assertions

```regex
^       # Start of string (or line with m flag)
$       # End of string (or line with m flag)
\b      # Word boundary
\B      # Non-word boundary
(?=)    # Lookahead: assert what follows
(?!)    # Negative lookahead
(?<=)   # Lookbehind: assert what precedes
(?<!)   # Negative lookbehind
```

### Flags

| Flag | Name | Effect |
|------|------|--------|
| `g` | Global | Match all occurrences |
| `i` | Case-insensitive | Ignore case |
| `m` | Multiline | `^` and `$` match lines, not just string |
| `s` | Dotall | `.` matches newlines |
| `u` | Unicode | Full Unicode support |
| `y` | Sticky | Match only at `lastIndex` position |

---

## Common Patterns

### Email Validation

```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

### URL Extraction

```regex
https?://[^\s]+
```

### Phone Number (International)

```regex
^\+?(\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$
```

### IPv4 Address

```regex
^(\d{1,3}\.){3}\d{1,3}$
```

### IPv6 Address

```regex
^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$
```

### HTML Tag Extraction

```regex
<([a-z]+)[^>]*>(.*?)</\1>
```

### CSV Field Parsing (Handles Quoted Fields)

```regex
(?:^|,)(?:"([^"]*)"|([^,]*))
```

### Markdown Link Extraction

```regex
\[([^\]]+)\]\(([^)]+)\)
```

### Date Extraction (Common Formats)

```regex
\d{4}[-/]\d{2}[-/]\d{2}                    # ISO: 2025-01-15
\d{2}[-/]\d{2}[-/]\d{4}                    # US: 01/15/2025
(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}  # Jan 15, 2025
```

---

## Text Extraction Recipes

### Extract All URLs from Text

```
Pattern: https?://[^\s<>"')\]]+
Captures: Full URLs including path and query strings
Caveat: May capture trailing punctuation — trim .,; from end
```

### Extract Code Blocks from Markdown

```
Pattern: ```(\w*)\n([\s\S]*?)```
Group 1: Language identifier
Group 2: Code content
Flags: g (global)
```

### Extract Key-Value Pairs

```
Input:  "Name: John, Age: 30, Email: john@example.com"
Pattern: (\w+):\s*([^,]+)
Result: { Name: "John", Age: "30", Email: "john@example.com" }
```

### Parse Query Strings

```
Input:  "foo=bar&baz=qux&array=1&array=2"
Pattern: ([^=&]+)=([^&]*)
Result: { foo: "bar", baz: "qux", array: ["1", "2"] }
```

### Extract Mentions and Hashtags

```
Mentions: @(\w+)
Hashtags: #(\w+)
```

---

## Unicode Regex

### Unicode Property Escapes

```
\p{Letter} or \p{L}       — Any letter in any script
\p{Number} or \p{N}       — Any number character
\p{Punctuation} or \p{P}  — Any punctuation
\p{Emoji}                  — Emoji characters
\p{Currency_Symbol}        — Currency symbols ($, €, ¥, £)
\p{Script=Greek}           — Greek script characters
\p{Script=Han}             — Chinese/Japanese Kanji
```

Requires `u` flag in JavaScript/ES2020+. Python requires `regex` library (not `re`).

### Unicode Patterns

| Need | Pattern | Notes |
|------|---------|-------|
| Any word (multilingual) | `[\p{L}\p{N}_]+` | Letters + numbers + underscore, any script |
| Remove diacritics class | `\p{M}` | Combining marks (accents) |
| Emoji detection | `\p{Emoji}` | May match digits — combine with lookbehind |
| CJK characters | `\p{Script=Han}` | Chinese, Japanese Kanji |
| Arabic text | `\p{Script=Arabic}` | Arabic script |

---

## Performance Optimization

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `(a+)+b` | Catastrophic backtracking on no-match | Use atomic groups: `(?>a+)b` |
| `cat|dog|bird|fish` | Linear alternation scan | Order by frequency, or use character classes |
| `.*` | Overly broad matching | Be specific: `[^<]*` instead of `.*` |
| Nested quantifiers | Exponential backtracking | Flatten or use possessive quantifiers |
| Unanchored patterns | Unnecessary scanning | Use `^` and `$` where possible |

### Best Practices

1. **Use anchors**: `^pattern$` to avoid unnecessary scanning
2. **Be specific**: `\d{3}-\d{4}` instead of `\d+`
3. **Avoid nested quantifiers**: `(a+)+` → use `a+` or `(?:a+)+`
4. **Prefer character classes**: `[abc]` instead of `(a|b|c)`
5. **Compile once**: Reuse compiled patterns, don't recreate in loops
6. **Test with large inputs**: Backtracking becomes expensive on long strings
7. **Use non-capturing groups**: `(?:abc)` instead of `(abc)` when capture not needed

### Performance Characteristics

| Operation | Relative Cost | Recommendation |
|-----------|--------------|----------------|
| Literal match | Very fast | Prefer literals where possible |
| Character class | Fast | Good for single-character alternatives |
| Alternation | Moderate | Order by likelihood, limit branches |
| Backreference | Slow | Avoid if possible, use named captures sparingly |
| Lookahead/behind | Moderate | Keep assertions short |
| Nested quantifiers | Very slow | Avoid entirely |

---

## Text Transformation Patterns

### Find and Replace Recipes

| Transform | Pattern | Replacement |
|-----------|---------|-------------|
| Trim whitespace | `^\s+\|\s+$` | (empty) |
| Collapse multiple spaces | `\s{2,}` | (single space) |
| Normalize line endings | `\r\n?\|\n` | `\n` |
| Remove HTML tags | `<[^>]+>` | (empty) |
| Extract domain from URL | `https?://([^/]+)` | Group 1 |
| CamelCase to snake_case | `([a-z])([A-Z])` | `$1_$2` (lowercase result) |
| Capitalize first letter | `^([a-z])` | Uppercase group 1 |
| Remove non-alphanumeric | `[^\w\s]` | (empty) |

---

## Testing and Debugging

### Online Tools

| Tool | URL | Best For |
|------|-----|----------|
| regex101.com | regex101.com | Visual debugging with step-by-step matching |
| regexper.com | regexper.com | Syntax diagram visualization |
| debuggex.com | debuggex.com | Railroad diagram generation |

### Testing Checklist

- [ ] Matches expected positive cases
- [ ] Rejects expected negative cases
- [ ] Handles edge cases (empty string, single char, max length)
- [ ] No catastrophic backtracking on adversarial input
- [ ] Unicode characters handled correctly (if applicable)
- [ ] Performance acceptable on typical input sizes
- [ ] Capture groups return expected positions

### Debugging Steps

1. **Simplify**: Test the smallest failing portion of the pattern
2. **Remove groups**: Strip capturing groups, test core pattern
3. **Check anchors**: `^` and `$` may be the issue with multiline content
4. **Check greediness**: Try non-greedy quantifiers (`*?`, `+?`)
5. **Check flags**: Missing `m`, `s`, or `i` flags cause silent failures
6. **Test boundaries**: Empty input, single character, very long input

---

## When to Use

- Validating user input (email, phone, URLs, dates)
- Extracting structured data from unstructured text
- Parsing log files, CSV, or semi-structured formats
- Search and replace operations on text content
- Building text filters or transformation pipelines
- Detecting patterns in document content

## Limitations

- Complex nested structures (balanced parentheses, nested HTML) are better handled by parsers, not regex
- Performance degrades significantly with nested quantifiers on long inputs
- Unicode property escapes require modern engines (ES2020+ for JS, `regex` lib for Python)
- Regex cannot count — patterns like "n occurrences total" need programmatic verification
- Different regex engines have slight syntax variations

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [content-extraction](../content-extraction/SKILL.md) | Use regex patterns within content extraction pipelines |
| [web-crawling](../web-crawling/SKILL.md) | Regex for URL matching and content parsing during crawls |
| [data-visualization](../data-visualization/SKILL.md) | Clean and normalize data before visualization |
| [structured-thinking](../structured-thinking/SKILL.md) | Decompose complex pattern-matching problems systematically |
| [summarization](../summarization/SKILL.md) | Text preprocessing before summarization |
