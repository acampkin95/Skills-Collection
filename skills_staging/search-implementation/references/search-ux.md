# Search UX Patterns Reference

## Autocomplete / Instant Search

### Debounced Search Input (React)

```tsx
import { useState, useEffect, useRef, useCallback } from 'react';

interface SearchResult {
  id: string;
  title: string;
  _formatted?: { title: string; description: string };
}

function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `/api/search?q=${encodeURIComponent(query)}&limit=8`
        );
        const data = await res.json();
        setResults(data.hits);
        setIsOpen(true);
      } catch {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 250); // 250ms debounce

    return () => clearTimeout(timer);
  }, [query]);

  // Reset active index when results change
  useEffect(() => {
    setActiveIndex(-1);
  }, [results]);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isOpen || results.length === 0) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setActiveIndex((prev) =>
            prev < results.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setActiveIndex((prev) =>
            prev > 0 ? prev - 1 : results.length - 1
          );
          break;
        case 'Enter':
          e.preventDefault();
          if (activeIndex >= 0) {
            navigateToResult(results[activeIndex]);
          } else {
            navigateToSearch(query);
          }
          break;
        case 'Escape':
          setIsOpen(false);
          inputRef.current?.blur();
          break;
      }
    },
    [isOpen, results, activeIndex, query]
  );

  // Scroll active item into view
  useEffect(() => {
    if (activeIndex >= 0 && listRef.current) {
      const item = listRef.current.children[activeIndex] as HTMLElement;
      item?.scrollIntoView({ block: 'nearest' });
    }
  }, [activeIndex]);

  return (
    <div className="relative w-full max-w-xl">
      <div className="relative">
        <input
          ref={inputRef}
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder="Search products..."
          role="combobox"
          aria-expanded={isOpen}
          aria-controls="search-results"
          aria-activedescendant={
            activeIndex >= 0 ? `result-${activeIndex}` : undefined
          }
          className="w-full rounded-lg border px-4 py-2.5 pl-10 outline-none
                     focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
        />
        {/* Search icon */}
        <svg className="absolute left-3 top-3 h-5 w-5 text-gray-400" /* ... */ />
        {/* Loading spinner */}
        {isLoading && (
          <div className="absolute right-3 top-3 h-5 w-5 animate-spin
                          rounded-full border-2 border-gray-300 border-t-blue-500" />
        )}
      </div>

      {/* Results dropdown */}
      {isOpen && (
        <ul
          ref={listRef}
          id="search-results"
          role="listbox"
          className="absolute z-50 mt-1 w-full rounded-lg border bg-white
                     shadow-lg max-h-96 overflow-y-auto"
        >
          {results.length === 0 ? (
            <li className="px-4 py-3 text-sm text-gray-500">
              No results for &quot;{query}&quot;
            </li>
          ) : (
            results.map((result, index) => (
              <li
                key={result.id}
                id={`result-${index}`}
                role="option"
                aria-selected={index === activeIndex}
                onClick={() => navigateToResult(result)}
                className={`cursor-pointer px-4 py-3 text-sm
                  ${index === activeIndex ? 'bg-blue-50' : 'hover:bg-gray-50'}`}
              >
                {/* Use _formatted for highlighted text */}
                <span
                  dangerouslySetInnerHTML={{
                    __html: result._formatted?.title ?? result.title,
                  }}
                />
              </li>
            ))
          )}
        </ul>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
```

## Highlighting Search Results

### HTML Highlighting (from search engine)

```tsx
// Meilisearch returns _formatted with highlighted matches
// Configure highlight tags in the search query:
// highlightPreTag: '<mark>', highlightPostTag: '</mark>'

function SearchResult({ hit }: { hit: SearchHit }) {
  return (
    <article className="border-b py-4">
      <h3
        className="text-lg font-semibold [&_mark]:bg-yellow-200 [&_mark]:font-bold"
        dangerouslySetInnerHTML={{ __html: hit._formatted.title }}
      />
      <p
        className="mt-1 text-sm text-gray-600 [&_mark]:bg-yellow-100"
        dangerouslySetInnerHTML={{ __html: hit._formatted.description }}
      />
      <span className="text-sm font-medium text-green-700">${hit.price}</span>
    </article>
  );
}
```

