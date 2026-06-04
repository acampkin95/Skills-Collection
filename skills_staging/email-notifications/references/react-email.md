# React Email Reference

Detailed patterns for building production email templates with React Email.

## Project Structure

```
emails/
├── components/         # Shared email components
│   ├── email-layout.tsx
│   ├── email-button.tsx
│   ├── email-header.tsx
│   └── email-footer.tsx
├── welcome.tsx         # Individual templates
├── verification.tsx
├── password-reset.tsx
├── invoice.tsx
└── digest.tsx
```

## Shared Layout Component

```tsx
// emails/components/email-layout.tsx
import {
  Html, Head, Preview, Body, Container, Section, Text, Link, Hr, Img,
} from "@react-email/components";

interface EmailLayoutProps {
  preview: string;
  children: React.ReactNode;
  footerLinks?: { label: string; href: string }[];
}

export function EmailLayout({ preview, children, footerLinks }: EmailLayoutProps) {
  return (
    <Html lang="en" dir="ltr">
      <Head>
        <meta name="color-scheme" content="light dark" />
        <meta name="supported-color-schemes" content="light dark" />
      </Head>
      <Preview>{preview}</Preview>
      <Body style={body}>
        <Container style={container}>
          <Section style={header}>
            <Img
              src={`${process.env.NEXT_PUBLIC_APP_URL}/email-logo.png`}
              width={120}
              height={40}
              alt="Company"
            />
          </Section>
          <Section style={content}>{children}</Section>
          <Hr style={hr} />
          <Section style={footerSection}>
            <Text style={footerText}>
              &copy; {new Date().getFullYear()} Company Inc.
            </Text>
            {footerLinks?.map((link) => (
              <Link key={link.href} href={link.href} style={footerLink}>
                {link.label}
              </Link>
            ))}
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const body = {
  backgroundColor: "#f6f9fc",
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  margin: "0",
  padding: "0",
};
const container = { backgroundColor: "#ffffff", margin: "40px auto", maxWidth: "560px", borderRadius: "8px", overflow: "hidden" as const };
const header = { padding: "32px 40px 0" };
const content = { padding: "24px 40px" };
const hr = { borderColor: "#e5e7eb", margin: "0" };
const footerSection = { padding: "24px 40px" };
const footerText = { color: "#9ca3af", fontSize: "12px", margin: "0 0 8px" };
const footerLink = { color: "#6b7280", fontSize: "12px", marginRight: "16px", textDecoration: "underline" };
```

## Responsive Email Patterns

Email clients have limited CSS support. Use these patterns:

### Table-Based Columns

```tsx
import { Row, Column, Section } from "@react-email/components";

// Two-column layout
<Section>
  <Row>
    <Column style={{ width: "50%", paddingRight: "8px" }}>
      <Text>Left column</Text>
    </Column>
    <Column style={{ width: "50%", paddingLeft: "8px" }}>
      <Text>Right column</Text>
    </Column>
  </Row>
</Section>
```

### Mobile-Friendly Width

```tsx
// Container max-width ensures readability on all screens
const container = {
  maxWidth: "560px",  // Standard email width
  margin: "0 auto",
  width: "100%",      // Fills mobile screens
};
```

### Fluid Images

```tsx
<Img
  src="https://yourdomain.com/hero.png"
  width={560}
  height={280}
  alt="Hero image"
  style={{
    width: "100%",
    height: "auto",
    display: "block",
    border: "0",
  }}
/>
```

## Dark Mode Support

Email dark mode is opt-in and partially supported. Use `color-scheme` meta and defensive styles:

