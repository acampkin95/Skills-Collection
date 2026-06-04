# 3rd Party Library Matrix & Stack Recommendations

Technical stack recommendations matched to four dashboard verticals: E-commerce, IT/DevOps, Portfolio/Creative, and Service/SaaS. Each recommendation is production-tested for 2026 with Next.js 15+, Tailwind v4, and React 19.

## Table of Contents
1. [Foundation Stack](#foundation)
2. [Component Library Matrix](#component-matrix)
3. [Charts & Data Visualisation Matrix](#charts)
4. [Data Grid & Table Matrix](#data-grid)
5. [Vertical Stack Recommendations](#verticals)
6. [Additional Specialist Libraries](#specialist)
7. [Bundle Impact Guide](#bundle)

---

## Foundation Stack (All Verticals)

These are non-negotiable for any POURFORM-style brand build:

| Layer | Library | Version | Role |
|-------|---------|---------|------|
| Framework | Next.js | 15+ (App Router) | SSR, RSC, routing |
| Styling | Tailwind CSS | v4 | Utility-first, @theme config |
| Primitives | Radix UI | Latest | Accessible headless components |
| Components | ShadCN/UI | Latest | Copy-paste Tailwind + Radix |
| Icons | react-icons/ri | 5.x | Remix Icon via tree-shakeable imports |
| Animation | Framer Motion | 12.x | Component-level React animation |
| State | Zustand | 5.x | Lightweight global state |
| Forms | React Hook Form + Zod | Latest | Validation + type-safe schemas |
| Fonts | @fontsource-variable | Latest | Self-hosted variable fonts |

---

## Component Library Matrix

### Comparison: Which Component Library for Which Use Case?

| Library | Styling | A11y | Components | Best For | Bundle | Licence |
|---------|---------|------|------------|----------|--------|---------|
| **ShadCN/UI** | Tailwind + Radix | AAA | 50+ | Custom-branded products | 0kb (copy-paste) | MIT |
| **Tremor** | Tailwind + Radix | AA | 35+ | Analytics dashboards | ~45kb | Apache 2.0 |
| **Mantine** | CSS Modules | AA | 100+ | Full-stack apps, rapid dev | ~80kb | MIT |
| **MUI** | Emotion/CSS | AA | 100+ | Enterprise admin panels | 100-200kb | MIT |
| **Ant Design** | CSS-in-JS | AA | 60+ | Chinese market, data-heavy | 150kb+ | MIT |
| **DaisyUI** | Tailwind plugin | A | 50+ | Prototyping, multi-framework | ~3kb CSS | MIT |
| **HeroUI** | Tailwind + React Aria | AAA | 40+ | Performance-critical apps | ~30kb | MIT |
| **Blueprint** | CSS | AA | 40+ | Desktop data tools | ~100kb | Apache 2.0 |
| **Headless UI** | Tailwind (unstyled) | AA | 10 | Custom design systems | ~5kb | MIT |
| **Flowbite** | Tailwind | AA | 50+ | Marketing + app hybrid | ~20kb | MIT |

### Recommendation

**Default choice**: ShadCN/UI (already in the POURFORM stack).
**Add Tremor** when building dashboards with charts/metrics.
**Add MUI Data Grid** when you need enterprise-grade data tables.
**Consider Mantine** as an alternative for rapid full-stack development.

---

## Charts & Data Visualisation Matrix

| Library | Base | React API | Chart Types | Large Data | Tailwind Compat | Best For |
|---------|------|-----------|-------------|------------|-----------------|----------|
| **Recharts** | D3 (SVG) | Declarative JSX | 12+ standard | Medium (<10k pts) | ✓ via CSS | General dashboards, SaaS |
| **Tremor Charts** | Recharts | High-level JSX | 8 core types | Medium | ✓ native | KPI dashboards, analytics |
| **ShadCN Charts** | Recharts | Copy-paste | 8 core types | Medium | ✓ native | Branded dashboards |
| **Apache ECharts** | Canvas/WebGL | echarts-for-react | 30+ types | Very large (1M+) | Partial | IoT, telemetry, financial |
| **Chart.js** | Canvas | react-chartjs-2 | 8 types | Medium-large | Partial | Simple charts, lightweight |
| **Visx** | D3 (SVG) | Low-level primitives | Unlimited | Medium | ✓ | Custom visualisations |
| **Nivo** | D3 (SVG/Canvas) | Declarative | 20+ types | Medium | Partial | Artistic/editorial charts |
| **TanStack Charts** | Custom (SVG) | Headless core | Standard | Large | ✓ | TanStack ecosystem apps |
| **ApexCharts** | SVG | react-apexcharts | 15+ types | Medium | Partial | Interactive dashboards |

### Recommendation by Vertical

| Vertical | Primary | Secondary | Why |
|----------|---------|-----------|-----|
| E-commerce | Recharts (via ShadCN) | ApexCharts | Revenue trends, conversion funnels |
| IT/DevOps | ECharts | Recharts | Time-series telemetry, large datasets |
| Portfolio | Nivo | Visx | Artistic, editorial-quality visuals |
| Service/SaaS | Tremor | Recharts | KPIs, metrics, analytics dashboards |

---

## Data Grid & Table Matrix

| Library | Headless | Virtual Scroll | Sort/Filter | Edit | Export | Bundle | Licence |
|---------|----------|----------------|-------------|------|--------|--------|---------|
| **TanStack Table** | ✓ | ✓ (via virtualiser) | ✓ | Custom | Custom | ~15kb | MIT |
| **AG Grid** | ✗ | ✓ native | ✓ | ✓ | ✓ | 200kb+ | MIT (Community) |
| **MUI X Data Grid** | ✗ | ✓ | ✓ | ✓ | ✓ | 100kb+ | MIT (Community) |
| **React Data Grid** | ✗ | ✓ native | ✓ | ✓ | ✓ | ~90kb | MIT |
| **Mantine DataTable** | ✗ | ✓ | ✓ | ✓ | ✓ | ~40kb | MIT |

### Recommendation

**Default**: TanStack Table v8 (headless, pairs with ShadCN Table component).
**Enterprise data grids**: AG Grid Community (if >10k rows, inline editing, CSV/Excel export needed).
**Mid-range**: Mantine DataTable (good balance of features and bundle size).

---

## Vertical Stack Recommendations

### E-Commerce Dashboard

**Use case**: Product management, order tracking, revenue analytics, inventory, customer insights.

| Layer | Library | Rationale |
|-------|---------|-----------|
| Components | ShadCN/UI | Brand-customisable, lightweight |
| Charts | Recharts (via ShadCN Charts) | Revenue trends, conversion funnels, product performance |
| Data Table | TanStack Table v8 | Order lists, product catalogue, customer tables |
| Forms | React Hook Form + Zod | Product creation, order management forms |
| State | Zustand | Cart state, filter state, dashboard preferences |
| Payments UI | Stripe Elements / Stripe.js | PCI-compliant payment forms |
| Image handling | next/image + Cloudinary SDK | Product image optimisation |
| Search | Algolia InstantSearch | Product search with faceted filtering |
| Date handling | date-fns | Order dates, reporting periods |
| Additional | @tanstack/react-query | Server state, caching API responses |

**Key components**: Product cards with image gallery, order timeline (horizontal pipeline), revenue sparklines, inventory status badges, customer segment donut charts.

### IT / DevOps Dashboard

**Use case**: Infrastructure monitoring, log analysis, deployment tracking, server metrics, incident management.

| Layer | Library | Rationale |
|-------|---------|-----------|
| Components | ShadCN/UI + Tremor | Metrics-focused components + standard UI |
| Charts | ECharts (echarts-for-react) | Time-series, streaming data, large datasets |
| Data Table | AG Grid Community | Log tables with 100k+ rows, real-time updates |
| Terminal | xterm.js / @xterm/xterm | Embedded terminal for log tailing |
| Code display | @uiw/react-codemirror | Config file viewing, YAML/JSON editing |
| Metrics | Tremor KPI cards | Uptime, latency, error rate, throughput |
| Status | react-hot-toast | Alert notifications, incident toasts |
| Real-time | socket.io-client / SSE | Live metric streaming |
| Maps | react-simple-maps | Server location visualisation |
| Date handling | dayjs | Lightweight, timezone-aware for multi-region ops |

**Key components**: Server health grid (asymmetric), latency sparklines, deployment timeline, log viewer with filter bar, incident severity badges, uptime tracker bars.

### Portfolio / Creative Dashboard

**Use case**: Project showcase, case study management, client inquiries, content calendar, analytics.

| Layer | Library | Rationale |
|-------|---------|-----------|
| Components | ShadCN/UI | Clean, minimal, brand-forward |
| Charts | Nivo | Artistic, editorial-quality data vis |
| Content | @portabletext/react or MDX | Rich text rendering for case studies |
| Media | react-photo-album / lightbox2 | Image galleries, project showcases |
| Animation | Framer Motion | Page transitions, scroll-triggered reveals |
| Video | react-player | Embedded project videos, showreels |
| 3D | @react-three/fiber + drei | Interactive 3D model viewers |
| Drag & drop | @dnd-kit/core | Portfolio reordering, content curation |
| Calendar | react-big-calendar | Content calendar, deadline tracking |
| CMS | Sanity.io client | Headless content management |

**Key components**: Project cards with hover-reveal metadata, full-bleed image heroes, case study timelines, inquiry form with status pipeline, client logo ticker, filterable project grid with category tags.

### Service / SaaS Dashboard

**Use case**: User management, subscription analytics, feature usage, support tickets, billing.

| Layer | Library | Rationale |
|-------|---------|-----------|
| Components | ShadCN/UI + Tremor | KPIs + standard UI |
| Charts | Tremor / Recharts | MRR trends, churn analysis, usage metrics |
| Data Table | TanStack Table v8 | User lists, subscription management |
| Auth UI | @clerk/nextjs or next-auth | User management, role-based access |
| Billing | Stripe Customer Portal | Subscription management |
| Notifications | Sonner | Toast notifications for SaaS events |
| Command | cmdk | Command palette for power users |
| Feature flags | @vercel/flags | Feature toggle management |
| Feedback | @sentry/nextjs | Error tracking, session replay |
| Email | @react-email/components | Transactional email templates |

**Key components**: MRR/ARR trend cards, subscription tier breakdown donut, usage heatmap, support ticket pipeline (horizontal stages), user activity feed, billing history table.

---

## Additional Specialist Libraries

### Animation & Motion
| Library | Use Case | Bundle |
|---------|----------|--------|
| **Framer Motion** | Component animations, gestures, layout | ~30kb |
| **GSAP** | Complex timeline animations, scroll-triggered | ~25kb |
| **Lottie (lottie-react)** | After Effects animations in web | ~20kb |
| **Motion One** | Lightweight alternative to Framer | ~5kb |

### Rich Text & Content
| Library | Use Case | Bundle |
|---------|----------|--------|
| **TipTap** | WYSIWYG editor, collaborative editing | ~40kb |
| **Plate** | Headless rich text (built on Slate) | ~35kb |
| **MDX** | Markdown + React components | Build-time |

### File Handling
| Library | Use Case | Bundle |
|---------|----------|--------|
| **react-dropzone** | File upload with drag & drop | ~7kb |
| **UploadThing** | File upload with S3 integration | ~10kb |
| **SheetJS** | Excel/CSV parsing and generation | ~30kb |

### Date & Time
| Library | Use Case | Bundle |
|---------|----------|--------|
| **date-fns** | Modular date manipulation | Tree-shakeable |
| **dayjs** | Lightweight Moment.js alternative | ~2kb |
| **Temporal API** | Native browser (Chrome 136+) | 0kb |

### Maps & Geo
| Library | Use Case | Bundle |
|---------|----------|--------|
| **Mapbox GL JS** | Interactive maps, custom styling | ~200kb |
| **react-simple-maps** | SVG-based thematic maps | ~15kb |
| **Leaflet (react-leaflet)** | OpenStreetMap-based maps | ~40kb |

---

## Bundle Impact Guide

### Budget by Vertical

| Vertical | Target JS Bundle | Recommended Strategy |
|----------|-----------------|---------------------|
| E-commerce | <150kb gzipped | Aggressive code-splitting, lazy charts |
| IT/DevOps | <250kb gzipped | Acceptable for desktop-heavy usage |
| Portfolio | <100kb gzipped | Minimal JS, CSS-heavy, image-optimised |
| Service/SaaS | <200kb gzipped | Lazy-load admin features, SSR public pages |

### Code Splitting Patterns

```typescript
// Lazy-load chart components (they're heavy)
const AreaChart = dynamic(() =>
  import('@/components/charts/AreaChart'), { ssr: false }
);

// Lazy-load data grids
const DataGrid = dynamic(() =>
  import('@/components/tables/DataGrid'), { ssr: false }
);

// Lazy-load rich text editor
const Editor = dynamic(() =>
  import('@/components/editor/TipTapEditor'), { ssr: false }
);
```

### Tree-Shaking Checklist

1. Import individual components: `import { Button } from '@/components/ui/button'`
2. Import individual icons: `import { RiHomeLine } from 'react-icons/ri'`
3. Import individual date functions: `import { format } from 'date-fns'`
4. Never: `import * as Icons from 'react-icons/ri'`
5. Use `next/dynamic` for anything >20kb that's below the fold

---

## Stack Selection Decision Tree

```
What are you building?
│
├─ E-commerce → ShadCN + Recharts + TanStack Table + Stripe
│  └─ Need product search? → Add Algolia
│  └─ Need image CDN? → Add Cloudinary
│
├─ IT/DevOps → ShadCN + Tremor + ECharts + AG Grid
│  └─ Need terminal? → Add xterm.js
│  └─ Need code editor? → Add CodeMirror
│
├─ Portfolio → ShadCN + Nivo + Framer Motion + Sanity
│  └─ Need 3D? → Add React Three Fiber
│  └─ Need galleries? → Add react-photo-album
│
└─ Service/SaaS → ShadCN + Tremor + TanStack Table + Clerk
   └─ Need command palette? → Add cmdk
   └─ Need email templates? → Add react-email
```