### Client-Side Highlighting (no engine support)

```typescript
function highlightMatches(text: string, query: string): string {
  if (!query.trim()) return text;

  // Escape regex special characters
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const words = escaped.split(/\s+/).filter(Boolean);
  const pattern = new RegExp(`(${words.join('|')})`, 'gi');

  return text.replace(pattern, '<mark>$1</mark>');
}

// Usage
const highlighted = highlightMatches(
  'Wireless Noise-Cancelling Headphones',
  'wireless headphones'
);
// "**<mark>Wireless</mark>** Noise-Cancelling **<mark>Headphones</mark>**"
```

## "Did You Mean" Suggestions

### Using Meilisearch (Built-in)

Meilisearch handles typos automatically — no "did you mean" needed. It returns corrected results directly.

### Custom Implementation (PostgreSQL)

```sql
-- Use pg_trgm to suggest corrections
CREATE OR REPLACE FUNCTION suggest_correction(query_text TEXT)
RETURNS TEXT AS $$
DECLARE
  suggestion TEXT;
BEGIN
  -- Find the most similar known term
  SELECT title INTO suggestion
  FROM products
  WHERE similarity(title, query_text) > 0.15
  ORDER BY similarity(title, query_text) DESC
  LIMIT 1;

  RETURN suggestion;
END;
$$ LANGUAGE plpgsql;
```

### Client-Side Suggestion UI

```tsx
function SearchResults({ query, results, suggestion }: Props) {
  if (results.length === 0 && suggestion) {
    return (
      <div className="py-8 text-center">
        <p className="text-gray-500">
          No results for <strong>&quot;{query}&quot;</strong>
        </p>
        <p className="mt-2">
          Did you mean{' '}
          <button
            onClick={() => onSearch(suggestion)}
            className="text-blue-600 underline hover:text-blue-800"
          >
            {suggestion}
          </button>
          ?
        </p>
      </div>
    );
  }

  return <div>{/* render results */}</div>;
}
```

## Facet UI

### Checkbox Facets

```tsx
interface FacetGroup {
  name: string;
  values: Record<string, number>; // value → count
}

function FacetFilter({
  facet,
  selected,
  onToggle,
}: {
  facet: FacetGroup;
  selected: Set<string>;
  onToggle: (facetName: string, value: string) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showAll, setShowAll] = useState(false);

  const entries = Object.entries(facet.values)
    .sort(([, a], [, b]) => b - a); // Sort by count descending
  const visible = showAll ? entries : entries.slice(0, 5);

  return (
    <fieldset className="border-b py-4">
      <legend>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex w-full items-center justify-between text-sm font-semibold"
        >
          {facet.name}
          <span>{isExpanded ? '−' : '+'}</span>
        </button>
      </legend>

      {isExpanded && (
        <div className="mt-2 space-y-1">
          {visible.map(([value, count]) => (
            <label
              key={value}
              className="flex cursor-pointer items-center gap-2 rounded px-2 py-1
                         text-sm hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={selected.has(value)}
                onChange={() => onToggle(facet.name, value)}
                className="rounded border-gray-300"
              />
              <span className="flex-1">{value}</span>
              <span className="text-xs text-gray-400">({count})</span>
            </label>
          ))}
          {entries.length > 5 && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="mt-1 text-xs text-blue-600 hover:underline"
            >
              {showAll ? 'Show less' : `Show all ${entries.length}`}
            </button>
          )}
        </div>
      )}
    </fieldset>
  );
}
```

### Price Range Slider Facet

