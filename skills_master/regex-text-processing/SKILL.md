---
name: regex-text-processing
description: Regex and text processing with character classes, quantifiers, lookaround, backreferences, Unicode, and performance optimization.
version: 2.0.0
reviewed: "2026-06-04"
---

# Regular Expressions and Text Processing

Use this skill for **pattern matching, text validation, extraction, and transformation** across any programming language. Covers regex syntax, Unicode handling, performance optimization, and production-ready patterns.

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
(?<=)   # Lookbehind: assert what precedes (JavaScript, Python 3.8+)
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

### Phone Number (US)

```regex
^\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$
```

### IPv4 Address

```regex
^(\d{1,3}\.){3}\d{1,3}$
```

### HTML Tag Extraction

```regex
<([a-z]+)[^>]*>(.*?)</\1>
```

### CSV Parsing (Handles Quoted Fields)

```regex
(?:^|,)(?:"([^"]*)"|([^,]*))
```

### Markdown Link Extraction

```regex
\[([^\]]+)\]\(([^)]+)\)
```

---

## Performance Optimization

### Anti-Patterns to Avoid

```javascript
// BAD: Catastrophic backtracking
/(a+)+b/

// BAD: Inefficient alternation
/cat|dog|bird|fish|mouse/  // Order matters - put common patterns first

// GOOD: Use atomic groups or possessive quantifiers
/(?>[a-z]+)b/

// GOOD: More specific pattern
/(ca|do|bi|fi|mo)\w+/
```

### Best Practices

1. **Use anchors**: `^pattern$` to avoid unnecessary scanning
2. **Be specific**: `\d{3}-\d{4}` instead of `\d+`
3. **Avoid nested quantifiers**: `(a+)+` → use `a+` or `(?:a+)+`
4. **Prefer character classes**: `[abc]` instead of `(a|b|c)`
5. **Compile once**: Store regex in a variable, don't recreate in loops
6. **Test with large inputs**: Backtracking becomes expensive on long strings

### Benchmarking in JavaScript

```javascript
const pattern = /your-regex/g;
const text = '...large text...';

console.time('regex');
const matches = text.matchAll(pattern);
for (const m of matches) {} // consume iterator
console.timeEnd('regex');
```

---

## Unicode Regex

### JavaScript (ES2020+)

```javascript
// With u flag
const pattern = /\p{Letter}+/u;
const pattern2 = /\p{Script=Greek}+/u;

// Named Unicode properties
/\p{Emoji}/u
/\p{Number}/u
/\p{Currency_Symbol}/u
```

### Python (re module)

```python
import regex  # pip install regex

// Named character classes
pattern = regex.compile(r'\p{L}+')  // Letters in any script
pattern2 = regex.compile(r'\p{Emoji}')
```

---

## Real-World Parsing Recipes

### Extract Code Blocks from Markdown

```javascript
const markdown = '...';
const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;

for (const match of markdown.matchAll(codeBlockRegex)) {
  const lang = match[1];
  const code = match[2];
  console.log(`Language: ${lang}`);
  console.log(code);
}
```

### Parse Query String

```javascript
const queryString = 'foo=bar&baz=qux&array=1&array=2';
const regex = /([^=&]+)=([^&]*)/g;
const params = {};

for (const match of queryString.matchAll(regex)) {
  const [, key, value] = match;
  if (params[key]) {
    params[key] = Array.isArray(params[key]) ? [...params[key], value] : [params[key], value];
  } else {
    params[key] = value;
  }
}
```

### Extract Structured Data from Text

```javascript
// Parse "Name: John, Age: 30, Email: john@example.com"
const text = 'Name: John, Age: 30, Email: john@example.com';
const regex = /(\w+):\s*([^,]+)/g;

const data = {};
for (const match of text.matchAll(regex)) {
  const [, key, value] = match;
  data[key] = value.trim();
}
```

---

## Testing Regex Patterns

### Online Tools

- **regex101.com** - Visual debugger with detailed explanation
- **regexper.com** - Syntax diagram generator
- **repro.sh** - Regex reproducers with test cases

### Testing in Code

```javascript
// Simple test harness
const tests = [
  { pattern: /^\d{3}-\d{4}$/, input: '123-4567', expected: true },
  { pattern: /^\d{3}-\d{4}$/, input: '12-456', expected: false },
];

for (const test of tests) {
  const result = test.pattern.test(test.input);
  console.assert(result === test.expected, `Failed: ${test.input}`);
}
```

---

## Resources

| Resource | Purpose |
|----------|---------|
| [regex101.com](https://regex101.com) | Online regex tester and debugger |
| [MDN RegExp](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp) | JavaScript RegExp documentation |
| [Python re module](https://docs.python.org/3/library/re.html) | Python regex documentation |
| [Regular-Expressions.info](https://www.regular-expressions.info/) | Comprehensive regex reference |
