# Production-Ready Validation Patterns

## Email (RFC 5322 Simplified)

```ts
// Covers 99.9% of real-world emails
const EMAIL = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

function isValidEmail(email: string): boolean {
  if (email.length > 254) return false;
  const [local, domain] = email.split("@");
  if (!local || local.length > 64) return false;
  if (!domain) return false;
  return EMAIL.test(email);
}
```

## URL

```ts
// HTTP/HTTPS URLs
const URL_HTTP = /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)$/;

// Any protocol
const URL_ANY = /^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\s]+$/;

// Practical: also match URLs without protocol
const URL_LOOSE = /^(?:https?:\/\/)?(?:[\w-]+\.)+[a-z]{2,}(?:\/[^\s]*)?$/i;
```

## IPv4 and IPv6

```ts
// IPv4: 0.0.0.0 to 255.255.255.255
const IPV4 = /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$/;

// IPv6 (simplified — covers most forms)
const IPV6 = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$/;

// Practical: use built-in when available
function isValidIP(ip: string): boolean {
  // Node.js
  const net = await import("node:net");
  return net.isIP(ip) !== 0;
}
```

## Phone (E.164 International)

```ts
// E.164: +[country code][number], max 15 digits total
const E164 = /^\+[1-9]\d{1,14}$/;

// US phone (various formats)
const US_PHONE = /^(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$/;

// Normalize to E.164
function normalizePhone(phone: string, countryCode = "1"): string {
  const digits = phone.replace(/\D/g, "");
  if (digits.startsWith(countryCode)) return `+${digits}`;
  return `+${countryCode}${digits}`;
}
```

## Credit Card (with Luhn Check)

```ts
// Card number format (13-19 digits, optionally with spaces/dashes)
const CARD_NUMBER = /^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{1,7}$/;

// Card type detection
const CARD_TYPES = {
  visa: /^4\d{12}(?:\d{3})?$/,
  mastercard: /^5[1-5]\d{14}$|^2(?:2[2-9]\d{2}|[3-6]\d{3}|7[01]\d{2}|720)\d{12}$/,
  amex: /^3[47]\d{13}$/,
  discover: /^6(?:011|5\d{2})\d{12}$/,
};

// Luhn algorithm
function luhnCheck(cardNumber: string): boolean {
  const digits = cardNumber.replace(/\D/g, "");
  let sum = 0;
  let isEven = false;

  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10);
    if (isEven) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    isEven = !isEven;
  }

  return sum % 10 === 0;
}

function detectCardType(number: string): string | null {
  const clean = number.replace(/\D/g, "");
  for (const [type, pattern] of Object.entries(CARD_TYPES)) {
    if (pattern.test(clean)) return type;
  }
  return null;
}
```

## UUID (v4 and Any Version)

```ts
// UUID v4 specifically
const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

// Any UUID version
const UUID_ANY = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// UUID without dashes
const UUID_NODASH = /^[0-9a-f]{32}$/i;
```

## Semantic Version

```ts
// Full semver with pre-release and build metadata
const SEMVER = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;

function parseSemver(version: string) {
  const match = version.match(SEMVER);
  if (!match) return null;
  return {
    major: parseInt(match[1]),
    minor: parseInt(match[2]),
    patch: parseInt(match[3]),
    prerelease: match[4] || null,
    build: match[5] || null,
  };
}
```

## Hex Color

```ts
// 3 or 6 digit hex
const HEX_COLOR = /^#(?:[0-9a-f]{3}){1,2}$/i;

// 3, 4, 6, or 8 digit (with alpha)
const HEX_COLOR_ALPHA = /^#(?:[0-9a-f]{3,4}){1,2}$/i;

// CSS color (hex, rgb, hsl, named)
const CSS_COLOR = /^(?:#(?:[0-9a-f]{3,4}){1,2}|rgb\(\s*\d{1,3}(?:\s*,\s*\d{1,3}){2}\s*\)|rgba\(\s*\d{1,3}(?:\s*,\s*\d{1,3}){2}\s*,\s*[\d.]+\s*\)|hsl\(\s*\d{1,3}\s*,\s*\d{1,3}%\s*,\s*\d{1,3}%\s*\)|[a-z]+)$/i;
```

