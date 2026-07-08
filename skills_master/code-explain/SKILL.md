---
name: code-explain
description: Explain code, debug errors, write tests. Use when user pastes code, asks what code does, wants to understand an error, or needs help fixing broken code.
user-invocable: true
---

# Code Explanation & Debugging

Use this skill when the user pastes code, asks what code does, encounters an error, or wants help fixing or improving code.

## When to Use

- User pastes code and asks "what does this do?"
- Error messages to explain or fix
- "Debug this", "fix this bug"
- "How does [library/pattern/framework] work?"
- "Write a test for this"
- "Explain this error"
- General programming help

## Code Explanation Framework

### Step 1 — Identify the Language & Framework

```python
def identify_stack(code: str) -> dict:
    """Detect language, framework, and purpose."""
    signals = {
        "typescript": ["interface", ": string", ": number", "import type"],
        "python": ["def ", "import ", "print(", "self."],
        "react": ["useState", "useEffect", "<Component", "JSX"],
        "nextjs": ["'use client'", "next.config", "app/", "route.ts"],
        "docker": ["FROM ", "docker compose", "RUN ", "CMD "],
        "sql": ["SELECT ", "INSERT ", "CREATE TABLE", "--"],
        "bash": ["#!/bin", "export ", "if [", "echo "]
    }
    
    detected = []
    for lang, markers in signals.items():
        if any(m in code for m in markers):
            detected.append(lang)
    
    return {"languages": detected, "purpose": infer_purpose(code)}
```

### Step 2 — Structure the Explanation

```markdown
## Code Analysis: [Filename/Snippet]

**Language:** [TypeScript / Python / etc.]
**Purpose:** [What this code does — 1 sentence]
**Complexity:** [Simple / Moderate / Complex]

### What It Does (Step by Step)

```
1. [First logical step — plain language]
2. [Second step]
3. [Third step]
...
```

### Key Components

| Component | Location | What It Does |
|-----------|----------|-------------|
| [Component 1] | Lines X–Y | [Description] |
| [Component 2] | Lines Y–Z | [Description] |

### Data Flow

```
[Input/Source] → [Processing] → [Output/Destination]
```

### Potential Issues

- [Issue 1] — [Why it's a problem] — [Fix suggestion]
- [Issue 2] — ...

### Equivalent Modern Pattern (if outdated)

```[Language]
[Modern equivalent code]
```

### When to Use This Pattern

- [Use case 1]
- [Use case 2]

## Error Diagnosis Pattern

```python
def diagnose_error(error_text: str) -> dict:
    """Parse and explain error messages."""
    
    # Common patterns
    error_patterns = {
        "import_error": {
            "pattern": r"ModuleNotFoundError|NoModuleNamed|ImportError",
            "explain": "Python can't find the module. Check: spelling, installation, path",
            "fix": "pip install [module] or check PYTHONPATH"
        },
        "syntax_error": {
            "pattern": r"SyntaxError|ParseError|unexpected token",
            "explain": "Code doesn't follow language grammar rules",
            "fix": "Check matching brackets, quotes, indentation, keywords"
        },
        "type_error": {
            "pattern": r"TypeError|cannot concatenate|is not a function",
            "explain": "Wrong data type used (e.g., adding string to number)",
            "fix": "Convert types, check variable types, validate inputs"
        },
        "null_undefined": {
            "pattern": r"null|undefined|Cannot read|is not defined",
            "explain": "Variable doesn't have a value yet or was deleted",
            "fix": "Add null checks, handle undefined, check scope"
        },
        "auth_error": {
            "pattern": r"401|403|unauthorized|forbidden|permission denied",
            "explain": "Not authenticated or not authorised for this action",
            "fix": "Check API key, token, permissions, headers"
        },
        "rate_limit": {
            "pattern": r"429|rate limit|too many requests",
            "explain": "Too many requests sent too quickly",
            "fix": "Add delays between requests, implement backoff, check quotas"
        },
        "database_error": {
            "pattern": r"SQLSyntaxError|constraint|foreign key|duplicate key",
            "explain": "Database operation failed — usually SQL or schema issue",
            "fix": "Check SQL syntax, constraints, table existence, data types"
        }
    }
    
    for error_type, info in error_patterns.items():
        if re.search(info["pattern"], error_text, re.IGNORECASE):
            return {
                "type": error_type,
                "explanation": info["explain"],
                "likely_cause": extract_cause(error_text),
                "fix_steps": info["fix"],
                "example_fix": get_fix_example(error_type)
            }
    
    return {
        "type": "unknown",
        "explanation": "General error — need more context",
        "suggestion": "Check the full stack trace, line number, and surrounding code"
    }
```

## Debugging Checklist

```markdown
## Debugging: [Error/Issue]

### Error Type
[type]

### What's Happening
[Plain language explanation of the error]

### Likely Causes (Most to Least Likely)
1. [Cause 1] — [why this fits]
2. [Cause 2] — [why this fits]
3. [Cause 3] — [least likely]

### Fix for Most Likely Cause

```[language]
[Fixed code]
```

### Verification
- [ ] Run the code again
- [ ] Check the error is resolved
- [ ] Test edge cases

### Prevention
- [ ] How to avoid this error in future
```

## Test Writing Pattern

```python
def write_tests(code: str, language: str) -> str:
    """Generate appropriate tests for the provided code."""
    
    if language == "python":
        return f'''import pytest
from your_module import your_function

class TestYourFunction:
    def test_happy_path(self):
        """Test with valid normal input."""
        result = your_function("valid input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Test with boundary condition."""
        result = your_function("")
        assert result is not None
    
    def test_error_case(self):
        """Test that invalid input raises appropriate error."""
        with pytest.raises(ValueError):
            your_function("invalid")
    
    def test_type_error(self):
        """Test with wrong type — should handle gracefully."""
        result = your_function(123)
        assert result is None  # or appropriate fallback
'''

    elif language == "typescript":
        return f'''import {{ describe, it, expect }} from "vitest";

describe("yourFunction", () => {{
  it("handles valid input", () => {{
    expect(yourFunction("valid")).toBe("expected");
  }});

  it("handles empty string", () => {{
    expect(yourFunction("")).toBeDefined();
  }});

  it("throws on invalid input", () => {{
    expect(() => yourFunction("bad")).toThrow();
  }});
}});
'''
```

## Common Anti-Patterns to Flag

```python
anti_patterns = {
    "python": {
        "bare_except": "except: → except Exception as e:",
        "mutable_default": "def f(x=[]): → def f(x=None): x=x or []",
        "shadowing": "Don't use same name for outer/inner variable",
        "string_concat": "'str' + var → f'str{{var}}' or str.format()"
    },
    "typescript": {
        "any_type": "Avoid : any — use specific types or unknown",
        "missing_error": "Always handle Promise rejections with .catch() or try/catch",
        "unsafe_dom": "Don't use innerHTML — use textContent or sanitised HTML",
        "missing_deps": "useEffect without deps array → infinite loop risk"
    },
    "general": {
        "hardcoded_secrets": "Never hardcode API keys — use env vars",
        "sql_concat": "Never f'SELECT * FROM {user_input}' → use parameterized queries",
        "sync_in_async": "Don't use sync code in async function without await"
    }
}
```

## Sources

- Python error messages — docs.python.org/3/reference/expressions.html
- TypeScript handbook — www.typescriptlang.org/docs
- Stack Overflow (general) — stackoverflow.com
- MDN Web Docs (JS) — developer.mozilla.org