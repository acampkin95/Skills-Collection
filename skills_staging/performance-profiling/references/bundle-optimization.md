# Bundle Optimization

## webpack-bundle-analyzer

```bash
# Install
npm install -D webpack-bundle-analyzer

# Generate stats
npx webpack --profile --json > stats.json
npx webpack-bundle-analyzer stats.json
```

### Next.js Bundle Analyzer

```javascript
// next.config.js
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

module.exports = withBundleAnalyzer({
  // your next config
});
```

```bash
ANALYZE=true npm run build
```

## Tree Shaking

### Ensure Proper Imports

```typescript
// BAD — imports entire library
import _ from "lodash";
_.debounce(fn, 300);

// GOOD — imports only what's needed
import debounce from "lodash/debounce";
debounce(fn, 300);

// GOOD — named imports with tree-shakeable library
import { debounce } from "lodash-es";
```

### Mark Package as Side-Effect Free

```json
// package.json
{
  "sideEffects": false
}

// Or specify files with side effects
{
  "sideEffects": ["*.css", "./src/polyfills.ts"]
}
```

### Verify Tree Shaking

```typescript
// Check what's included in your bundle:
// 1. Build with source maps
// 2. Use source-map-explorer
npx source-map-explorer dist/main.*.js
```

## Code Splitting

### Route-Based Splitting (React)

```tsx
import { lazy, Suspense } from "react";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));
const Profile = lazy(() => import("./pages/Profile"));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Suspense>
  );
}
```

### Component-Level Splitting

```tsx
import { lazy, Suspense, useState } from "react";

// Only load when user opens the modal
const HeavyModal = lazy(() => import("./HeavyModal"));

function Page() {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <button onClick={() => setShowModal(true)}>Open Editor</button>
      {showModal && (
        <Suspense fallback={<div>Loading editor...</div>}>
          <HeavyModal onClose={() => setShowModal(false)} />
        </Suspense>
      )}
    </>
  );
}
```

### Dynamic Import with Prefetch

```tsx
// Prefetch on hover for perceived performance
function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const prefetch = () => {
    // Webpack magic comment for prefetch
    import(/* webpackPrefetch: true */ `./pages/${to}`);
  };

  return (
    <Link to={to} onMouseEnter={prefetch}>
      {children}
    </Link>
  );
}
```

## Lazy Loading

### Images

```html
<!-- Native lazy loading -->
<img src="photo.jpg" loading="lazy" width="400" height="300" alt="Photo" />
```

### Intersection Observer Pattern

```typescript
function useLazyLoad(ref: React.RefObject<HTMLElement>) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "200px" } // load 200px before visible
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return isVisible;
}
```

## Font Optimization

```css
/* Subset fonts to only needed characters */
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-var-latin.woff2") format("woff2");
  font-display: swap; /* or optional for no CLS */
  unicode-range: U+0000-00FF, U+0131, U+0152-0153; /* Latin only */
}
```

```tsx
// Next.js font optimization
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});
```

## Bundle Size Monitoring in CI

```yaml
# .github/workflows/bundle.yml
- name: Check bundle size
  uses: andresz1/size-limit-action@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

```json
// package.json
{
  "size-limit": [
    { "path": "dist/main.*.js", "limit": "150 KB" },
    { "path": "dist/vendor.*.js", "limit": "200 KB" },
    { "path": "dist/**/*.css", "limit": "30 KB" }
  ]
}
```

## Common Large Dependencies and Alternatives

| Package | Size | Alternative | Size |
|---------|------|-------------|------|
| `moment` | 72KB | `date-fns` | 6KB (tree-shaken) |
| `lodash` | 72KB | `lodash-es` (tree-shaken) | ~5KB typical |
| `axios` | 14KB | `fetch` (native) | 0KB |
| `uuid` | 4KB | `crypto.randomUUID()` | 0KB |
| `classnames` | 1KB | Template literals | 0KB |