```tsx
<Head>
  <meta name="color-scheme" content="light dark" />
  <meta name="supported-color-schemes" content="light dark" />
  <style>{`
    :root { color-scheme: light dark; }
    @media (prefers-color-scheme: dark) {
      .email-body { background-color: #1a1a2e !important; }
      .email-container { background-color: #16213e !important; }
      .email-text { color: #e0e0e0 !important; }
      .email-heading { color: #ffffff !important; }
      .email-muted { color: #a0a0a0 !important; }
    }
  `}</style>
</Head>

{/* Use className for dark-mode overrides, inline style for light-mode base */}
<Body className="email-body" style={{ backgroundColor: "#f6f9fc" }}>
  <Container className="email-container" style={{ backgroundColor: "#ffffff" }}>
    <Text className="email-text" style={{ color: "#1a1a1a" }}>
      This text adapts to dark mode.
    </Text>
  </Container>
</Body>
```

**Dark mode support by client:**
| Client | Support |
|--------|---------|
| Apple Mail | Full (`prefers-color-scheme`) |
| iOS Mail | Full |
| Gmail (web) | Partial (auto-inverts) |
| Gmail (mobile) | Partial (auto-inverts) |
| Outlook (desktop) | None |
| Outlook.com | Partial |

## Tailwind in Email

React Email supports Tailwind via `@react-email/tailwind`:

```tsx
import { Tailwind } from "@react-email/tailwind";

export default function StyledEmail() {
  return (
    <Html>
      <Tailwind
        config={{
          theme: {
            extend: {
              colors: {
                brand: "#2563eb",
                "brand-dark": "#1d4ed8",
              },
            },
          },
        }}
      >
        <Body className="bg-gray-100 font-sans">
          <Container className="bg-white mx-auto max-w-[560px] rounded-lg p-10">
            <Text className="text-2xl font-bold text-gray-900">
              Hello World
            </Text>
            <Button
              href="https://example.com"
              className="bg-brand text-white rounded-md px-6 py-3 font-semibold"
            >
              Click Me
            </Button>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}
```

**Tailwind limitations in email:**
- No hover/focus states (most email clients strip them)
- No `gap`, `grid`, or flexbox — use `Row`/`Column` for layout
- `max-w-*` works on `Container` only
- Tailwind classes are compiled to inline styles at render time

## Common Email Templates

### Password Reset

```tsx
// emails/password-reset.tsx
import { EmailLayout } from "./components/email-layout";
import { Text, Button, CodeInline } from "@react-email/components";

interface PasswordResetProps {
  resetUrl: string;
  expiresInMinutes: number;
}

export default function PasswordReset({ resetUrl, expiresInMinutes = 60 }: PasswordResetProps) {
  return (
    <EmailLayout preview="Reset your password">
      <Text style={{ fontSize: "20px", fontWeight: "600", color: "#1a1a1a" }}>
        Password Reset Request
      </Text>
      <Text style={{ fontSize: "16px", color: "#4a4a4a", lineHeight: "26px" }}>
        We received a request to reset your password. Click the button below to
        choose a new password. This link expires in {expiresInMinutes} minutes.
      </Text>
      <Button
        href={resetUrl}
        style={{
          backgroundColor: "#2563eb",
          color: "#ffffff",
          padding: "12px 24px",
          borderRadius: "6px",
          fontSize: "16px",
          fontWeight: "600",
          textDecoration: "none",
        }}
      >
        Reset Password
      </Button>
      <Text style={{ fontSize: "14px", color: "#6b7280", marginTop: "24px" }}>
        If you didn&apos;t request this, you can safely ignore this email.
      </Text>
    </EmailLayout>
  );
}
```

### Invoice / Receipt

```tsx
// emails/invoice.tsx
import { EmailLayout } from "./components/email-layout";
import { Text, Section, Row, Column, Hr } from "@react-email/components";

interface InvoiceProps {
  invoiceNumber: string;
  items: { name: string; qty: number; price: number }[];
  total: number;
  currency: string;
}

export default function Invoice({ invoiceNumber, items, total, currency }: InvoiceProps) {
  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);

  return (
    <EmailLayout preview={`Invoice ${invoiceNumber} — ${fmt(total)}`}>
      <Text style={{ fontSize: "20px", fontWeight: "600" }}>
        Invoice {invoiceNumber}
      </Text>
      {/* Table header */}
      <Section>
        <Row>
          <Column style={{ width: "60%" }}>
            <Text style={tableHeader}>Item</Text>
          </Column>
          <Column style={{ width: "15%", textAlign: "center" }}>
            <Text style={tableHeader}>Qty</Text>
          </Column>
          <Column style={{ width: "25%", textAlign: "right" }}>
            <Text style={tableHeader}>Price</Text>
          </Column>
        </Row>
        <Hr style={{ borderColor: "#e5e7eb" }} />
        {items.map((item, i) => (
          <Row key={i}>
            <Column style={{ width: "60%" }}>
              <Text style={tableCell}>{item.name}</Text>
            </Column>
            <Column style={{ width: "15%", textAlign: "center" }}>
              <Text style={tableCell}>{item.qty}</Text>
            </Column>
            <Column style={{ width: "25%", textAlign: "right" }}>
              <Text style={tableCell}>{fmt(item.price * item.qty)}</Text>
            </Column>
          </Row>
        ))}
        <Hr style={{ borderColor: "#e5e7eb" }} />
        <Row>
          <Column style={{ width: "75%" }}>
            <Text style={{ ...tableCell, fontWeight: "700" }}>Total</Text>
          </Column>
          <Column style={{ width: "25%", textAlign: "right" }}>
            <Text style={{ ...tableCell, fontWeight: "700" }}>{fmt(total)}</Text>
          </Column>
        </Row>
      </Section>
    </EmailLayout>
  );
}

const tableHeader = { fontSize: "12px", color: "#6b7280", fontWeight: "600" as const, textTransform: "uppercase" as const, margin: "0" };
const tableCell = { fontSize: "14px", color: "#1a1a1a", margin: "4px 0" };
```

## Testing Email Rendering

### Preview Server

```bash
npx react-email dev --dir emails --port 3001
```

### Render to HTML (for testing or non-React Email senders)

```typescript
import { render } from "@react-email/render";
import WelcomeEmail from "@/emails/welcome";

// Render to HTML string
const html = await render(WelcomeEmail({ name: "Alice", actionUrl: "https://example.com" }));

// Render to plain text (auto-generated from components)
const text = await render(
  WelcomeEmail({ name: "Alice", actionUrl: "https://example.com" }),
  { plainText: true }
);
```

### Unit Testing Templates

```typescript
// __tests__/emails/welcome.test.tsx
import { render } from "@react-email/render";
import WelcomeEmail from "@/emails/welcome";

describe("WelcomeEmail", () => {
  it("renders with user name", async () => {
    const html = await render(
      WelcomeEmail({ name: "Alice", actionUrl: "https://example.com/start" })
    );
    expect(html).toContain("Alice");
    expect(html).toContain("https://example.com/start");
    expect(html).toContain("Get Started");
  });

  it("generates plain text version", async () => {
    const text = await render(
      WelcomeEmail({ name: "Bob", actionUrl: "https://example.com" }),
      { plainText: true }
    );
    expect(text).toContain("Bob");
    expect(text).toContain("https://example.com");
  });
});
```

### Email Client Testing Services

For cross-client rendering verification, use:
- **Litmus** — Automated screenshots across 90+ clients
- **Email on Acid** — Rendering + accessibility checks
- **Mailtrap** — Staging inbox for dev/test environments

Configure Mailtrap for development:

```typescript
// lib/resend.ts
import { Resend } from "resend";

const isDev = process.env.NODE_ENV === "development";

export const resend = isDev
  ? new Resend(process.env.MAILTRAP_API_KEY) // Mailtrap SMTP or API
  : new Resend(process.env.RESEND_API_KEY);
```

## Email CSS Compatibility Quick Reference

| CSS Property | Gmail | Apple Mail | Outlook | Yahoo |
|-------------|-------|------------|---------|-------|
| `margin` | Yes | Yes | Partial | Yes |
| `padding` | Yes | Yes | Yes | Yes |
| `background-color` | Yes | Yes | Yes | Yes |
| `border-radius` | Yes | Yes | No | Yes |
| `flexbox` | No | Yes | No | No |
| `grid` | No | Yes | No | No |
| `max-width` | Yes | Yes | No | Yes |
| `@media queries` | No | Yes | No | No |

**Safe approach:** Use table-based layout (`Row`/`Column`), inline styles, and avoid modern CSS layout. React Email handles this automatically.