## Slug

```ts
// URL-safe slug
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

// With optional forward slashes (nested routes)
const SLUG_PATH = /^[a-z0-9]+(?:[-/][a-z0-9]+)*$/;
```

## File Extensions

```ts
// Common image types
const IMAGE_EXT = /\.(jpe?g|png|gif|webp|avif|svg|ico)$/i;

// Common document types
const DOC_EXT = /\.(pdf|docx?|xlsx?|pptx?|csv|txt|rtf)$/i;

// Common code types
const CODE_EXT = /\.(ts|tsx|js|jsx|py|go|rs|java|c|cpp|h|rb|php|swift|kt)$/i;

// Safe filename (no path traversal)
const SAFE_FILENAME = /^[a-zA-Z0-9][\w\-. ]*[a-zA-Z0-9]$/;
```

## Password Strength

```ts
// Minimum 8 chars, at least one uppercase, lowercase, digit, special
const STRONG_PASSWORD = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]).{8,}$/;

function passwordStrength(password: string): "weak" | "fair" | "strong" {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;
  if (score <= 2) return "weak";
  if (score <= 3) return "fair";
  return "strong";
}
```

## Date Formats

```ts
// ISO 8601 date
const ISO_DATE = /^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$/;

// ISO 8601 datetime
const ISO_DATETIME = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$/;

// US date (MM/DD/YYYY)
const US_DATE = /^(?:0[1-9]|1[0-2])\/(?:0[1-9]|[12]\d|3[01])\/\d{4}$/;
```

## ISO 8601 Full (Date, Datetime, Duration, Interval)

```ts
// Full ISO 8601 datetime with optional fractional seconds and timezone
const ISO_8601_FULL = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}(?::?\d{2})?)$/;

// ISO 8601 duration: P[n]Y[n]M[n]DT[n]H[n]M[n]S
const ISO_DURATION = /^P(?:\d+Y)?(?:\d+M)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$/;

// ISO 8601 week date: 2025-W05-1
const ISO_WEEK = /^\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])(?:-[1-7])?$/;
```

## JWT Token

```ts
// JWT format: header.payload.signature (Base64url encoded)
const JWT = /^[A-Za-z0-9_-]{2,}(?:\.[A-Za-z0-9_-]{2,}){2}$/;

function isJWT(token: string): boolean {
  if (!JWT.test(token)) return false;
  try {
    const [header] = token.split(".");
    const decoded = JSON.parse(atob(header.replace(/-/g, "+").replace(/_/g, "/")));
    return "alg" in decoded;
  } catch {
    return false;
  }
}
```

## Base64 and Base64url

```ts
// Standard Base64
const BASE64 = /^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/;

// Base64url (URL-safe variant, used in JWTs)
const BASE64URL = /^[A-Za-z0-9_-]+$/;

function isBase64(str: string): boolean {
  if (str.length % 4 !== 0 && !BASE64URL.test(str)) return false;
  return BASE64.test(str) || BASE64URL.test(str);
}
```

## CIDR Notation

```ts
// IPv4 CIDR: 192.168.1.0/24
const CIDR_V4 = /^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\/(?:3[0-2]|[12]?\d)$/;

// IPv6 CIDR: 2001:db8::/32
const CIDR_V6 = /^(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}\/(?:12[0-8]|1[01]\d|[1-9]?\d)$/;

function parseCIDR(cidr: string): { ip: string; prefix: number } | null {
  const match = cidr.match(/^(.+)\/(\d+)$/);
  if (!match) return null;
  return { ip: match[1], prefix: parseInt(match[2]) };
}
```

## Cron Expression