```tsx
function PriceRangeFilter({
  min,
  max,
  currentMin,
  currentMax,
  onChange,
}: {
  min: number;
  max: number;
  currentMin: number;
  currentMax: number;
  onChange: (min: number, max: number) => void;
}) {
  return (
    <div className="py-4">
      <h3 className="text-sm font-semibold">Price Range</h3>
      <div className="mt-3 flex items-center gap-3">
        <input
          type="number"
          value={currentMin}
          min={min}
          max={currentMax}
          onChange={(e) => onChange(+e.target.value, currentMax)}
          className="w-20 rounded border px-2 py-1 text-sm"
          aria-label="Minimum price"
        />
        <span className="text-gray-400">—</span>
        <input
          type="number"
          value={currentMax}
          min={currentMin}
          max={max}
          onChange={(e) => onChange(currentMin, +e.target.value)}
          className="w-20 rounded border px-2 py-1 text-sm"
          aria-label="Maximum price"
        />
      </div>
    </div>
  );
}
```

## Search Analytics

### Track Key Metrics

```typescript
interface SearchEvent {
  query: string;
  resultsCount: number;
  duration: number;
  timestamp: number;
  filters?: Record<string, string[]>;
  facetsUsed?: string[];
}

interface ClickEvent {
  query: string;
  resultId: string;
  position: number; // 0-indexed position in results
  timestamp: number;
}

// Track searches
async function trackSearch(event: SearchEvent) {
  await fetch('/api/analytics/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  });
}

// Track result clicks
async function trackClick(event: ClickEvent) {
  await fetch('/api/analytics/click', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  });
}

// Key metrics to compute:
// - Zero-result rate: searches with 0 results / total searches
// - Click-through rate (CTR): clicks / searches
// - Mean Reciprocal Rank (MRR): avg(1 / click_position)
// - Search exit rate: users who leave after searching
// - Top queries with no results → add synonyms or content
```

### Analytics Dashboard Query (SQL)

```sql
-- Top queries with zero results (add synonyms for these)
SELECT query, COUNT(*) AS searches
FROM search_events
WHERE results_count = 0
  AND created_at > now() - INTERVAL '7 days'
GROUP BY query
ORDER BY searches DESC
LIMIT 20;

-- Click-through rate by query
SELECT
  query,
  COUNT(DISTINCT se.id) AS searches,
  COUNT(DISTINCT ce.id) AS clicks,
  ROUND(COUNT(DISTINCT ce.id)::NUMERIC / NULLIF(COUNT(DISTINCT se.id), 0) * 100, 1) AS ctr
FROM search_events se
LEFT JOIN click_events ce ON se.query = ce.query
WHERE se.created_at > now() - INTERVAL '7 days'
GROUP BY query
HAVING COUNT(DISTINCT se.id) > 10
ORDER BY ctr ASC  -- Lowest CTR first = needs improvement
LIMIT 20;
```

## Empty States