```ts
// Standard cron (5 fields): minute hour day-of-month month day-of-week
const CRON_5 = /^(\*|[0-5]?\d)(?:\/\d+)?\s+(\*|[01]?\d|2[0-3])(?:\/\d+)?\s+(\*|[1-9]|[12]\d|3[01])(?:\/\d+)?\s+(\*|[1-9]|1[0-2])(?:\/\d+)?\s+(\*|[0-7])(?:\/\d+)?$/;

// With aliases and ranges (practical)
const CRON_EXTENDED = /^(?:[\d*,/-]+\s+){4}[\d*,/-]+$/;

function describeCron(expr: string): string {
  const parts = expr.split(/\s+/);
  if (parts.length !== 5) return "Invalid cron";
  const [min, hr, dom, mon, dow] = parts;
  if (expr === "* * * * *") return "Every minute";
  if (min === "0" && hr === "*") return "Every hour at :00";
  if (min === "0" && hr === "0") return "Daily at midnight";
  if (dow === "1" && min === "0" && hr === "9") return "Every Monday at 9:00 AM";
  return `At ${min} min, ${hr} hr, dom=${dom}, mon=${mon}, dow=${dow}`;
}
```

## Usage Pattern: Validate Function Factory

```ts
function createValidator(pattern: RegExp, message: string) {
  return (value: string): { valid: boolean; error?: string } => {
    if (pattern.test(value)) return { valid: true };
    return { valid: false, error: message };
  };
}

const validators = {
  email: createValidator(EMAIL, "Invalid email address"),
  phone: createValidator(E164, "Phone must be E.164 format (+1234567890)"),
  slug: createValidator(SLUG, "Slug must be lowercase with hyphens only"),
  uuid: createValidator(UUID_V4, "Invalid UUID v4"),
  jwt: createValidator(JWT, "Invalid JWT format"),
  cidr: createValidator(CIDR_V4, "Invalid CIDR notation"),
};

// Usage
const result = validators.email("test@example.com");
// { valid: true }
```

## Testing Regex Patterns

### Unit Testing with Vitest/Jest

```ts
import { describe, it, expect } from "vitest";

describe("EMAIL regex", () => {
  const valid = ["user@example.com", "user+tag@sub.domain.co", "a@b.cc"];
  const invalid = ["@no-local.com", "no-at-sign", "no@tld", "spaces @bad.com", ""];

  it.each(valid)("accepts valid email: %s", (email) => {
    expect(EMAIL.test(email)).toBe(true);
  });

  it.each(invalid)("rejects invalid email: %s", (email) => {
    expect(EMAIL.test(email)).toBe(false);
  });
});

// Parameterized boundary testing
describe("E164 phone", () => {
  it.each([
    ["+1234567890", true],
    ["+12345678901234", true],      // 14 digits after +
    ["+123456789012345", true],     // 15 digits (max)
    ["+1234567890123456", false],   // 16 digits (too long)
    ["+0123456789", false],         // Leading zero in country code
    ["1234567890", false],          // Missing +
    ["+", false],                   // Just +
  ])("E164.test(%s) → %s", (input, expected) => {
    expect(E164.test(input)).toBe(expected);
  });
});
```

### Testing Capture Groups

```ts
describe("SEMVER capture groups", () => {
  it("extracts version components", () => {
    const m = "2.14.3-beta.1+build.42".match(SEMVER);
    expect(m).not.toBeNull();
    expect(m![1]).toBe("2");           // major
    expect(m![2]).toBe("14");          // minor
    expect(m![3]).toBe("3");           // patch
    expect(m![4]).toBe("beta.1");      // prerelease
    expect(m![5]).toBe("build.42");    // build metadata
  });
});
```

### ReDoS Safety Testing

```ts
// Test that regex completes within time limit (catches catastrophic backtracking)
function testRegexPerformance(pattern: RegExp, evilInput: string, maxMs = 100) {
  const start = performance.now();
  pattern.test(evilInput);
  const elapsed = performance.now() - start;
  expect(elapsed).toBeLessThan(maxMs);
}

it("EMAIL regex is safe from ReDoS", () => {
  const evilInput = "a".repeat(50) + "@" + "b".repeat(50);
  testRegexPerformance(EMAIL, evilInput);
});
```