```tsx
function SearchEmptyState({ query }: { query: string }) {
  return (
    <div className="flex flex-col items-center py-16 text-center">
      <svg className="h-16 w-16 text-gray-300" /* search icon */ />

      <h2 className="mt-4 text-lg font-semibold text-gray-700">
        No results for &quot;{query}&quot;
      </h2>

      <p className="mt-2 max-w-md text-sm text-gray-500">
        Try adjusting your search terms or removing filters to find what
        you&apos;re looking for.
      </p>

      <div className="mt-6 space-y-3">
        <h3 className="text-sm font-medium text-gray-600">Suggestions:</h3>
        <ul className="text-sm text-gray-500 space-y-1">
          <li>Check your spelling</li>
          <li>Use fewer or different keywords</li>
          <li>Remove applied filters</li>
        </ul>
      </div>

      {/* Popular searches */}
      <div className="mt-8">
        <h3 className="text-sm font-medium text-gray-600">Popular searches:</h3>
        <div className="mt-2 flex flex-wrap justify-center gap-2">
          {['headphones', 'laptop', 'camera', 'watch'].map((term) => (
            <button
              key={term}
              onClick={() => onSearch(term)}
              className="rounded-full bg-gray-100 px-3 py-1 text-sm
                         text-gray-700 hover:bg-gray-200"
            >
              {term}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## Initial Search State (No Query)

```tsx
function SearchInitialState() {
  return (
    <div className="py-8">
      {/* Recent searches */}
      <section>
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
          Recent searches
        </h3>
        <div className="mt-2 space-y-1">
          {recentSearches.map((term) => (
            <button
              key={term}
              onClick={() => onSearch(term)}
              className="flex items-center gap-2 rounded px-2 py-1.5 text-sm
                         text-gray-700 hover:bg-gray-50 w-full text-left"
            >
              <ClockIcon className="h-4 w-4 text-gray-400" />
              {term}
            </button>
          ))}
        </div>
      </section>

      {/* Trending / Popular */}
      <section className="mt-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
          Trending
        </h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {trendingTerms.map((term) => (
            <button
              key={term}
              onClick={() => onSearch(term)}
              className="rounded-full border px-3 py-1 text-sm hover:bg-gray-50"
            >
              {term}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
```

## Mobile Full-Screen Search

```tsx
function MobileSearchOverlay({ isOpen, onClose }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus input when overlay opens
  useEffect(() => {
    if (isOpen) {
      // Small delay to allow animation
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-white">
      {/* Header with input */}
      <div className="flex items-center gap-2 border-b px-4 py-3">
        <button
          onClick={onClose}
          className="p-1"
          aria-label="Close search"
        >
          <ArrowLeftIcon className="h-5 w-5" />
        </button>
        <input
          ref={inputRef}
          type="search"
          placeholder="Search..."
          className="flex-1 text-base outline-none"
          onChange={(e) => setQuery(e.target.value)}
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="p-1 text-gray-400"
            aria-label="Clear search"
          >
            <XIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Full-screen results */}
      <div className="overflow-y-auto" style={{ height: 'calc(100vh - 56px)' }}>
        {query ? <ResultsList /> : <SearchInitialState />}
      </div>
    </div>
  );
}
```

## URL State Synchronization

Preserve search state in the URL for sharing and browser back/forward:

```typescript
// Next.js App Router: sync search params with URL
'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { useCallback } from 'react';

function useSearchState() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const query = searchParams.get('q') ?? '';
  const page = Number(searchParams.get('page') ?? '1');
  const sort = searchParams.get('sort') ?? 'relevance';

  // Get active filters from URL
  const filters: Record<string, string[]> = {};
  searchParams.forEach((value, key) => {
    if (!['q', 'page', 'sort'].includes(key)) {
      filters[key] = value.split(',');
    }
  });

  const updateSearch = useCallback(
    (updates: Record<string, string | null>) => {
      const params = new URLSearchParams(searchParams.toString());

      Object.entries(updates).forEach(([key, value]) => {
        if (value === null) {
          params.delete(key);
        } else {
          params.set(key, value);
        }
      });

      // Reset page when query or filters change
      if ('q' in updates || Object.keys(updates).some((k) => !['page', 'sort'].includes(k))) {
        params.delete('page');
      }

      router.push(`${pathname}?${params.toString()}`, { scroll: false });
    },
    [router, pathname, searchParams]
  );

  return { query, page, sort, filters, updateSearch };
}

// Usage
function SearchPage() {
  const { query, page, sort, filters, updateSearch } = useSearchState();

  return (
    <>
      <SearchInput
        value={query}
        onChange={(q) => updateSearch({ q: q || null })}
      />
      <SortSelect
        value={sort}
        onChange={(s) => updateSearch({ sort: s })}
      />
      <FacetFilters
        filters={filters}
        onToggle={(name, value) => {
          const current = filters[name] ?? [];
          const next = current.includes(value)
            ? current.filter((v) => v !== value)
            : [...current, value];
          updateSearch({ [name]: next.length ? next.join(',') : null });
        }}
      />
      <Pagination
        page={page}
        onChange={(p) => updateSearch({ page: p > 1 ? String(p) : null })}
      />
    </>
  );
}
```

## Accessibility Checklist

- `role="combobox"` on search input
- `role="listbox"` on results dropdown
- `role="option"` on each result item
- `aria-expanded` reflects dropdown state
- `aria-activedescendant` points to focused result
- `aria-label` on search input and clear button
- Escape closes dropdown and clears focus
- Enter selects active result or submits search
- Arrow keys navigate results without mouse
- Focus trap within mobile overlay
- Live region announces result count: `aria-live="polite"`

```tsx
<div aria-live="polite" className="sr-only">
  {results ? `${results.estimatedTotalHits} results found` : ''}
</div>
```
